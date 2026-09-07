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

    def read_file(self, login: str, repo_name: str, file_name: str):
        """
            Получает информацию о файле и декодирует его содержимое.
            :param login: Имя пользователя или организации
            :param repo_name: Название репозитория
            :param file_path: Путь к файлу в репозитории (например, 'folder/file.txt')
            :return: кортеж (status_code, response_json, decoded_text)
            """
        url = f"{self.url}/repos/{login}/{repo_name}/contents/{file_name}"
        response = requests.get(url, headers=self.headers)

        # Если файл не найден или произошла ошибка, возвращаем статус и пустые данные
        if response.status_code != 200:
            return response.status_code, None, None
        res = response.json()
        file_data = {
            "sha": res.get("sha"),
            "name": res.get("name"),
            "size": res.get("size")
        }

        # 2. Извлекаем и декодируем контент из base64 в обычную строку
        content_b64 = res.get("content", "")
        # GitHub может возвращать текст со знаками переноса строки, убираем их перед декодированием
        cleaned_b64 = content_b64.replace("\n", "").replace("\r", "")

        try:
            decoded_text = base64.b64decode(cleaned_b64).decode("utf-8")
        except Exception as e:
            print(f"Ошибка декодирования: {e}")
            decoded_text = ""

        return response.status_code, file_data, decoded_text

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

    def delete_last_modified_file(self, login: str, repo_name: str, file_name: str = None):
        """
        Находит последний измененный файл и удаляет его.
        Если передан file_name, берется именно он, иначе ищется динамически.
        """
        commits_url = f"{self.url}/repos/{login}/{repo_name}/commits"
        commits_response = requests.get(commits_url, headers=self.headers, params={"per_page": 1})

        if commits_response.status_code != 200 or not commits_response.json():
            raise Exception("Не удалось получить историю коммитов.")

        commit_data = commits_response.json()[0]
        last_commit_sha = commit_data.get("sha")

        commit_detail_url = f"{self.url}/repos/{login}/{repo_name}/commits/{last_commit_sha}"
        commit_detail_response = requests.get(commit_detail_url, headers=self.headers)

        if commit_detail_response.status_code != 200:
            raise Exception("Не удалось получить детали последнего коммита.")

        files = commit_detail_response.json().get("files", [])
        if not files:
            raise Exception("В последнем коммите нет измененных файлов.")

        if not file_name:
            last_file = files[-1]
            file_name = last_file.get("filename")
            if last_file.get("status") == "removed":
                raise Exception(f"Файл '{file_name}' уже удален.")

        content_url = f"{self.url}/repos/{login}/{repo_name}/contents/{file_name}"
        content_response = requests.get(content_url, headers=self.headers)
        if content_response.status_code != 200:
            raise Exception(f"Не удалось получить актуальный SHA для {file_name}")

        current_file_sha = content_response.json().get("sha")

        # 4. Исправлено: метод requests.delete
        data = {
            "message": f"Delete file {file_name}",
            "sha": current_file_sha,
            "committer": {"name": "antares20012", "email": "4ingizxan20012@gmail.com"}
        }

        response = requests.delete(content_url, headers=self.headers, json=data)
        return response.status_code  # или просто response в зависимости от ваших ассертов

    def delete_repo(self, repo_name: str):
        url = f"{self.url}/repos/{self.login}/{repo_name}"
        response = requests.delete(url, headers=self.headers)
        return response.status_code

    # def download_last_repo(self, login: str, repo_name: str, ref: str):
    #     """
    #     Скачивает последний созданный репозиторий
    #     :param login:
    #     :param repo_name:
    #     :param ref:
    #     :return:
    #     """
    #     all_repo_url = f"{self.url}/users/{login}/repos"
    #     repo_response = requests.get(all_repo_url, headers=self.headers, params={"per_page": 1})
    #     if repo_response.status_code != 200:
    #         return repo_response.status_code, None
    #
    #     repo_data = repo_response.json()
    #     ref = repo_data.get("ref")
    #     url = f"{self.url}/repos/{login}/{repo_name}/zipball/{ref}"
    #     response = requests.get(url, headers=self.headers, json={"name": repo_name})
    #
    #     if response.status_code != 201:
    #         print(f"\n[GitHub Error Payload]: {response.json()}")
    #         return response.status_code, None
    #
    #     data = response.json()

    def download_user_latest_repo(self, login: str, output_dir: str = "."):
        """
        Находит последний обновленный репозиторий пользователя и скачивает его.

        :param username: Имя пользователя на GitHub
        :param token: GitHub Personal Access Token (обязателен для приватных репозиториев)
        :param output_dir: Папка для сохранения архива
        """
        print(f"Запрос списка репозиториев...")

        url = f"{self.url}/users/{login}/repos"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            print(f"Ошибка получения списка! Код: {response.status_code}\n{response.text}")
            return None

        repos = response.json()
        if not repos:
            print(f"У пользователя {login} не найдено репозиториев.")
            return None

        # Извлекаем данные самого последнего обновленного репозитория
        repos_sorted = sorted(repos, key=lambda x: x.get("updated_at", ""), reverse=True)
        latest_repo = repos_sorted[0]
        repo_name = latest_repo["name"]
        # Берем владельца из ответа, так как при использовании токена это может быть ваш личный репозиторий
        owner_login = latest_repo["owner"]["login"]

        print(f"Найден последний репозиторий: {owner_login}/{repo_name}")

        # Скачиваем ZIP-архив репозитория
        download_url = f"{self.url}/repos/{owner_login}/{repo_name}/zipball"
        output_path = f"{output_dir}/{repo_name}_latest.zip"

        print("Скачивание архива...")
        with requests.get(
                download_url, headers=self.headers, stream=True
        ) as download_resp:
            if download_resp.status_code == 200:
                with open(output_path, "wb") as file:
                    for chunk in download_resp.iter_content(chunk_size=8192):
                        file.write(chunk)
                print(f"Успешно скачано в: {output_path}")
                return output_path
            else:
                print(
                    f"Ошибка скачивания архива! Код: {download_resp.status_code}\n{download_resp.text}"
                )
                return None
