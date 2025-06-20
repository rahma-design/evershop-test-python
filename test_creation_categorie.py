import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from config import ADMIN_LOGIN_URL, ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_CATEGORIES_URL

class TestCategoryCreation:
    @pytest.fixture(scope="function")
    def driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        # chrome_options.add_argument('--headless')
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(10)
        yield driver
        driver.quit()

    def safe_click(self, driver, by, value, timeout=10):
        element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, value)))
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        WebDriverWait(driver, 0.5).until(lambda d: element.is_displayed() and element.is_enabled())
        try:
            element.click()
        except Exception:
            driver.execute_script("arguments[0].click();", element)

    def delete_category(self, driver, category_name):
        driver.get(ADMIN_CATEGORIES_URL)
        print("URL courante:", driver.current_url)
        print("HTML page:", driver.page_source[:1000])
        driver.save_screenshot("debug_before_delete.png")
        search_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "name"))
        )
        search_input.clear()
        search_input.send_keys(category_name)
        search_input.send_keys(Keys.ENTER)
        rows = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table.listing tbody tr"))
        )
        print(f"{len(rows)} lignes trouvées dans le tableau après recherche de la catégorie '{category_name}'")
        checkbox_clicked = False
        for row in rows:
            columns = row.find_elements(By.TAG_NAME, "td")
            if len(columns) > 1:
                name = columns[1].text.strip() if len(columns) > 1 else ""
                if name == category_name:
                    checkbox = columns[0].find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                    ActionChains(driver).move_to_element(checkbox).click().perform()
                    checkbox_clicked = True
                    print(f"Catégorie '{category_name}' trouvée et sélectionnée.")
                    break
        assert checkbox_clicked, f"La catégorie '{category_name}' n'a pas été trouvée ou sélectionnée."
        time.sleep(1)
        delete_button = None
        for span in driver.find_elements(By.CSS_SELECTOR, "span"):
            if span.text.strip().lower() == "delete":
                delete_button = span
                break
        assert delete_button, "Bouton Delete non trouvé."
        delete_button.click()
        print("Bouton Delete cliqué.")
        modal_delete_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Delete']]"))
        )
        modal_delete_button.click()
        WebDriverWait(driver, 10).until(EC.invisibility_of_element(modal_delete_button))
        print(f"Catégorie '{category_name}' supprimée.")

    def test_create_and_delete_category(self, driver):
        category_name = "Chaussures de sport"
        url_key = "chaussures-de-sport"
        meta_title = "Chaussures de sport - Boutique"
        meta_keywords = "sport, chaussures, fitness, running"

        # 1. LOGIN
        driver.get(ADMIN_LOGIN_URL)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(ADMIN_EMAIL)
        driver.find_element(By.NAME, "password").send_keys(ADMIN_PASSWORD)
        self.safe_click(driver, By.CSS_SELECTOR, "button[type='submit']")
        dashboard_title = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.page-heading-title"))
        )
        assert dashboard_title.text == "Dashboard"
        print("[STEP] Login réussi")

        # 2. CRÉATION CATÉGORIE
        driver.get(ADMIN_CATEGORIES_URL)
        self.safe_click(driver, By.LINK_TEXT, "New Category")
        WebDriverWait(driver, 10).until(EC.url_contains("/admin/categories/new"))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "name"))).send_keys(category_name)
        driver.find_element(By.NAME, "url_key").send_keys(url_key)
        driver.find_element(By.NAME, "meta_title").send_keys(meta_title)
        driver.find_element(By.NAME, "meta_keywords").send_keys(meta_keywords)
        self.safe_click(driver, By.XPATH, "//button[contains(@class, 'button') and contains(@class, 'primary') and .//span[text()='Save']]")
        print("[STEP] Catégorie créée")
        toast_body = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".Toastify__toast--success .Toastify__toast-body"))
        )
        print("Toast HTML:", toast_body.get_attribute("outerHTML"))
        print("Toast text:", toast_body.text)
        assert "category saved successfully" in toast_body.text.lower()
        print("[SUCCESS] Catégorie créée avec succès.")

        # 3. SUPPRESSION CATÉGORIE
        self.delete_category(driver, category_name)
        print("[SUCCESS] Catégorie supprimée à la fin du test.")