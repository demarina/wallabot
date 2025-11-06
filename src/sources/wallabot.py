from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

OFFERS_URL = (
    "https://es.wallapop.com/search?"
    "distance_in_km=50&time_filter=lastMonth&min_sale_price=500&max_sale_price=2000&"
    "keywords=bicicleta+orbea&order_by=price_high_to_low&source=side_bar_filters"
)


def main():
    # Configuración del navegador (sin mensajes molestos)
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--start-maximized")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    driver.get(OFFERS_URL)

    wait = WebDriverWait(driver, 10)

    # --- Aceptar cookies ---
    try:
        accept_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@id,'onetrust-accept-btn-handler')]"))
        )
        accept_button.click()
        print("✅ Cookies aceptadas.")
    except TimeoutException:
        print("⚠️ No apareció el banner de cookies (puede que ya estuviera aceptado).")

    # --- Esperar a que se carguen las tarjetas ---
    try:
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "item-card_ItemCard--vertical__CNrfk")))
        cards = driver.find_elements(By.CLASS_NAME, "item-card_ItemCard--vertical__CNrfk")
        print(f"✅ Se encontraron {len(cards)} productos.")
    except TimeoutException:
        print("❌ No se cargaron productos.")
        driver.quit()
        return

    print("\n🟢 Buenos días Argonauta, estas son tus ofertas para hoy:\n")

    for e in cards:
        try:
            titulo = e.find_element(By.CLASS_NAME, "item-card_ItemCard__title__5TocV").text
            precio = e.find_element(By.CLASS_NAME, "item-card_ItemCard__price__pVpdc").text
            enlace = e.tag_name == "a" and e.get_attribute("href") or e.find_element(By.TAG_NAME, "a").get_attribute("href")
            
            print(f"- 🚲 {titulo} | 💰 {precio} | 🔗 {enlace}")

        except Exception as err:
            print(f"Error procesando una tarjeta: {err}")
            continue

    print("\n✅ Fin del scraping.")
    driver.quit()


if __name__ == "__main__":
    main()