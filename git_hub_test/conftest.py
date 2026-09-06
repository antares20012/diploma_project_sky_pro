# import os
# from datetime import datetime
# import pytest
# from selenium import webdriver
# from selenium_stealth import stealth
# from pages.GitPageUI import GitPage
#
#
# @pytest.fixture(scope="function")
# def driver():
#     options = webdriver.ChromeOptions()
#     options.add_argument("--start-maximized")
#
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option("useAutomationExtension", False)
#
#     driver = webdriver.Chrome(options=options)
#
#
#     stealth(
#         driver,
#         languages=["ru-RU", "ru"],
#         vendor="Google Inc.",
#         platform="Win32",
#         webgl_vendor="Intel Inc.",
#         renderer="Intel Iris OpenGL Engine",
#         fix_hairline=True,
#     )
#
#     yield driver
#     driver.quit()
#
#
# @pytest.fixture
# def credentials():
#     return {
#         "login": "RudolfAbel20012",
#         "password": "e6@stZ2nQ8wtzk2"
#     }
#
#
# def pytest_addoption(parser):
#     parser.addoption("--file_timestamp", action="store", default="")
#
#
# def pytest_configure(config):
#     timestamp = config.getoption("--file_timestamp")
#
#     # Если пользователь ничего не ввел, генерируем текущее время
#     if not timestamp:
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#
#     # Сохраняем в систему окружения
#     os.environ["MY_FILE_TIMESTAMP"] = timestamp
#
#
# @pytest.fixture(scope="function")
# def github_repo_name(driver, credentials):
#     """Фикстура создаёт репозиторий перед тестом и возвращает его точное динамическое имя."""
#     git_test = GitPage(driver, "https://github.com", credentials)
#     login = credentials["login"]
#     password = credentials["password"]
#     git_test.login_git(login, password)
#     created_repo_name = git_test.create_repository(login)
#
#     return created_repo_name
#
# # @pytest.fixture(scope="session")
# # def file_timestamp():
# #     """Возвращает время старта сессии в формате YYYY-MM-DD_HH-MM-SS."""
# #     return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#
# # ВОЗМОЖНО НЕ БУДЕТ ЗАПИСЫВАТЬ sha commita
#
# # def credentials():
# #     raw_data = {
# #         "variable": [
# #             {"key": "token", "value": "your_token_here"}, # НЕ ЗАБУДЬ УДАЛИТЬ!
# #             {"key": "base_url", "value": "https://github.com"},
# #             {"key": "user_name", "value": "john_doe"},
# #             {"key": "current_repo_name", "value": "test-repo"},
# #             {"key": "last_commit_sha", "value": ""},
# #             {"key": "target_file_sha", "value": ""},
# #             {"key": "target_file_path", "value": ""},
# #             {"key": "test_mail", "value": "test@example.com"},
# #             {"key": "test_user_name", "value": "tester"},
# #             {"key": "current_file_name", "value": ""},
# #             {"key": "login", "value": ""}, # НЕ ЗАБУДЬ УДАЛИТЬ!
# #             {"key": "password", "value": ""} # НЕ ЗАБУДЬ УДАЛИТЬ!
# #         ]
# #     }
# #     return {item["key"]: item["value"] for item in raw_data["variable"]}
#
#
# # import pytest
# # import subprocess
#
#
# # 1. Фикстура (используем scope="session", чтобы данные сохранялись между тестами)
# # @pytest.fixture(scope="session")
# # def credentials():
# #     return {
# #         "token": "my_token",
# #         "last_commit_sha": "",  # Изначально пусто
# #         "current_repo_name": "my-app"
# #     }
# #
# #
# # # # 2. Первый тест получает SHA и записывает его
# # def test_get_latest_commit(credentials):
# #     # Пример А: Получаем SHA локально из Git
# #     cmd = ["git", "rev-parse", "HEAD"]
# #     sha = subprocess.check_output(cmd).decode("utf-8").strip()
# #
# #     # Пример Б: Если бы вы делали запрос к GitHub API, то:
# #     # sha = response.json()["sha"]
# #
# #     # Динамически записываем SHA в фикстуру
# #     credentials["last_commit_sha"] = sha
# #
# #     assert len(credentials["last_commit_sha"]) == 40
# #
# #
# # # 3. Второй тест автоматически видит обновленное значение
# # def test_use_commit_sha(credentials):
# #     # Проверяем, что значение не пустое и сохранилось из прошлого теста
# #     assert credentials["last_commit_sha"] != ""
# #
# #     # Используем SHA в следующем запросе
# #     print(f"Работаем с коммитом: {credentials['last_commit_sha']}")
#
import os
import base64
from faker import Faker
from datetime import datetime
import pytest
from dotenv import load_dotenv
from selenium import webdriver
from selenium_stealth import stealth
from pages.GitPageUI import GitPage
from pages.GitPageAPI import GitPageAPI

load_dotenv()

@pytest.fixture(scope="session")
def github_token():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        pytest.fail("Ошибка: Переменная окружения GITHUB_TOKEN не задана!")
    return token

@pytest.fixture(scope="function")
def git_api(github_token, credentials):
    # Фикстура возвращает готовый экземпляр класса для каждого теста
    login = credentials["login"]
    return GitPageAPI(url="https://api.github.com", token=github_token, login=login)

@pytest.fixture
def to_base64():
    """Фикстура для кодирования строк в Base64."""
    def _encode(text: str) -> str:
        if not text:
            return ""
        return base64.b64encode(text.encode("utf-8")).decode("utf-8")
    return _encode

@pytest.fixture
def random_faker_file_name():
    fake = Faker()
    # fake.word() вернет случайное английское слово, например "development"
    # Добавляем расширение, чтобы получилось "development.md"
    return f"{fake.word()}"

@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)
    stealth(
        driver,
        languages=["ru-RU", "ru"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    yield driver
    driver.quit()


@pytest.fixture
def credentials():
    return {
        "login": "RudolfAbel20012",
        "password": "e6@stZ2nQ8wtzk2"
    }


def pytest_addoption(parser):
    parser.addoption("--file_timestamp", action="store", default="")


def pytest_configure(config):
    timestamp = config.getoption("--file_timestamp")
    if not timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.environ["MY_FILE_TIMESTAMP"] = timestamp


@pytest.fixture()
def repo_name(credentials) -> str:
    """Формирует уникальное имя репозитория."""
    login = credentials["login"]
    timestamp = os.environ.get("MY_FILE_TIMESTAMP")
    return f"{login}_{timestamp}"

# @pytest.fixture(scope="function")
# def github_repo_name(driver, credentials):
#     """Фикстура создаёт репозиторий ДО теста и удаляет его ПОСЛЕ теста."""
#     git_test = GitPage(driver, "https://github.com", credentials)
#     login = credentials["login"]
#     password = credentials["password"]
#
#     # Шаг 1: Авторизация и создание
#     git_test.login_git(login, password)
#     created_repo_name = git_test.create_repository(login)
#
#     # Передаем имя репозитория в тест
#     yield created_repo_name
#
#     # Шаг 2: Гарантированная очистка после завершения теста
#     print(f"\n[Фикстура] Удаляем созданный репозиторий: {created_repo_name}")
#     git_test.delete_repo(login=login, password=password, repo_name=created_repo_name)
