

import os
import time
import logging
from undetected_chromedriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path

logger = logging.getLogger("HiLiteLogger")

class ScrapingService:
    """
    Service for web scraping operations using Selenium and undetected ChromeDriver.
    Handles Twitch clip downloads with automated browser interactions.
    """
    
    def __init__(self):
        """
        Initialize Chrome driver with download preferences for Twitch clips.
        """
        options = ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        
        # Convert relative path to absolute path
        download_dir = Path(os.getenv("TWITCH_CLIP_FOLDER_PATH")).resolve()
        download_dir.mkdir(parents=True, exist_ok=True)
        
        prefs = {
            "download.default_directory": str(download_dir),
            "download.prompt_for_download": False,
            "directory_upgrade": True
        }
        options.add_experimental_option("prefs", prefs)
        self.driver = Chrome(options=options)
        logger.info(f"Scraping service initialized. Download directory: {download_dir}")

    def accept_cookies(self):
        """
        Accept cookie consent banner if it appears on the page.
        """
        try:
            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'consent-banner') or contains(text(), 'Accept') or contains(text(), 'Accepter') or contains(text(), 'Tout accepter')]"))
            ).click()
            logger.info("Cookie consent accepted.")
        except Exception:
            logger.info("No cookie consent popup found or already accepted.")
    
    def download_clip(self, clip_url):
        """
        Download a Twitch clip by navigating to the URL and clicking download link.
        
        :param clip_url: Full URL of the Twitch clip to download.
        """
        logger.info(f"Starting clip download from: {clip_url}")
        self.driver.get(clip_url)
        
        try:
            # Accept cookies if needed
            self.accept_cookies()
            
            # Click the 'Share' button (supports both French and English)
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[.//div[contains(text(), 'Partager') or contains(text(), 'Share')]]"))
            ).click()
            logger.info("Share button clicked successfully.")
            
            # Click the 'Download portrait version' link (supports both French and English)
            download_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'tw-interactable') and (.//div[contains(text(), 'version portrait')] or .//div[contains(text(), 'portrait version')])]"))
            )
            download_url = download_link.get_attribute("href")
            logger.info(f"Download link found: {download_url}")
            download_link.click()
            logger.info("Download started successfully.")
            
            # Wait for download to complete
            time.sleep(10)
            
        except Exception as e:
            logger.error(f"Failed to download clip from {clip_url}: {e}")
            raise
    
    def close(self):
        """
        Close the browser and clean up driver resources.
        """
        try:
            self.driver.quit()
            logger.info("Scraping service closed.")
        except Exception as e:
            logger.warning(f"Error while closing driver: {e}")

   