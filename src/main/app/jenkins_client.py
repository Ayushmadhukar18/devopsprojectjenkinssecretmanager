import os
import json
import requests
from requests.auth import HTTPBasicAuth

class JenkinsClient:
    """Talks to Jenkins Credentials API to sync secrets."""

    def __init__(self):
        self.base_url = os.environ.get("JENKINS_URL", "http://localhost:8080")
        self.user = os.environ.get("JENKINS_USER", "admin")
        self.token = os.environ.get("JENKINS_TOKEN", "")
        self.store = "system::system::jenkins"
        self.domain = "_"

    @property
    def _auth(self):
        return HTTPBasicAuth(self.user, self.token)

    @property
    def _cred_url(self):
        return (f"{self.base_url}/credentials/store/{self.store}"
                f"/domain/{self.domain}/credential")

    def is_connected(self) -> bool:
        try:
            r = requests.get(f"{self.base_url}/api/json", auth=self._auth, timeout=3)
            return r.status_code == 200
        except Exception:
            return False

    def push_credential(self, name: str, value: str, description: str = "") -> bool:
        """Create or update a Jenkins secret-text credential."""
        payload = {
            "": "com.cloudbees.plugins.credentials.impl.StringCredentialsImpl",
            "credentials": {
                "scope": "GLOBAL",
                "id": name,
                "description": description,
                "secret": value,
                "$class": "com.cloudbees.plugins.credentials.impl.StringCredentialsImpl"
            }
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        try:
            # Try update first
            update_url = f"{self._cred_url}/{name}/config.xml"
            xml_body = self._to_xml(name, value, description)
            r = requests.post(update_url, data=xml_body,
                              headers={"Content-Type": "application/xml"},
                              auth=self._auth, timeout=5)
            if r.status_code == 404:
                # Create new
                r = requests.post(
                    f"{self._cred_url}/createItem",
                    data=f"json={json.dumps(payload)}",
                    headers=headers,
                    auth=self._auth, timeout=5
                )
            return r.status_code in (200, 201)
        except Exception as e:
            print(f"[Jenkins] push_credential failed: {e}")
            return False

    def delete_credential(self, name: str) -> bool:
        try:
            r = requests.delete(f"{self._cred_url}/{name}",
                                auth=self._auth, timeout=5)
            return r.status_code in (200, 204)
        except Exception as e:
            print(f"[Jenkins] delete_credential failed: {e}")
            return False

    def list_credentials(self) -> list:
        try:
            r = requests.get(f"{self.base_url}/credentials/store/{self.store}"
                             f"/domain/{self.domain}/api/json?depth=1",
                             auth=self._auth, timeout=5)
            if r.status_code == 200:
                return r.json().get("credentials", [])
        except Exception as e:
            print(f"[Jenkins] list_credentials failed: {e}")
        return []

    @staticmethod
    def _to_xml(name: str, value: str, description: str) -> str:
        return f"""<?xml version='1.1' encoding='UTF-8'?>
<org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl>
  <scope>GLOBAL</scope>
  <id>{name}</id>
  <description>{description}</description>
  <secret>{value}</secret>
</org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl>"""
