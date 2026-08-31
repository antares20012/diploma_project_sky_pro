from typing import Dict
import time
import os
from datetime import datetime
from random import randint
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys



class GitPage:
    def __init__(self, driver, url: str, credentials: Dict[str, str]):
        self.driver = driver
        self.url = url
        self.wait = WebDriverWait(driver, 10)


    def login_git(self, login: str, password: str):
        self.driver.get(self.url + "/login")

        login_field = self.wait.until(
            EC.presence_of_element_located((
                By.XPATH, "//input[@id='login_field']"
            )))
        login_field.send_keys(login)
        time.sleep(1)

        password_field = self.wait.until(
            EC.presence_of_element_located((
                By.XPATH,  "//input[@id='password']"
            )))
        password_field.send_keys(password)
        time.sleep(2.3)
        commit_btn = self.wait.until(
            EC.element_to_be_clickable((
                By.XPATH, "//input[@name='commit']")))
        commit_btn.click()

    def get_logged_in_username(self) -> str:
        avatar_button = self.wait.until(EC.visibility_of_element_located((
            By.CSS_SELECTOR, "img[alt='User avatar']"
        )))
        self.driver.execute_script("arguments[0].click();", avatar_button)

        profile_button = self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//*[translate(text(), 'PROFILE', 'profile')='profile']"
        )))
        profile_button.click()

        username_element = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".vcard-username"))
        )
        return username_element.text.strip()

##################################
##CREATE_REPO_WORKS_100%
#######

    def create_repository(self, login: str, timestamp: str = None) -> str:
        if not timestamp:
            timestamp = os.environ.get("MY_FILE_TIMESTAMP") or datetime.now().strftime("%Y%m%d_%H%M%S")

        self.driver.get(self.url + "/new")

        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id='owner-dropdown-header-button']")))
        # Проверить соответствие текста с  xpath///*[@id="_r_1c_--label"]
        repo_name_input = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[@id='repository-name-input']"))
        )
        # repo_name = f"{login}_{timestamp}"
        # repo_name_input.clear()
        # repo_name_input.send_keys(repo_name)
        # self.wait.until(
        #     EC.presence_of_element_located(
        #         (By.XPATH, "//*[contains(@id, 'repo-available') or contains(@class, 'success')]"))
        # )
        # self.wait.until(
        #     EC.text_to_be_present_in_element_value(
        #         (By.ID, "repository-name-input"),
        #         repo_name))
        #
        # create_button = self.wait.until(
        #     EC.element_to_be_clickable((
        #         By.XPATH, "//span[contains(text(),'Create repository')]"
        #     )))
        # create_button.click()
        #
        # expected_url_part = f"/{login}/{repo_name}"
        # print(f"Ожидаем переход на URL, содержащий: {expected_url_part}")
        # self.wait.until(EC.url_contains(expected_url_part))
        #
        # print(f"Создан репозиторий: {repo_name}. Текущий URL: {self.driver.current_url}")
        # return repo_name

        repo_name = f"{login}_{timestamp}"
        repo_name_input.clear()
        repo_name_input.send_keys(repo_name)

        # 1. Ждем, пока скроется индикатор загрузки/проверки имени (если он есть)
        time.sleep(2)

        # 2. Ждем, пока кнопка создания станет полностью активной (не disabled)
        # На GitHub кнопка отправки — это button[type='submit']
        create_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )

        # 3. Скроллим до кнопки, чтобы она точно была в зоне видимости драйвера
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", create_button)
        time.sleep(1)

        # 4. Пробуем кликнуть стандартным способом Selenium
        try:
            create_button.click()
        except Exception:
            # Если стандартный клик не сработал (например, элемент перекрыт),
            # нажимаем на кнопку напрямую через JavaScript (это пробивает любые блокировки интерфейса)
            print("Стандартный клик не сработал, нажимаем через JS...")
            self.driver.execute_script("arguments[0].click();", create_button)

        # 5. Ожидаем, что URL изменился (произошел редирект в созданный репо)
        expected_url_part = f"/{login}/{repo_name}"
        print(f"\nОжидаем переход на URL репозитория...")
        self.wait.until(EC.url_contains(expected_url_part))

        print(f"Создан репозиторий: {repo_name}")
        return repo_name


    def create_new_fil(self, repo_name: str, file_name: str, timestamp: str = None) -> str:
        if not timestamp:
            timestamp = os.environ.get("MY_FILE_TIMESTAMP") or datetime.now().strftime("%Y%m%d_%H%M%S")

        name_parts = file_name.split('.')
        if len(name_parts) > 1:
            final_file_name = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
        else:
            final_file_name = f"{file_name}_{timestamp}"

        login = self.get_logged_in_username()

        repo_url = f"https://github.com/{login}/{repo_name}"
        print(repo_url)
        self.driver.get(repo_url)

        # 2. Ищем ссылку "creating a new file" на странице Quick Setup и кликаем по ней
        # create_new_file_link = self.wait.until(
        #     EC.element_to_be_clickable(
        #         (By.XPATH, "//a[contains(@href, '/new/main') or contains(text(), 'creating a new file')]"))
        # )
        # create_new_file_link.click()
        create_new_file_link = self.wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "creating a new file"))
        )
        create_new_file_link.click()
        time.sleep(3)
        # 3. Ожидаем поле ввода имени файла по актуальным селекторам GitHub

        file_name_input = self.wait.until(
            EC.visibility_of_element_located(
                (By.XPATH,
                 "//input[@aria-label='File name' or @name='filename' or @id='file-name-editor']"))
        )
        file_name_input.send_keys(Keys.CONTROL + "a")
        file_name_input.send_keys(Keys.BACKSPACE)

        time.sleep(randint(1, 3))
        file_name_input.send_keys(final_file_name)

        commit_dialog_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Commit changes')]"))
        )
        time.sleep(randint(4, 8))
        commit_dialog_btn.click()

        confirm_commit_btn = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button:nth-of-type(2) > span > span"))
        )
        time.sleep(randint(2, 5))
        confirm_commit_btn.click()
        print(f"Создан файл:{final_file_name}")
        return final_file_name