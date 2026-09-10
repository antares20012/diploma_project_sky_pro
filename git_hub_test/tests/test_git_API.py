import os
import pytest
import allure


pytestmark =[
    pytest.mark.api,
    allure.epic("Платформа интеграций"),
    allure.feature("GitHub API"),
    allure.story("Управление репозиториями и файлами"),
]

@allure.title("Тестирование создания репозитория на странице пользователя в GitHub")
@allure.description("Проверяет корректность API запросов при создании репозитория")
@allure.feature("GitHub")
@allure.severity(allure.severity_level.CRITICAL)
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

@allure.title("Тестирование создания пустого файла в репозитории на странице пользователя в GitHub")
@allure.description("Проверяет корректность API запросов при создании файла")
@allure.feature("GitHub")
@allure.severity(allure.severity_level.CRITICAL)
def test_create_empty_file(git_api, repo_name,credentials, random_faker_file_name: str, temp_repo):
    repo_data = temp_repo
    login = credentials["login"]
    # Проверка создания репозитория (базовая)
    assert repo_name in repo_data["full_name"]
    print(f"\nРепозиторий готов: {repo_data['html_url']}")

    # 2. Создаем пустой файл и получаем статус с данными
    file_status, file_data = git_api.create_empty_file(login, repo_name, file_name=random_faker_file_name)

    print(f"Статус создания файла: {file_status}")
    # 3. Проверки файла
    assert file_status == 201
    assert file_data["content"]["name"] == random_faker_file_name
    assert file_data["content"]["size"] == 0

    # 4. Удаление файла (внутри теста, так как проверяем специфичный метод удаления)
    # delete_file_status = git_api.delete_last_modified_file(login, repo_name)
    delete_file_status = git_api.delete_last_modified_file(login, repo_name, file_data["content"]["name"])
    print(f"Статус удаления файла: {delete_file_status}")
    assert delete_file_status == 200

@allure.title("Тестирование изменения последнего файла в репозитории на странице пользователя в GitHub")
@allure.description("Проверяет корректность API запросов при изменении последнего файла")
@allure.feature("GitHub")
@allure.severity(allure.severity_level.CRITICAL)
def test_update_file(git_api, repo_name,credentials, random_faker_file_name: str, to_base64, temp_repo):

    repo_data = temp_repo
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
    assert repo_name in repo_data["full_name"]
    assert update_status in [200, 201]  # GitHub возвращает 200 при обновлении
    assert update_data["content"]["size"] > 0  # Файл больше не пустой
    print(f"\nСоздан репозиторий: {repo_name}")
    print(f"Ссылка на репозиторий: {repo_data['html_url']}")
    print(f"Часть текста: {code_text[:12]}")
    print(f"Статус обновления файла: {update_status}. Файл обновлен")

@allure.title("Тестирование чтения последнего файла в репозитории на странице пользователя в GitHub")
@allure.description("Проверяет корректность API запросов при чтении последнего файла")
@allure.feature("GitHub")
@allure.severity(allure.severity_level.CRITICAL)
def test_read_file(git_api, repo_name, credentials, random_faker_file_name: str, to_base64, temp_repo):

    login = credentials["login"]

    # 1. Создаем пустой файл и получаем его SHA
    status_create, create_data = git_api.create_empty_file(
        login, repo_name, file_name=random_faker_file_name
    )
    assert status_create == 201, f"Не удалось создать файл, статус: {status_create}"
    file_sha = create_data["content"]["sha"]

    # 2. Обновляем файл текстом
    expected_text = "def greeting():\n    print('Hello, World!')\ngreeting()\n"
    status_update, update_data = git_api.update_file(
        login=login,
        repo_name=repo_name,
        file_name=random_faker_file_name,
        to_base64=to_base64,
        new_text=expected_text,
        sha=file_sha
    )
    assert status_update == 200, f"Не удалось обновить файл, статус: {status_update}"

    # 3. Читаем содержимое файла для проверки
    status_code, file_data, decoded_text = git_api.read_file(
        login, repo_name, file_name=random_faker_file_name
    )

    # 4. Проверки (Ассерты)
    assert status_code == 200, f"Ожидался статус 200, получили {status_code}"

    # Наличие поля sha в ответе get_file_content
    assert "sha" in file_data, "В ответе отсутствует поле 'sha'"
    assert file_data["sha"] is not None and file_data["sha"] != "", "Поле 'sha' пустое"
    assert decoded_text == expected_text, f"Текст не совпадает. Ожидалось: '{expected_text}', получили: '{decoded_text}'"

@allure.title("Тестирование скачивания репозитория со страницы пользователя в GitHub")
@allure.description("Проверяет корректность API запросов при скачивании репозитория")
@allure.feature("GitHub")
@allure.severity(allure.severity_level.CRITICAL)
def test_download_user_latest_repo(git_api, repo_name,credentials, random_faker_file_name: str, to_base64, temp_repo):
    login = credentials["login"]
    create_status, create_data = git_api.create_empty_file(login, repo_name, file_name=random_faker_file_name)
    assert create_status == 201, f"Не удалось создать файл: {create_data}"
    file_sha = create_data["content"]["sha"]
    expected_text = "def greeting():\n    print('Hello, World!')\n"
    status_update, update_data = git_api.update_file(
        login=login,
        repo_name=repo_name,
        file_name=random_faker_file_name,
        to_base64=to_base64,
        new_text=expected_text,
        sha=file_sha
    )
    assert status_update == 200, f"Не удалось обновить файл: {update_data}"
    downloaded_file_path = git_api.download_user_latest_repo(
        login, output_dir="."
    )
    assert (
            downloaded_file_path is not None
    ), "Метод вернул None, скачивание не удалось."
    assert os.path.exists(
        downloaded_file_path
    ), f"Файл {downloaded_file_path} не был создан на диске."
    assert (
            os.path.getsize(downloaded_file_path) > 0
    ), "Скачанный архив пуст (размер 0 байт)."

    if os.path.exists(downloaded_file_path):
        os.remove(downloaded_file_path)
