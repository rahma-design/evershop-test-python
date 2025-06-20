import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from config import ADMIN_LOGIN_URL, ADMIN_EMAIL, ADMIN_PASSWORD

class TestAdminLogin:
    @pytest.fixture(scope="function")
    def driver(self):
        # Configuration des options Chrome
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--headless')  # Exécution sans interface graphique (désactivé pour debug)
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        try:
            # Installation et configuration du ChromeDriver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.implicitly_wait(10)
            yield driver
        finally:
            if 'driver' in locals():
                driver.quit()

    def test_login_success(self, driver):
        driver.get(ADMIN_LOGIN_URL)
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        password_input = driver.find_element(By.NAME, "password")
        email_input.send_keys(ADMIN_EMAIL)
        password_input.send_keys(ADMIN_PASSWORD)
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        submit_button.click()
        driver.save_screenshot("apres_login_success.png")
        print("URL après login:", driver.current_url)
        dashboard_title = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.page-heading-title"))
        )
        assert dashboard_title.text == "Dashboard" 