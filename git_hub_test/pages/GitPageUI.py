import time
import os
from datetime import datetime
from random import randint
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


class GitPage:
    def __init__(self, driver, url: str, credentials):
        """
        Конструктор класса GitPage.
        :param driver: WebDriver — объект драйвера Selenium.
        """
        self.driver = driver
        self.url = url
        self.credentials = credentials
        self.wait = WebDriverWait(driver, 10)


    def login_git(self, login: str, password: str):
        """Входит на страницу пользователя в а проприетарной платформе разработчиков Github.
        url = https://github.com/login
        Вводит указанные в фикстуре логин и пароль
        :param login:
        :param password:
        :return: None
        """

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
        """
        Возвращает имя пользователя, который авторизовался при помощи логина и пароля.
        :return: Username
        """
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

    def create_repository(self, login: str, timestamp: str = None) -> str:
        """
        1. Авторизуется на странице пользователя.
        2. Создает ПУСТОЙ репозиторий на странице авторизованного пользователя с заданным именем.
        :param login:
        :param timestamp:
        :return: repo_name
        """
        if not timestamp:
            timestamp = os.environ.get("MY_FILE_TIMESTAMP") or datetime.now().strftime("%Y%m%d_%H%M%S")

        self.driver.get(self.url + "/new")

        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//button[@id='owner-dropdown-header-button']")))

        repo_name_input = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[@id='repository-name-input']"))
        )

        repo_name = f"{login}_{timestamp}"
        repo_name_input.clear()
        repo_name_input.send_keys(repo_name)

        time.sleep(2)

        create_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
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

    def create_new_file(self, repo_name: str, file_name: str, timestamp: str = None) -> str:
        """
        1. Авторизуется на странице пользователя.
        2. Создает ПУСТОЙ файл в репозитории авторизованного пользователя.
        3. Оставляет коммит при создании файла.
        :param repo_name:
        :param file_name:
        :param timestamp:
        :return final_file_name:
        """
        # 1. Формирование имени файла
        if not timestamp:
            timestamp = os.environ.get("MY_FILE_TIMESTAMP") or datetime.now().strftime("%Y%m%d_%H%M%S")

        if '.' in file_name:
            name_parts = file_name.rsplit('.', 1)  # Избегаем багов, если в имени несколько точек
            final_file_name = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
        else:
            final_file_name = f"{file_name}_{timestamp}"

        # 2. Переход в репозиторий
        login = self.credentials['login']
        repo_url = f"https://github.com/{login}/{repo_name}"
        self.driver.get(repo_url)

        # 3. Клик по ссылке создания нового файла
        # GitHub часто меняет структуру (кнопка "Add file" -> "Create new file").
        # Этот селектор ищет как прямую ссылку, так и кнопку в выпадающем меню Add File
        create_new_file_link = self.wait.until(EC.presence_of_element_located((
            By.XPATH, "//a[normalize-space()='creating a new file']"
        )))
        create_new_file_link.click()

        # 4. Ввод имени файла
        file_name_input = self.wait.until(EC.visibility_of_element_located((
            By.XPATH,
            "//input[@aria-label='File name'] | //input[@name='filename'] | //input[contains(@data-testid, 'file-name-editor')]"
        )))

        # Более надежная очистка поля перед вводом text
        file_name_input.click()
        file_name_input.clear()
        if file_name_input.get_attribute("value"):
            file_name_input.send_keys(Keys.CONTROL + "a")
            file_name_input.send_keys(Keys.BACKSPACE)

        file_name_input.send_keys(final_file_name)

        # 5. Открытие диалога коммита
        # Кнопка 'Commit changes...' часто имеет тип submit или button
        commit_dialog_btn = self.wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//button[contains(., 'Commit changes') or @data-testid='dialog-show-commit-changes-dialog']"
        )))
        # Имитация человеческой задержки перед отправкой формы
        time.sleep(randint(2, 4))
        commit_dialog_btn.click()

        # 6. Подтверждение коммита во всплывающем окне
        # Селектор "button:nth-of-type(2)" крайне хрупок. Используем точный data-testid или текст внутри модалки
        confirm_commit_btn = self.wait.until(EC.element_to_be_clickable((
            By.XPATH, "//button[@aria-disabled='false']"
        )))
        time.sleep(randint(1, 3))
        confirm_commit_btn.click()
        self.wait.until(EC.none_of(EC.url_contains("/new/")))
        print(f"Создан файл: {final_file_name}")

        return final_file_name

    def code_editor(self, repo_name: str, file_name: str, timestamp: str) -> str:
        """
        1. Изменяет содержимое созданного файла.
        2. Оставляет коммит при сохранении изменений.
        :param repo_name:
        :param file_name:
        :param timestamp:
        :return:
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

    def delete_file(self, login: str, repo_name: str, file_name: str) ->str:
        """
        1. Удаляет созданный в репозитории файл.
        2. Оставляет заданный коммит.
        :param login: login
        :param repo_name: repo_name
        :param file_name: file_name
        :return:
        """
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
        Удаляет созданный репозиторий
        :param login:
        :param password:
        :param repo_name:
        :return:
        """
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

        # 3. Скроллим до кнопки, чтобы она точно была в зоне видимости драйвера
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
            # Ждем появления поля ввода пароля (максимум 5 секунд, чтобы не затягивать)
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

            # 8. Проверка успешного удаления по всплывающему уведомлению
        success_alert = self.wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//div[@role='alert'] | //div[contains(@class, 'js-flash-alert')]"))
        )
        return success_alert.text