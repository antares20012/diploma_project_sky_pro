import time
import os
import allure
from datetime import datetime
from random import randint
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys




class GitPage:
    """
        Класс Page Object для взаимодействия с веб-интерфейсом платформы GitHub.

        Обеспечивает автоматизацию сквозного сценария (E2E): авторизацию,
        создание репозитория, добавление, редактирование и удаление файлов,
        а также полное удаление репозитория.
        """
    LOGIN_FIELD = (By.XPATH, "//input[@id='login_field']")
    PASSWORD_FIELD = (By.XPATH,  "//input[@id='password']")
    REPO_NAME_INPUT = (By.XPATH, "//input[@id='repository-name-input']")
    LOGIN_COMMIT = (By.XPATH, "//input[@name='commit']")
    AVATAR_BTN = (By.CSS_SELECTOR, "img[alt='User avatar']")
    PROFILE_BTN = (By.XPATH, "//*[translate(text(), 'PROFILE', 'profile')='profile']" )
    REPO_SUBMIT_BTN = (By.CSS_SELECTOR, "button[type='submit']")
    CREATE_EMPTY_FILE = (By.XPATH, "//a[normalize-space()='creating a new file']")


    def __init__(self, driver, url: str, credentials):
        """
           Инициализирует объект страницы GitHub.

           :param driver: WebDriver — объект драйвера Selenium для управления браузером.
           :param url: str — базовый URL-адрес платформы (например, https://github.com).
           :param credentials: dict — словарь с учетными данными пользователя {'login': '...', 'password': '...'}.
        """
        self.driver = driver
        self.url = url
        self.credentials = credentials
        self.wait = WebDriverWait(driver, 10)

    # @allure.step("Вход в GitHub")
    def login_git(self, login: str, password: str):
        """
        Выполняет авторизацию пользователя на странице /login.

        Вводит переданные логин и пароль в соответствующие текстовые поля
        и кликает по кнопке подтверждения ("Sign in").

        :param login: str — логин или email пользователя.
        :param password: str — пароль от учетной записи.
        :return: None
        """

        with allure.step(f"Вход в GitHub под пользователем: {login}"):
            self.driver.get(self.url + "/login")

            login_field = self.wait.until(
                EC.presence_of_element_located(self.LOGIN_FIELD))
            login_field.send_keys(login)
            time.sleep(1)

            password_field = self.wait.until(
                EC.presence_of_element_located(self.PASSWORD_FIELD))
            password_field.send_keys(password)
            time.sleep(2.3)

            commit_btn = self.wait.until(
                EC.element_to_be_clickable(self.LOGIN_COMMIT))
            commit_btn.click()

    @allure.step("Получение имени пользователя, вошедшего в GitHub")
    def get_logged_in_username(self) -> str:
        """
        Извлекает имя текущего авторизованного пользователя из его профиля.

        Метод кликает по аватару в правом верхнем углу, переходит в профиль
        и считывает текст из элемента юзернейма для верификации успешного входа.

        :return: str — отображаемое имя пользователя (vcard-username).
        """
        avatar_button = self.wait.until(EC.visibility_of_element_located(self.AVATAR_BTN))
        self.driver.execute_script("arguments[0].click();", avatar_button)

        profile_button = self.wait.until(EC.element_to_be_clickable(self.PROFILE_BTN))
        profile_button.click()

        username_element = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".vcard-username"))
        )
        return username_element.text.strip()

    @allure.step("Создание репозитория на странице авторизованного пользователя GitHub")
    def create_repository(self, login: str, timestamp: str = None) -> str:
        """
           Создает новый пустой публичный/приватный репозиторий.

           Имя репозитория формируется динамически на основе логина и временной метки
           для обеспечения уникальности при повторных запусках тестов.

           :param login: str — логин пользователя (используется как префикс имени репозитория).
           :param timestamp: str, optional — уникальная временная метка. Если не передана, генерируется автоматически.
           :return: str — сгенерированное имя созданного репозитория (формат: login_timestamp).
        """

        if not timestamp:
            timestamp = os.environ.get("MY_FILE_TIMESTAMP") or datetime.now().strftime("%Y%m%d_%H%M%S")

        self.driver.get(self.url + "/new")

        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//button[@id='owner-dropdown-header-button']")))

        repo_name_input = self.wait.until(
            EC.element_to_be_clickable(self.REPO_NAME_INPUT)
        )

        repo_name = f"{login}_{timestamp}"
        repo_name_input.clear()
        repo_name_input.send_keys(repo_name)

        time.sleep(2)

        create_button = self.wait.until(
            EC.element_to_be_clickable(self.REPO_SUBMIT_BTN)
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", create_button)
        time.sleep(3)
        try:
            create_button.click()
        except Exception:
            print("Стандартный клик не сработал, нажимаем через JS...")
            self.driver.execute_script("arguments[0].click();", create_button)

        print(f"\nОжидаем переход на URL репозитория...")

        print(f"Создан репозиторий: {repo_name}")
        return repo_name

    @allure.step("Создание пустого файла в новом репозитории GitHub")
    def create_new_file(self, repo_name: str, file_name: str, timestamp: str = None) -> str:
        """
        Создает новый пустой файл в указанном репозитории.

        Переходит по прямому URL репозитория, нажимает кнопку создания файла,
        вводит уникальное имя файла с временной меткой и подтверждает коммит.

        :param repo_name: str — имя целевого репозитория, в котором создается файл.
        :param file_name: str — базовое имя файла (может включать расширение, например 'test.py').
        :param timestamp: str, optional — временная метка для уникализации имени файла.
        :return: str — финальное имя созданного файла с учетом временной метки.
        """

        if not timestamp:
            timestamp = os.environ.get("MY_FILE_TIMESTAMP") or datetime.now().strftime("%Y%m%d_%H%M%S")

        if '.' in file_name:
            name_parts = file_name.rsplit('.', 1)  # Избегаем багов, если в имени несколько точек
            final_file_name = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
        else:
            final_file_name = f"{file_name}_{timestamp}"


        login = self.credentials['login']
        repo_url = f"https://github.com/{login}/{repo_name}"
        self.driver.get(repo_url)

        create_new_file_link = self.wait.until(EC.presence_of_element_located(self.CREATE_EMPTY_FILE))
        create_new_file_link.click()


        file_name_input = self.wait.until(EC.visibility_of_element_located((
            By.XPATH,
            "//input[@aria-label='File name'] | //input[@name='filename'] | //input[contains(@data-testid, 'file-name-editor')]"
        )))

        file_name_input.click()
        file_name_input.clear()
        if file_name_input.get_attribute("value"):
            file_name_input.send_keys(Keys.CONTROL + "a")
            file_name_input.send_keys(Keys.BACKSPACE)

        file_name_input.send_keys(final_file_name)

        commit_dialog_btn = self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//button[contains(., 'Commit changes') or @data-testid='dialog-show-commit-changes-dialog']"
        )))

        time.sleep(randint(2, 4))
        commit_dialog_btn.click()


        confirm_commit_btn = self.wait.until(EC.element_to_be_clickable((
            By.XPATH, "//button[@aria-disabled='false']"
        )))
        time.sleep(randint(1, 3))
        confirm_commit_btn.click()
        self.wait.until(EC.none_of(EC.url_contains("/new/")))
        print(f"Создан файл: {final_file_name}")

        return final_file_name

    @allure.step("Измененеие пустого файла file_name")
    def code_editor(self, repo_name: str, file_name: str, timestamp: str) -> str:
        """
            Открывает встроенный текстовый редактор GitHub и изменяет содержимое файла.

            Метод находит созданный файл в корне репозитория, нажимает на иконку редактирования,
            очищает старое содержимое, вставляет шаблонный код на Python ("Hello, World!")
            и сохраняет изменения, указывая текущее время в сообщении коммита.

            :param repo_name: str — имя репозитория.
            :param file_name: str — точное имя изменяемого файла.
            :param timestamp: str — временная метка (не используется напрямую, заменяется на актуальное время коммита).
            :return: str — текст сообщения коммита (Commit Message).
        """

        current_time_str = datetime.now().strftime("%Y%m%d_%H%M%S")

        login = self.credentials['login']
        repo_url = f"https://github.com/{login}/{repo_name}"
        if self.driver.current_url != repo_url:
            self.driver.get(repo_url)

        file_element = self.wait.until(EC.presence_of_element_located((
            By.XPATH, f"//a[@title='{file_name}' or text()='{file_name}']"
        )))
        self.driver.execute_script("arguments[0].click();", file_element)

        edit_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='edit-button'] svg")))
        edit_btn.click()

        editor_textarea = self.wait.until(EC.presence_of_element_located((
            By.XPATH, "//div[@role='textbox']"
        )))

        editor_textarea.click()
        editor_textarea.send_keys(Keys.CONTROL + "a")
        editor_textarea.send_keys(Keys.BACKSPACE)

        new_text = "def greeting():\n    print('Hello, World!')\ngreeting()\n"
        editor_textarea.send_keys(new_text)

        commit_changes_btn = self.wait.until(
            EC.element_to_be_clickable((
                By.XPATH, "//span[contains(text(),'Commit changes...')]"
            )))
        commit_changes_btn.click()

        commit_message_input = self.wait.until(
            EC.presence_of_element_located((
                By.XPATH, "//input[@id='commit-message-input']"
            )))
        commit_message_input.clear()
        commit_message_input.send_keys(f"{current_time_str}")

        confirm_commit_btn = self.wait.until(EC.element_to_be_clickable((
            By.XPATH, "//button[@aria-disabled='false']"
        )))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", confirm_commit_btn)
        confirm_commit_btn.click()

        self.wait.until(EC.none_of(EC.url_contains("/edit/")))

        print(f"Файл {file_name} успешно сохранен!")
        return f"Update {file_name} at {current_time_str}"

    @allure.step("Удаление последнего созданного файла")
    def delete_file(self, login: str, repo_name: str, file_name: str) ->str:
        """Удаляет файл из репозитория через веб-интерфейс.
        Переходит к файлу,
        открывает контекстное меню дополнительных действий ("More file actions"),
        выбирает пункт "Delete file" и подтверждает операцию коммитом.
        :param login: str — логин владельца репозитория.
        :param repo_name: str — имя репозитория.
        :param file_name: str — имя удаляемого файла.
        :return: str — статусная строка, подтверждающая удаление."""
        current_time_str = datetime.now().strftime("%Y%m%d_%H%M%S")

        repo_url = f"https://github.com/{login}/{repo_name}"
        if self.driver.current_url != repo_url:
            self.driver.get(repo_url)

        file_element = self.wait.until(EC.presence_of_element_located((
            By.XPATH, f"//a[@title='{file_name}' or text()='{file_name}']"
        )))
        self.driver.execute_script("arguments[0].click();", file_element)

        more_actions_locator = (By.XPATH, "//button[@data-testid='more-file-actions-button-nav-menu-wide']")
        more_actions_btn = self.wait.until(EC.element_to_be_clickable(more_actions_locator))
        more_actions_btn.click()

        delete_file_locator = (By.XPATH, "//*[text()='Delete file']")
        delete_file_btn = self.wait.until(EC.element_to_be_clickable(delete_file_locator))
        delete_file_btn.click()

        commit_changes_btn = self.wait.until(
            EC.element_to_be_clickable((
                By.XPATH, "//span[contains(text(),'Commit changes...')]"
            )))
        commit_changes_btn.click()

        commit_message_input = self.wait.until(
            EC.presence_of_element_located((
                By.XPATH, "//input[@id='commit-message-input']"
            )))
        commit_message_input.clear()
        commit_message_input.send_keys(f"{current_time_str}")

        confirm_commit_btn = self.wait.until(EC.element_to_be_clickable((
            By.XPATH, "//button[@aria-disabled='false']"
        )))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", confirm_commit_btn)
        confirm_commit_btn.click()
        return f"Deleted: {file_name}"


    def delete_repo(self, login: str, password: str, repo_name: str) ->str:
        """
            Полностью удаляет репозиторий из учетной записи GitHub.
            Проходит многоэтапную процедуру подтверждения в "Danger Zone" настроек:
            клики по кнопкам предупреждений, ввод проверочного текста формата "login/repo_name".
            При необходимости (в зависимости от сессии GitHub) обрабатывает окно повторного ввода пароля (Sudo-режим).
            :param login: str — логин владельца репозитория.
            :param password: str — пароль для прохождения Sudo-проверки GitHub.
            :param repo_name: str — имя удаляемого репозитория.
            :return: str — текст всплывающего уведомления об успешном удалении (успешный alert).
        """

        with allure.step(f"Удаление репозитория пользователем: {login}"):
            repo_url = f"https://github.com/{login}/{repo_name}"
            if self.driver.current_url != repo_url:
                self.driver.get(repo_url)

            settings_btn = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//span[normalize-space()='Settings']"))
            )
            settings_btn.click()

            delete_repo_btn = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#dialog-show-repo-delete-menu-dialog"))
            )


            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", delete_repo_btn)
            time.sleep(1)
            delete_repo_btn.click()

            want_btn = self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH, "//span[contains(text(),'I want to delete this repository')]"
                )))
            want_btn.click()
            time.sleep(2)
            understand_btn = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'I have read and understand these effects')]"))
            )
            understand_btn.click()
            time.sleep(2)

            time.sleep(2)
            verification_field = self.wait.until(
                EC.visibility_of_element_located((By.XPATH, "//input[@id='verification_field']"))
            )
            verification_field.clear()
            verification_field.send_keys(f"{login}/{repo_name}")
            time.sleep(1)

            proceed_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#repo-delete-proceed-button")))
            proceed_btn.click()
            time.sleep(1)

            try:
                sudo_pwd = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located((By.XPATH, "//input[@id='sudo_password']"))
                )
                sudo_pwd.clear()
                sudo_pwd.send_keys(password)

                delete_commit_btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//form[@action='/sudo']//button[@type='submit']"))
                )
                delete_commit_btn.click()
                print("Пароль потребовался и был успешно введен.")
            except TimeoutException:
                print("Ввод пароля не потребовался, репозиторий удален сразу.")

            success_alert = self.wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//div[@role='alert'] | //div[contains(@class, 'js-flash-alert')]"))
            )
            return success_alert.text