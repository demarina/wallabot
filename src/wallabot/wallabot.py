import os.path
import time

import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from utils.mongo_db import MongoDB
from src.trainer.ner import Ner

from openai import OpenAI

OFFERS_URL = (
    'https://es.wallapop.com/search?'
    'distance_in_km=50&time_filter=lastMonth&min_sale_price=500&max_sale_price=2000&'
    'keywords=bicicleta+orbea&order_by=price_high_to_low&source=side_bar_filters'
)
COLLECTION_NAME = 'walla_bikes'
DOWNLOAD_IMAGES_FOLDER_PATH = ''  # COMPLETE
DEEP_SEEK_API_KEY = 'sk-a0283572fde3497ca8ca12e6ee8daf0c'

client = OpenAI(
    api_key=DEEP_SEEK_API_KEY,
    base_url='https://api.deepseek.com/v1'
)


def chat_with_deepseek(description: str) -> str:
    try:
        response = client.chat.completions.create(
            model='deepseek-chat',
            messages=[
                {'role': 'system', 'content': 'Eres un asistente experto en crear anuncios para bicicletas.'},
                {'role': 'user', 'content': f'Reformula el siguiente anuncio de manera concisa: {description}'}
            ],
            stream=False
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f'Error calling Deepseek api: {e}')

    return ''


def main():
    chrome_options = Options()
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--start-maximized')

    nlp_model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'trainer', 'data', 'bikes')
    walla_ner = Ner(nlp_model_path=nlp_model_path)
    mongo_cli = MongoDB(host='localhost', port='27017', db_name='wallabot', user='admin', password='admin123')

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    driver.get(OFFERS_URL)

    wait = WebDriverWait(driver, 10)
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
        link = e.tag_name == 'a' and e.get_attribute('href') or e.find_element(
            By.TAG_NAME, 'a').get_attribute('href')
        try:
            title = e.find_element(By.CLASS_NAME, 'item-card_ItemCard__title__5TocV').text
            price = e.find_element(By.CLASS_NAME, 'item-card_ItemCard__price__pVpdc').text
            id = link.split('-')[-1]

            driver.execute_script(f"window.open('{link}', '_blank');")
            tabs = driver.window_handles
            driver.switch_to.window(tabs[1])
            time.sleep(1)

            complete_bike = driver.find_element(
                By.CLASS_NAME, 'item-detail_ItemDetailTwoColumns__container__aOiE5')
            last_updated = complete_bike.find_element(
                By.CLASS_NAME, 'item-detail-stats_ItemDetailStats__description__015I3').text
            views = complete_bike.find_element(By.CLASS_NAME, 'item-detail-stats_ItemDetailStats__ORKSL')
            views_text = views.find_element(By.CLASS_NAME, 'd-flex').text
            description = complete_bike.find_element(
                By.CLASS_NAME, 'item-detail_ItemDetailTwoColumns__description__0DKb0').text
            elemets = complete_bike.find_elements(
                By.CLASS_NAME, 'item-detail-location_ItemDetailLocation__link__OmVsa'
            )
            location = elemets[0].text if elemets else None
            state = complete_bike.find_element(
                By.CLASS_NAME, 'item-detail-characteristics_ItemDetailCharacteristics__container__MDLJk').text
            images_name = []

            # Download images
            try:
                div_images = driver.find_element(By.CLASS_NAME, 'wallapop-carousel--rounded')
                imgs = div_images.find_elements(By.TAG_NAME, "img")
                for i, img in enumerate(imgs):
                    url = img.get_attribute('src')

                    extension = 'png'
                    if '.jpg' in url:
                        extension = 'jpg'

                    name = f'{title.replace(" ", "_")}_{i}.{extension}'
                    print(f'Downloading image {name} from url')

                    response = requests.get(url)
                    if response.status_code == 200:
                        with open(name, 'wb') as f:
                            f.write(response.content)
                        images_name.append(name)

                    else:
                        print(f'Error downloading image {name}')

            except Exception as e:
                print(f'Error getting images {e}')

            driver.close()  # close tab
            driver.switch_to.window(tabs[0])
            time.sleep(1)

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
                'id': id,
                'last_updated': last_updated,
                'views': views_text,
                'description': description,
                'location': location,
                'state': state,
                'images': images_name,
                'new_description': chat_with_deepseek(description=description)
            }

            try:
                mongo_cli.insert(coll_name=COLLECTION_NAME, data=bike_info)
            except Exception as e:
                raise ValueError(f'Error inserting element "{bike_info}" in db: {e}')

        except NoSuchElementException as e:
            print(f'Element not fount {e}, in bike {link}.')
            continue
        except Exception as e:
            print(f'Error processing card: {e}, in bike {link}.')
            continue

    print('Scraping finish')
    driver.quit()


if __name__ == '__main__':
    main()
