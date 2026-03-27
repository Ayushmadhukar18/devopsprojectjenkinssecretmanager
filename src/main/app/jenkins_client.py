import os
import requests
from requests.auth import HTTPBasicAuth

class JenkinsClient:
    def __init__(self):
        self.base_url = os.environ.get("JENKINS_URL", "http://localhost:8080")
        self.user = os.environ.get("JENKINS_USER", "admin")
        self.token = os.environ.get("JENKINS_TOKEN", "")
        self.store = "system"
        self.domain = "_"

    @property
    def _auth(self):
        return HTTPBasicAuth(self.user, self.token)

    @property
    def _cred_url(self):
        return f"{self.base_url}/credentials/store/{self.store}/domain/{self.domain}"

    def _get_crumb(self):
        try:
            r = requests.get(
                f"{self.base_url}/crumbIssuer/api/json",
                auth=self._auth, timeout=5
            )
            if r.status_code == 200:
                data = r.json()
                return {data["crumbRequestField"]: data["crumb"]}
        except Exception as e:
            print(f"[Jenkins] crumb failed: {e}")
        return {}

    def is_connected(self) -> bool:
        try:
            r = requests.get(f"{self.base_url}/api/json", auth=self._auth, timeout=3)
            return r.status_code == 200
        except Exception:
            return False

    def push_credential(self, name: str, value: str, description: str = "") -> bool:
        import json as _json
        try:
            crumb_data = self._get_crumb()

            # Check if credential already exists
            check_url = f"{self._cred_url}/credential/{name}/config.xml"
            check = requests.get(check_url, auth=self._auth, timeout=5)
            print(f"[Jenkins] CHECK {name}: status={check.status_code}")

            if check.status_code == 200:
                # --- UPDATE existing credential via XML POST ---
                xml_body = self._to_xml(name, value, description)
                headers = {"Content-Type": "application/xml"}
                headers.update(crumb_data)
                r = requests.post(check_url, data=xml_body,
                                  headers=headers, auth=self._auth, timeout=5)
                print(f"[Jenkins] UPDATE {name}: status={r.status_code}")
                return r.status_code in (200, 201, 204)
            else:
                # --- CREATE new credential via form-encoded JSON ---
                payload = {
                    "": "0",
                    "credentials": {
                        "scope": "GLOBAL",
                        "id": name,
                        "description": description,
                        "$class": "org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl",
                        "secret": value,
                    }
                }
                form_body = "json=" + requests.utils.quote(_json.dumps(payload))
                headers = {"Content-Type": "application/x-www-form-urlencoded"}
                headers.update(crumb_data)
                create_url = f"{self._cred_url}/createCredentials"
                r = requests.post(create_url, data=form_body,
                                  headers=headers, auth=self._auth, timeout=5)
                print(f"[Jenkins] CREATE {name}: status={r.status_code} body={r.text[:300]}")
                return r.status_code in (200, 201, 204, 302)

        except Exception as e:
            print(f"[Jenkins] push_credential failed: {e}")
            return False

    def delete_credential(self, name: str) -> bool:
        try:
            headers = self._get_crumb()
            r = requests.delete(f"{self._cred_url}/credential/{name}",
                                headers=headers, auth=self._auth, timeout=5)
            print(f"[Jenkins] DELETE {name}: status={r.status_code}")
            return r.status_code in (200, 204)
        except Exception as e:
            print(f"[Jenkins] delete_credential failed: {e}")
            return False

    def list_credentials(self) -> list:
        try:
            r = requests.get(f"{self._cred_url}/api/json?depth=1",
                             auth=self._auth, timeout=5)
            if r.status_code == 200:
                return r.json().get("credentials", [])
        except Exception as e:
            print(f"[Jenkins] list_credentials failed: {e}")
        return []

    @staticmethod
    def _to_xml(name: str, value: str, description: str) -> str:
        return f"""<?xml version='1.1' encoding='UTF-8'?>
<org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl plugin="plain-credentials">
  <scope>GLOBAL</scope>
  <id>{name}</id>
  <description>{description}</description>
  <secret>{value}</secret>
</org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl>"""