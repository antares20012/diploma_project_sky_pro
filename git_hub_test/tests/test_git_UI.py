import time
import os
from random import randint
from pages.GitPageUI import GitPage


def test_check_profile(driver, credentials):
    git_test = GitPage(driver,"https://github.com", credentials)
    git_test.login_git(credentials['login'], credentials['password'])
    time.sleep(randint(2,5))

    login = git_test.get_logged_in_username()
    assert login == credentials['login']


def test_create_repository(driver, credentials):
    timestamp = os.environ.get("MY_FILE_TIMESTAMP")
    git_test = GitPage(driver,"https://github.com", credentials)
    git_test.login_git(credentials['login'], credentials['password'])
    time.sleep(randint(3,6))

    current_user = git_test.get_logged_in_username()
    assert current_user == credentials['login'], f"Ожидался пользователь {credentials['login']}, но вошли под {current_user}"

    expected_repo_name = f"{credentials['login']}_{timestamp}"
    created_repo_name = git_test.create_repository(credentials['login'])

    assert created_repo_name == expected_repo_name, f"Имя репозитория не совпадает. Ожидалось: {expected_repo_name}, получено: {created_repo_name}"
    time.sleep(5)

def test_crete_new_file(driver, credentials):
    timestamp = os.environ.get("MY_FILE_TIMESTAMP")
    git_test = GitPage(driver, "https://github.com", credentials)
    git_test.login_git(credentials['login'], credentials['password'])
    time.sleep(randint(2,5))

    # current_user = git_test.get_logged_in_username()
    # assert current_user == credentials['login']

    created_repo_name = git_test.create_repository(credentials['login'], timestamp=timestamp)
    #expected_repo_name = f"{credentials['login']}_{timestamp}"
    # driver.save_screenshot("after_repo_creation.png")
    # print("Текущий URL после создания:", driver.current_url)
    #assert created_repo_name == expected_repo_name, "Имя репозитория не совпадает!"
    time.sleep(6)
    # created_repo_name = git_test.create_repository(credentials['login'])
    # expected_repo_name = f"{credentials['login']}_{timestamp}"
    # assert created_repo_name == expected_repo_name, f"Имя репозитория не совпадает. Ожидалось: {expected_repo_name}, получено: {created_repo_name}"

    target_file = "new_file"
    final_name = git_test.create_new_file(repo_name=created_repo_name, file_name=target_file, timestamp=timestamp)
    expected_file_name = f"new_file_{timestamp}"
    assert final_name == expected_file_name

# def test_file_edits(driver, credentials):
#     timestamp = os.environ.get("MY_FILE_TIMESTAMP")
#     git_test = GitPage(driver, "https://github.com", credentials)
#     git_test.login_git(credentials['login'], credentials['password'])
#     time.sleep(randint(2, 5))
#
#     # current_user = git_test.get_logged_in_username()
#     # assert current_user == credentials['login']
#
#     created_repo_name = git_test.create_repository(credentials['login'], timestamp=timestamp)
#     time.sleep(randint(3, 6))
#     expected_repo_name = f"{credentials['login']}_{timestamp}"
#     driver.save_screenshot("after_repo_creation.png")
#     print("Текущий URL после создания:", driver.current_url)
#     assert created_repo_name == expected_repo_name, "Имя репозитория не совпадает!"
#     time.sleep(6)
#
#     target_file = f"new_file.py"
#     final_name = git_test.create_new_file(repo_name=created_repo_name, file_name=target_file, timestamp=timestamp)
#     # expected_file_name = f"new_file_{timestamp}"
#     # assert final_name == expected_file_name
#     git_test.code_editor(repo_name=created_repo_name, file_name=final_name, timestamp=timestamp)

def test_file_edits(driver, credentials):
    timestamp = os.environ.get("MY_FILE_TIMESTAMP")
    git_test = GitPage(driver, "https://github.com", credentials)
    git_test.login_git(credentials['login'], credentials['password'])

    # 1. Создаем репозиторий и получаем его имя
    created_repo_name = git_test.create_repository(credentials['login'], timestamp=timestamp)
    time.sleep(3)

    # 2. Передаем "чистое" имя. Метод создаст файл и ВЕРНЕТ его финальное имя.
    # Мы сохраняем его в переменную final_name
    final_name = git_test.create_new_file(
        repo_name=created_repo_name,
        file_name="new_file.py",
        timestamp=timestamp
    )
    time.sleep(3)
    print(final_name)

    # 3. Передаем ПРАВИЛЬНОЕ сгенерированное имя в метод редактирования кода
    git_test.code_editor(
        repo_name=created_repo_name,
        file_name=final_name,  # Переменная содержит: new_file_TIMESTAMP.py
        timestamp=timestamp
    )


