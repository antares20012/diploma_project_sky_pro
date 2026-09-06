from pages.GitPageAPI import GitPageAPI


def test_create_repository(git_api, repo_name):

    status_code, repo_data = git_api.create_repo(repo_name)
    print(f"\nСтатус создания: {status_code}")
    print(f"Создан репозииторий: {repo_name}")
    print(f"Ссылка на репозиторий: {repo_data['html_url']}")
    assert status_code == 201
    assert repo_data is not None
    assert repo_name in repo_data["full_name"]
    assert repo_name in repo_data["html_url"]

    delete_status = git_api.delete_repo(repo_name)
    print(f"Статус удаления: {delete_status}")
    assert delete_status == 204

def test_create_empty_file(git_api, repo_name,credentials, random_faker_file_name: str):
    repo_status, repo_data = git_api.create_repo(repo_name)
    login = credentials["login"]

    # 2. Создаем пустой файл и получаем статус с данными
    file_status, file_data = git_api.create_empty_file(login, repo_name, file_name=random_faker_file_name)

    # 3. Проверки
    print(f"\nСтатус создания: {repo_status}")
    print(f"Создан репозииторий: {repo_name}")
    print(f"Ссылка на репозиторий: {repo_data['html_url']}")
    assert repo_status in [200, 201]
    assert repo_name in repo_data["full_name"]

    print(f"\nСтатус создания: {file_status}")
    print(f"Создан репозииторий: {file_data}")
    assert file_status == 201
    assert file_data["content"]["name"] == random_faker_file_name
    assert file_data["content"]["size"] == 0


    # 4. Гарантированная очистка данных
    delete_status = git_api.delete_repo(repo_name)
    print(f"Статус удаления: {delete_status}")
    assert delete_status == 204

def test_update_file(git_api, repo_name,credentials, random_faker_file_name: str, to_base64):
    repo_status, repo_data = git_api.create_repo(repo_name)
    login = credentials["login"]

    create_status, create_data = git_api.create_empty_file(login, repo_name, file_name=random_faker_file_name)

    file_sha = create_data["content"]["sha"]
    code_text= "def greeting():\n    print('Hello, World!')\ngreeting()\n"
    update_status, update_data = git_api.update_file(
        login=login, repo_name=repo_name,
        file_name=random_faker_file_name,
        to_base64=to_base64,
        new_text=code_text,
        sha = file_sha
    )


    # Проверки (Ассерты)
    assert repo_status in [200, 201]
    assert repo_name in repo_data["full_name"]
    assert update_status in [200, 201]  # GitHub возвращает 200 при обновлении
    assert update_data["content"]["size"] > 0  # Файл больше не пустой

    # 4. Удаляем репозиторий
    delete_status = git_api.delete_repo(repo_name)
    assert delete_status == 204
    print(f"\nСтатус создания репозитория: {repo_status}. Создан успешно")
    print(f"Создан репозиторий: {repo_name}")
    print(f"Ссылка на репозиторий: {repo_data['html_url']}")
    print(f"Часть текста: {code_text[:12]}")
    print(f"Статус обновления файла: {update_status}. Файл обновлен")
    print(f"Статус удаления: {delete_status}. Удаление прошло успешно")


