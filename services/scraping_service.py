

import os
from undetected_chromedriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pathlib import Path

class ScrapingService:
    def __init__(self):
        options = ChromeOptions()
        # options.add_argument('--headless')  # Enlève le headless pour voir la fenêtre
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        prefs = {
            "download.default_directory": str(Path(os.getenv("TWITCH_CLIP_FOLDER_PATH"))),
            "download.prompt_for_download": False,
            "directory_upgrade": True
        }
        options.add_experimental_option("prefs", prefs)
        self.driver = Chrome(options=options)

    def scraping_service(self):
        self.driver.get("https://google.com")
        try:
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "L2AGLb"))
                ).click()
        except Exception as e:
                print("Bouton 'Tout accepter' non trouvé ou déjà accepté.")

    def close(self):
        self.driver.quit()

   