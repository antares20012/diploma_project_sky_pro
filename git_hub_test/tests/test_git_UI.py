import time
import  os
from random import randint
from pages.GitPageUI import GitPage


def test_check_profile(driver, credentials):
    git_test = GitPage(driver,"https://github.com", credentials)
    git_test.login_git(credentials['login'], credentials['password'])
    time.sleep(randint(2,5))
    git_test.get_logged_in_username()
    assert git_test.get_logged_in_username() == credentials['login']


def test_create_repository(driver, credentials):
    timestamp = os.environ.get("MY_FILE_TIMESTAMP")
    git_test = GitPage(driver,"https://github.com", credentials)
    git_test.login_git(credentials['login'], credentials['password'])
    time.sleep(randint(3,6))
    git_test.get_logged_in_username()
    current_user = git_test.get_logged_in_username()
    assert current_user == credentials['login'], f"Ожидался пользователь {credentials['login']}, но вошли под {current_user}"
    created_repo_name = git_test.create_repository(credentials['login'])
    expected_repo_name = f"{credentials['login']}_{timestamp}"
    assert created_repo_name == expected_repo_name, f"Имя репозитория не совпадает. Ожидалось: {expected_repo_name}, получено: {created_repo_name}"

def test_create_file(driver, credentials):
    git_test = GitPage(driver, "https://github.com", credentials)

    # Логин
    git_test.login_git(credentials['login'], credentials['password'])
    time.sleep(randint(2,5))
    # assert git_test.is_logged_in(), "Не удалось авторизоваться на GitHub"

    # Создание репозитория
    repo_name = f"{credentials['login']}_{int(time.time())}"
    created_repo_url = git_test.create_repository(repo_name)
    assert created_repo_url is not None, "create_repository не вернул URL репозитория"
    assert repo_name in created_repo_url, f"Создан репозиторий с неожиданным именем: {created_repo_url}"

    # Переход в репозиторий и создание файла
    time.sleep(randint(2,5))
    driver.get(created_repo_url)
    file_name = f"{credentials['login']}_{int(time.time())}"
    created_file_url = git_test.create_new_file(file_name)

    assert created_file_url is not None, "create_new_file не вернул URL файла"
    assert file_name in created_file_url, f"Файл создан с неожиданным именем: {created_file_url}"


def test_crete_new_file(driver, credentials):
    timestamp = os.environ.get("MY_FILE_TIMESTAMP")
    git_test = GitPage(driver, "https://github.com", credentials)
    git_test.login_git(credentials['login'], credentials['password'])
    time.sleep(randint(2,5))
    git_test.get_logged_in_username()
    current_user = git_test.get_logged_in_username()
    assert current_user == credentials['login']
    created_repo_name = git_test.create_repository(credentials['login'])
    expected_repo_name = f"{credentials['login']}_{timestamp}"
    assert created_repo_name == expected_repo_name, f"Имя репозитория не совпадает. Ожидалось: {expected_repo_name}, получено: {created_repo_name}"

