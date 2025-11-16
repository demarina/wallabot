import os.path

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from utils.mongo_db import MongoDB
from src.trainer.ner import Ner

OFFERS_URL = (
    'https://es.wallapop.com/search?'
    'distance_in_km=50&time_filter=lastMonth&min_sale_price=500&max_sale_price=2000&'
    'keywords=bicicleta+orbea&order_by=price_high_to_low&source=side_bar_filters'
)
COLLECTION_NAME = 'walla_bikes'


def main():
    # Configuración del navegador (sin mensajes molestos)
    chrome_options = Options()
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--start-maximized')

    nlp_model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'trainer', 'data')
    walla_ner = Ner(nlp_model_path=nlp_model_path)
    mongo_cli = MongoDB(host='localhost', port='27017', db_name='wallabot', user='admin', password='admin123')

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
        print('Cookies aceptadas.')
    except TimeoutException:
        print('No apareció el banner de cookies (puede que ya estuviera aceptado).')

    # --- Esperar a que se carguen las tarjetas ---
    try:
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'item-card_ItemCard--vertical__CNrfk')))
        cards = driver.find_elements(By.CLASS_NAME, 'item-card_ItemCard--vertical__CNrfk')
        print(f'Se encontraron {len(cards)} productos.')
    except TimeoutException:
        print('No se cargaron productos.')
        driver.quit()
        return

    for e in cards:
        try:
            title = e.find_element(By.CLASS_NAME, 'item-card_ItemCard__title__5TocV').text
            price = e.find_element(By.CLASS_NAME, 'item-card_ItemCard__price__pVpdc').text
            link = e.tag_name == 'a' and e.get_attribute('href') or e.find_element(By.TAG_NAME, 'a').get_attribute(
                'href')
            id = link.split('-')[-1]

            try:
                features = walla_ner.predict(query=title)
            except Exception as e:
                raise ValueError(f'Error predicting features in title "{title}": {e}')

            print(f'{title} | {price} | {features}')

            bike_info = {
                'title': title,
                'price': price,
                'link': link,
                'features': features,
                'id': id
            }

            try:
                mongo_cli.insert(coll_name=COLLECTION_NAME, data=bike_info)
            except Exception as e:
                raise ValueError(f'Error inserting element "{bike_info}" in db: {e}')

        except Exception as e:
            print(f'Error processing card: {e}')
            continue

    print('Scraping finish')
    driver.quit()


if __name__ == '__main__':
    main()
