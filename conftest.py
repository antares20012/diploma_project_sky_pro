import os
import base64
from faker import Faker
from datetime import datetime
import pytest
from dotenv import load_dotenv
from pygments.lexer import default
from selenium import webdriver
from selenium_stealth import stealth
from pages.GitPageAPI import GitPageAPI

load_dotenv()



@pytest.fixture(scope="session")
def github_token():
    """Фикстура для получения токена GitHub API из переменных окружения.

        Выполняется один раз за всю тестовую сессию (scope="session"). Если
        переменная GITHUB_TOKEN не задана, принудительно прерывает выполнение
        тестов с понятной ошибкой.

        Returns:
            str: Секретный токен авторизации GitHub.
        """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        pytest.fail("Ошибка: Переменная окружения GITHUB_TOKEN не задана! "
                    "Пожалуйста, экспортируйте её перед запуском тестов.")
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

    options.add_argument("--start-maximized")  # Заменяем --start-maximized
    options.add_argument("--disable-gpu")  # Отключаем аппаратное ускорение
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
        "login": os.getenv("LOGIN"), # Логин пользователя. Заполнить для проведения UI тестировани
        "password": os.getenv("PASSWORD") # Пароль пользователя. Заполнить для проведения UI тестировани
    }


def pytest_addoption(parser):
    parser.addoption("--file_timestamp", action="store", default="")
    parser.addoption("--headless", action="store_true", default = False, help="Запуск браузера в фоновом режиме")


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


@pytest.fixture
def temp_repo(git_api, repo_name):
    """Создает и удаляет тестовый репозиторий независимо упал тест или нет"""
    repo_status, repo_data = git_api.create_repo(repo_name)
    assert repo_status in [200, 201], f"Не удалось создать репозиторий. Статус: {repo_status}"

    yield repo_data

    delete_status = git_api.delete_repo(repo_name)
    print(f"\nСтатус удаления репозитория: {delete_status}")