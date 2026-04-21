import requests


class DHIS2Error(Exception):
    def __init__(self, message: str, status_code: int = 0, body: str = ""):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class AuthError(DHIS2Error):
    pass


class ConnectionError(DHIS2Error):
    pass


class DHIS2Client:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.headers.update({"Accept": "application/json", "Content-Type": "application/json"})

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _raise_for(self, resp: requests.Response) -> None:
        if resp.status_code == 401:
            raise AuthError("Invalid credentials (401)", 401, resp.text)
        if resp.status_code == 404:
            raise DHIS2Error(f"Not found: {resp.url}", 404, resp.text)
        if not resp.ok:
            raise DHIS2Error(f"HTTP {resp.status_code}: {resp.text[:300]}", resp.status_code, resp.text)

    def get(self, path: str, params: dict = None) -> dict:
        try:
            resp = self.session.get(self._url(path), params=params, timeout=30)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Cannot reach {self.base_url} — check the URL and your network. ({e})")
        self._raise_for(resp)
        return resp.json()

    def post(self, path: str, payload: dict, params: dict = None) -> dict:
        try:
            resp = self.session.post(self._url(path), json=payload, params=params, timeout=120)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Cannot reach {self.base_url} ({e})")
        self._raise_for(resp)
        return resp.json()

    def put(self, path: str, payload: dict) -> dict:
        try:
            resp = self.session.put(self._url(path), json=payload, timeout=60)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Cannot reach {self.base_url} ({e})")
        self._raise_for(resp)
        try:
            return resp.json()
        except Exception:
            return {}

    def delete(self, path: str) -> None:
        try:
            resp = self.session.delete(self._url(path), timeout=30)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Cannot reach {self.base_url} ({e})")
        if resp.status_code == 404:
            return  # already gone — treat as success
        self._raise_for(resp)

    def test_connection(self) -> tuple[bool, str]:
        try:
            data = self.get("/api/system/info")
            version = data.get("version", "unknown")
            context = data.get("contextPath", self.base_url)
            return True, f"DHIS2 {version} ({context})"
        except AuthError:
            return False, "Invalid credentials"
        except ConnectionError as e:
            return False, str(e)
        except Exception as e:
            return False, str(e)

    def get_org_unit_by_name(self, name: str) -> dict | None:
        data = self.get(
            "/api/organisationUnits",
            params={"filter": f"name:eq:{name}", "fields": "id,name,level", "paging": "false"},
        )
        units = data.get("organisationUnits", [])
        return units[0] if units else None

    def post_org_unit(self, payload: dict) -> str:
        resp = self.post("/api/organisationUnits", payload)
        uid = (
            resp.get("response", {}).get("uid")
            or resp.get("response", {}).get("lastImported")
            or resp.get("uid")
        )
        if not uid:
            raise DHIS2Error(f"Could not determine UID from org unit creation response: {resp}")
        return uid

    def import_metadata(self, bundle: dict) -> dict:
        return self.post(
            "/api/metadata",
            bundle,
            params={"importStrategy": "CREATE_AND_UPDATE", "atomicMode": "NONE"},
        )

    def assign_org_unit_to_dataset(self, dataset_uid: str, ou_uid: str) -> None:
        path = f"/api/dataSets/{dataset_uid}/organisationUnits/{ou_uid}"
        try:
            resp = self.session.post(self._url(path), timeout=30)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Cannot reach {self.base_url} ({e})")
        # 200 or 204 both mean success; some versions return 409 if already assigned
        if resp.status_code not in (200, 204, 409):
            self._raise_for(resp)

    def post_data_values(self, payload: dict) -> dict:
        return self.post("/api/dataValueSets", payload)

    def delete_data_values(self, dataset_uid: str, ou_uid: str, period: str) -> None:
        try:
            resp = self.session.delete(
                self._url("/api/dataValueSets"),
                params={"dataSet": dataset_uid, "orgUnit": ou_uid, "period": period},
                timeout=60,
            )
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Cannot reach {self.base_url} ({e})")
        if resp.status_code not in (200, 204, 404):
            self._raise_for(resp)
