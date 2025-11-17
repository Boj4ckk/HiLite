
import time
from services.scraping_service import ScrapingService
class ScrapingBuisness:
    def __init__(self, scraping_service: ScrapingService):
        self.scraping_service = scraping_service

    def dowload_clip(self, clip_url):
        self.scraping_service.driver.get(clip_url)
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.by import By
            WebDriverWait(self.scraping_service.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[div//div[text()='Partager']]") )
            ).click()
            print("Bouton 'Partager' cliqué.")
            # Wait for the 'Télécharger la version portrait' link to appear and click it
            download_link = WebDriverWait(self.scraping_service.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'tw-interactable') and .//div[text()='Télécharger la version portrait']]") )
            )
            print("Lien de téléchargement trouvé :", download_link.get_attribute("href"))
            download_link.click()
            print("Lien 'Télécharger la version portrait' cliqué.")
        except Exception:
            print("Bouton 'Partager' non trouvé.")
        time.sleep(20)
        self.scraping_service.close()



