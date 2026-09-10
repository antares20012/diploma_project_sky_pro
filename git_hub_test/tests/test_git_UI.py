import time
import os
from random import randint
from pages.GitPageUI import GitPage
import pytest
import allure


pytestmark =[
    pytest.mark.ui,
    allure.epic("Платформа интеграций"),
    allure.feature("GitHub UI"),
    allure.story("Управление репозиториями и файлами"),
]

@allure.title("Тестирование входа на страницу пользователя в GitHub")
@allure.description("Проверяет корректность входа на страницу пользователя GitHub")
@allure.feature("GitHub")
@allure.severity(allure.severity_level.CRITICAL)
def test_check_profile(driver, credentials):
    git_test = GitPage(driver, "https://github.com", credentials)
    git_test.login_git(credentials['login'], credentials['password'])
    time.sleep(randint(2, 5))

    login = git_test.get_logged_in_username()
    assert login == credentials['login'], f"Ожидался логин {credentials['login']}, но получен {login}"

@allure.title("Тестирование создания репозитория на странице авторизованного пользователя в GitHub")
@allure.description("Проверяет успешное создание нового репозитория после авторизации пользователя")
@allure.feature("GitHub")
@allure.story("Создание репозитория")
@allure.severity(allure.severity_level.CRITICAL)
def test_create_repo(driver, credentials):
    """Тест просто проверяет работоспособность фикстуры создания репозитория."""
    timestamp = os.environ.get("MY_FILE_TIMESTAMP")
    git_test = GitPage(driver, "https://github.com", credentials)
    git_test.login_git(credentials['login'], credentials['password'])
    git_test.create_repository(login=credentials['login'], timestamp=timestamp)

@allure.title("Тестирование создания пустого файла в новом репозитории авторизованного пользователя в GitHub")
@allure.description("Проверяет успешное создание нового пустого файла после создания репозитория")
@allure.feature("GitHub")
@allure.story("Создание пустого файла")
@allure.severity(allure.severity_level.CRITICAL)
def test_create_new_file(driver, credentials):
    """Тест создаёт файл в уже существующем (благодаря фикстуре) репозитории."""
    timestamp = os.environ.get("MY_FILE_TIMESTAMP")
    git_test = GitPage(driver, "https://github.com", credentials)
    git_test.login_git(credentials['login'], credentials['password'])
    login = credentials['login']
    password = credentials['password']
    repo_name = git_test.create_repository(login, timestamp)
    target_file = "new_file"
    time.sleep(2)
    final_name = git_test.create_new_file(repo_name=repo_name, file_name=target_file, timestamp=timestamp)

    expected_file_name = f"new_file_{timestamp}"
    assert final_name == expected_file_name

    git_test.delete_file(login=credentials['login'], repo_name=repo_name, file_name=final_name)
    result_text = git_test.delete_repo(login=login, password=password, repo_name=repo_name)
    assert result_text is not None

@allure.title("Тестирование изменения последнего созданного файла в репозитории авторизованного пользователя GitHub")
@allure.description("Проверяет успешное изменение файла после создания")
@allure.feature("GitHub")
@allure.story("Изменение файла")
@allure.severity(allure.severity_level.CRITICAL)
def test_file_edits(driver, credentials):
    """Тест создаёт файл, редактирует его код и затем подчищает за собой."""
    timestamp = os.environ.get("MY_FILE_TIMESTAMP")
    git_test = GitPage(driver, "https://github.com", credentials)
    git_test.login_git(credentials['login'], credentials['password'])
    login = credentials['login']
    password = credentials['password']
    repo_name = git_test.create_repository(login, timestamp)
    time.sleep(3)
    final_name = git_test.create_new_file(
        repo_name=repo_name,
        file_name="new_file",
        timestamp=timestamp
    )
    time.sleep(3)

    git_test.code_editor(
        repo_name=repo_name,
        file_name=final_name,
        timestamp=timestamp
    )

    git_test.delete_file(login=login, repo_name=repo_name, file_name=final_name)
    time.sleep(3)
    result_text = git_test.delete_repo(login=login, password=password, repo_name=repo_name)
    assert result_text is not None

@allure.title("Тестирование удаления последнего измененного файла в репозитории авторизованного пользователя GitHub")
@allure.description("Проверяет успешное удаление файла после измененеия")
@allure.feature("GitHub")
@allure.story("Изменение файла")
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_file(driver, credentials):
    """Тест изолированно проверяет удаление файла."""
    timestamp = os.environ.get("MY_FILE_TIMESTAMP")

    git_test = GitPage(driver, "https://github.com", credentials)
    git_test.login_git(credentials['login'], credentials['password'])
    git_test.get_logged_in_username()
    login = credentials['login']
    password = credentials['password']
    repo_name = git_test.create_repository(login=login, timestamp=timestamp)
    time.sleep(3)

    final_name = git_test.create_new_file(repo_name=repo_name, file_name="file_for_delete.py",
                                          timestamp=timestamp)
    time.sleep(2)

    git_test.delete_file(login=credentials['login'], repo_name=repo_name, file_name=final_name)
    time.sleep(3)
    result_text = git_test.delete_repo(login=login, password=password, repo_name=repo_name)
    assert result_text is not None

@allure.title("Тестирование изменения последнего созданного репозитория авторизованного пользователя GitHub")
@allure.description("Проверяет успешное удаление последнего созданного репозитория")
@allure.feature("GitHub")
@allure.story("Удаление репозитория")
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_repo(driver, credentials):
    """Тест удаляет динамически созданный фикстурой репозиторий."""
    timestamp = os.environ.get("MY_FILE_TIMESTAMP")
    git_test = GitPage(driver, "https://github.com", credentials)
    git_test.login_git(credentials['login'], credentials['password'])
    git_test.get_logged_in_username()
    login = credentials['login']
    password = credentials['password']
    repo_name = git_test.create_repository(login=login, timestamp=timestamp)
    time.sleep(3)

    result_text = git_test.delete_repo(login=login, password=password, repo_name=repo_name)
    assert result_text is not None
