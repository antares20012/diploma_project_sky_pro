import requests
import base64
from faker import Faker


fake = Faker()
file_name = fake.word()



class GitPageAPI:
    def __init__(self, token: str, login: str, url: str = "https://api.github.com"):
        self.url = url.rstrip('/')
        self.token = token
        self.login = login


    @property
    def headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

    def create_repo(self, repo_name: str):
        url = f"{self.url}/user/repos"
        response = requests.post(url, headers=self.headers, json={"name": repo_name})

        if response.status_code != 201:
            print(f"\n[GitHub Error Payload]: {response.json()}")
            return response.status_code, None

        data = response.json()
        repo_data = {
            "id": data.get("id"),
            "full_name": data.get("full_name"),
            "html_url": data.get("html_url")
        }
        return response.status_code, repo_data

    def create_empty_file(self, login: str, repo_name: str, file_name: str):
        url = f"{self.url}/repos/{login}/{repo_name}/contents/{file_name}"
        empty_content_b64 = base64.b64encode(b"").decode("utf-8")

        commit =  {
            "message": "Create empty file.",
            "committer": {
                "name": "antares20012",
                "email": "4ingizxan20012@gmail.com"
                },
                "content": empty_content_b64
            }
        response = requests.put(url, headers=self.headers, json=commit)
        if response.status_code != 201:
            print(f"\n[GitHub Error Payload]: {response.json()}")
            return response.status_code, None
        # data = response.json()
        res= response.json()
        file_data = {
            "content": {
                "name": res.get("content", {}).get("name"),
                "sha": res.get("content", {}).get("sha"),
                "size": res.get("content", {}).get("size"),
                "html_url": res.get("content", {}).get("html_url")
            },
            "commit": {
                "sha": res.get("commit", {}).get("sha"),
                "committer": {
                    "name": res.get("commit", {}).get("committer", {}).get("name"),
                    "email": res.get("commit", {}).get("committer", {}).get("email"),
                },
                "message": res.get("commit", {}).get("message")
            }
        }
        return response.status_code, file_data

    def update_file(self, login: str, repo_name: str, file_name: str, to_base64, new_text: str, sha):
        url = f"{self.url}/repos/{login}/{repo_name}/contents/{file_name}"
        # new_text = "def greeting():\n    print('Hello, World!')\ngreeting()\n"
        encoded_string = to_base64(new_text)
        commit = {
            "message": f"Update file{file_name}",
            "committer": {
                "name": "antares20012",
                "email": "4ingizxan20012@gmail.com"
            },
            "content": encoded_string,
            "sha": sha
        }

        response = requests.put(url, headers=self.headers, json=commit)
        if response.status_code not in [200, 201]:
            print(f"\n[GitHub Error Payload]: {response.json()}")
            return response.status_code, None

        res = response.json()

        file_data = {
            "content": {
                "name": res.get("content", {}).get("name"),
                "sha": res.get("content", {}).get("sha"),
                "size": res.get("content", {}).get("size"),
                "html_url": res.get("content", {}).get("html_url")
            },
            "commit": {
                "sha": res.get("commit", {}).get("sha"),
                "committer": {
                    "name": res.get("commit", {}).get("committer", {}).get("name"),
                    "email": res.get("commit", {}).get("committer", {}).get("email"),
                },
                "message": res.get("commit", {}).get("message")
            }
        }
        return response.status_code, file_data

    def delete_repo(self, repo_name: str):
        url = f"{self.url}/repos/{self.login}/{repo_name}"
        response = requests.delete(url, headers=self.headers)
        return response.status_code
