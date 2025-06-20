from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def debug_step(driver, step_name):
    """Fonction utilitaire pour le débogage"""
    print(f"\n=== Étape: {step_name} ===")
    driver.save_screenshot(f"debug_{step_name.lower().replace(' ', '_')}.png")
    time.sleep(2)  # Petite pause pour mieux voir ce qui se passe

# Lancement navigateur chrome
driver = webdriver.Chrome()
driver.maximize_window()

# Accès à ton instance Evershop
driver.get("http://localhost:3000")
wait = WebDriverWait(driver, 20)

try:
    debug_step(driver, "Page d'accueil chargée")

    # Aller sur un produit hh

    print("Recherche du lien produit...")
    product_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.product-name a")))
    debug_step(driver, "Produit trouvé")
    product_link.click()
    
    debug_step(driver, "Page produit chargée")

    # Ajouter au panier
    print("Recherche du bouton Ajouter au panier...")
    add_to_cart_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.button.primary")))
    debug_step(driver, "Bouton Ajouter trouvé")
    add_to_cart_btn.click()
    
    debug_step(driver, "Produit ajouté au panier")

    # Voir le panier
    print("Recherche du lien Voir le panier...")
    view_cart_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/cart']")))
    debug_step(driver, "Bouton Voir panier trouvé")
    view_cart_btn.click()
    
    debug_step(driver, "Page panier chargée")

    # Checkout
    print("Recherche du bouton Checkout...")
    checkout_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/checkout']")))
    debug_step(driver, "Bouton Checkout trouvé")
    checkout_btn.click()
    
    debug_step(driver, "Page checkout chargée")

    # Formulaire client
    print("Remplissage du formulaire client...")
    fields = {
        "email": "test@example.com",
        "firstName": "Test",
        "lastName": "Utilisateur",
        "address": "1 rue de test",
        "city": "Lyon",
        "zip": "69000"
    }
    
    for field, value in fields.items():
        print(f"Remplissage du champ {field}...")
        input_field = wait.until(EC.presence_of_element_located((By.NAME, field)))
        input_field.clear()  # On efface d'abord le champ
        input_field.send_keys(value)
        time.sleep(0.5)  # Petite pause entre chaque champ
    
    debug_step(driver, "Formulaire client rempli")

    # Stripe iframe
    print("Recherche de l'iframe Stripe...")
    iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[name^='__privateStripeFrame']")))
    debug_step(driver, "Iframe Stripe trouvé")
    driver.switch_to.frame(iframe)
    
    # Carte de crédit
    print("Remplissage des informations de carte...")
    card_fields = {
        "cardnumber": "4242424242424242",
        "exp-date": "1230",
        "cvc": "123"
    }
    
    for field, value in card_fields.items():
        print(f"Remplissage du champ {field}...")
        input_field = wait.until(EC.presence_of_element_located((By.NAME, field)))
        input_field.send_keys(value)
        time.sleep(0.5)
    
    debug_step(driver, "Informations de carte remplies")

    # Retour au contenu principal
    driver.switch_to.default_content()
    
    # Confirmation
    print("Recherche du bouton de confirmation...")
    confirm_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
    debug_step(driver, "Bouton de confirmation trouvé")
    confirm_btn.click()
    
    # Vérification finale
    print("Attente du message de succès...")
    confirmation = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".checkout-success-message")))
    debug_step(driver, "Commande confirmée")
    
    print("\n✅ Test réussi : commande passée avec succès!")

except Exception as e:
    print(f"\n❌ Erreur : {str(e)}")
    debug_step(driver, "erreur")
    raise e

finally:
    print("\n🔚 Fermeture du navigateur...")
    driver.quit()

