import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from config import ADMIN_LOGIN_URL, ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_NEW_PRODUCT_URL
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time

class TestProductCreation:

    @pytest.fixture(scope="function")
    def driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        # chrome_options.add_argument('--headless')  # Décommente pour mode headless
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

    def delete_existing_product(self, driver):
        product_name = "Bague-Test"
        driver.get(ADMIN_NEW_PRODUCT_URL.replace("/new", ""))  # URL liste produits

        # 1. Saisir le nom dans le champ de recherche et valider
        search_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "keyword"))
        )
        search_input.clear()
        search_input.send_keys(product_name)
        search_input.send_keys(Keys.ENTER)

        # 2. Attendre la première ligne du tableau (hors lignes vides)
    
        rows = driver.find_element(By.CSS_SELECTOR, "table.listing tbody tr")
        checkbox_clicked = False
        for row in rows:
            columns = row.find_elements(By.TAG_NAME, "td")
            if len(columns) > 1:
                name = columns[2].text.strip() if len(columns) > 2 else ""
                if name == product_name:
                    checkbox = columns[0].find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                   
                    ActionChains(driver).move_to_element(checkbox).click().perform()
                    checkbox_clicked = True
                    break
        assert checkbox_clicked, f"Le produit '{product_name}' n'a pas été trouvé ou sélectionné."
        time.sleep(5)
        # 4. Cliquer sur le bouton Delete global (span avec texte 'Delete')
        delete_button = None
        for span in driver.find_elements(By.CSS_SELECTOR, "span"):
            if span.text.strip() == "Delete":
                delete_button = span
                break
        if delete_button:
            delete_button.click()
        else:
            print("Bouton Delete non trouvé.")
            return

        # 5. Confirmer la suppression
        confirm_button = None
        for btn in driver.find_elements(By.CSS_SELECTOR, "button"):
            if "Confirm" in btn.text:
                confirm_button = btn
                break
        if confirm_button:
            WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Confirm')]")))
            confirm_button.click()
            WebDriverWait(driver, 3).until(
                EC.invisibility_of_element(confirm_button)
            )
            #test
            #hhhhhhhh
            
            print(f"Produit '{product_name}' supprimé.")
        else:
            print("Bouton Confirm non trouvé.")

    def test_login_and_create_product(self, driver):
        product_name = "Bague-Test"
        unique_sku = "BAG-FEM-032-FIXE"
        url_key = "bague-test"

        # LOGIN ADMIN
        driver.get(ADMIN_LOGIN_URL)
        email_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))
        email_input.send_keys(ADMIN_EMAIL)
        driver.find_element(By.NAME, "password").send_keys(ADMIN_PASSWORD)
        self.safe_click(driver, By.CSS_SELECTOR, "button[type='submit']")

        dashboard_title = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.page-heading-title"))
        )
        assert dashboard_title.text == "Dashboard"

        # SUPPRIMER SI PRODUIT EXISTANT
        self.delete_existing_product(driver)

        # # AJOUT PRODUIT
        # driver.get(ADMIN_NEW_PRODUCT_URL)
        # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "name"))).send_keys(product_name)
        # driver.find_element(By.NAME, "sku").send_keys(unique_sku)
        # driver.find_element(By.NAME, "price").send_keys("89.99")
        # driver.find_element(By.NAME, "weight").send_keys("0.25")

        # # Sélectionner la catégorie 'Women'
        # self.safe_click(driver, By.XPATH, "//a[@class='text-interactive' and text()='Select category']")
        # self.safe_click(driver, By.XPATH, "//div[.//text()[normalize-space()='Women']]//button[contains(text(), 'Select')]")

        # driver.find_element(By.ID, "urlKey").send_keys(url_key)
        # driver.find_element(By.ID, "metaTitle").send_keys(product_name)
        # driver.find_element(By.ID, "qty").send_keys("100")

        # self.safe_click(driver, By.XPATH, "//button[contains(@class, 'button') and contains(@class, 'primary') and .//span[text()='Save']]")

        # success_message = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success, .notification-success, .success-message"))
        # )
        # assert "success" in success_message.text.lower() or "succès" in success_message.text.lower(), "Message de succès non trouvé"

        # # Vérification dans la liste produit
        # driver.get(ADMIN_NEW_PRODUCT_URL.replace("/new", ""))
        # product_name_element = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.XPATH, f"//td[contains(text(), '{product_name}')]"))
        # )
        # assert product_name_element is not None, "Le produit n'a pas été trouvé dans la liste"
