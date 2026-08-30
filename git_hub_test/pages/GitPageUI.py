import random

import pytest
from typing import Dict
import time
import os
from datetime import datetime

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



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

        password_field = self.wait.until(
            EC.presence_of_element_located((
                By.XPATH,  "//input[@id='password']"
            )))
        password_field.send_keys(password)

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
        repo_name = f"{login}_{timestamp}"
        repo_name_input.clear()
        repo_name_input.send_keys(repo_name)
        self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(@id, 'repo-available') or contains(@class, 'success')]"))
        )
        self.wait.until(
            EC.text_to_be_present_in_element_value(
                (By.ID, "repository-name-input"),
                repo_name))

        create_button = self.wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR, "button[type='submit']"
            )))

        create_button.click()
        print(f"Создан репозиторий: {repo_name}")
        return repo_name


    def create_new_file(self, file_name: str, commit_message: str | None = None) -> str:
        """
        Создаёт новый файл в текущем репозитории.
        :param file_name: имя файла (с расширением, например 'test.py')
        :param commit_message: сообщение коммита; если не передано, генерируется автоматически
        :return: URL созданного файла
        """
        if commit_message is None:
            login = self.get_logged_in_username()
            commit_message = f"Add {file_name} by {login}"

        # Открытие меню добавления файла
        add_file_btn = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='add-file-dropdown-button']"))
        )
        add_file_btn.click()

        create_file_item = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='create-new-file-menu-item']"))
        )
        create_file_item.click()

        # Ввод имени файла
        file_name_input = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='file-name-input']"))
        )
        file_name_input.clear()
        file_name_input.send_keys(file_name)

        # Активация и ввод текста в CodeMirror через ActionChains
        editor_container = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='codemirror-editor']"))
        )
        editor_container.click()

        self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "[data-testid='codemirror-editor'] .cm-content")
        ))

        # Эмуляция ввода кода (гарантирует корректную работу отступов CodeMirror)
        file_content = 'def hello():\n    print("Hello World")\n\nhello()'
        ActionChains(self.driver).send_keys(file_content).perform()

        # Ввод заголовка коммита (используем commit-summary-input для первой строки)
        commit_text_input = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#commit-summary-input"))
        )
        commit_text_input.clear()
        commit_text_input.send_keys(commit_message)

        # Подтверждение коммита
        submit_btn = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='submit-commit-button']"))
        )
        submit_btn.click()

        # Ожидание обновления URL и его валидация
        self.wait.until(lambda d: file_name in d.current_url)
        time.sleep(0.5)  # Защита от stale-состояния при мгновенном чтении URL

        return self.driver.current_url
