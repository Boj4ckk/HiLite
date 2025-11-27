import logging
import os
import time
import uuid
from pathlib import Path

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from undetected_chromedriver import Chrome, ChromeOptions

from config.path_config import BASE_DIR
from config.settings import settings

logger = logging.getLogger("HiLiteLogger")


class ScrapingService:
    """
    Service for web scraping operations using Selenium and undetected ChromeDriver.
    Handles Twitch clip downloads with automated browser interactions.
    """

    def __init__(self):
        """
        Initialize Chrome driver with download preferences for Twitch clips.

        Raises:
            ValueError: If TWITCH_CLIP_FOLDER_PATH is not set
            Exception: If ChromeDriver fails to initialize
        """
        clip_folder_path = settings.TWITCH_CLIP_FOLDER_PATH
        if not clip_folder_path:
            raise ValueError("TWITCH_CLIP_FOLDER_PATH environment variable is not set")

        try:
            options = ChromeOptions()
            options.binary_location = "/usr/bin/chromium"  # comment if not in container
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-software-rasterizer")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-setuid-sandbox")
            options.add_argument("--single-process")  # Important pour Docker
            options.add_argument("--window-size=1920,1080")

            # Forcer le profil Chrome dans un dossier accessible
            profile_dir = os.path.join("/tmp", "chrome_profile")
            logger.info(f"{profile_dir}")
            Path(profile_dir).mkdir(parents=True, exist_ok=True)
            options.add_argument(f"--user-data-dir={profile_dir}")

            # Chemin absolu à partir de la racine du projet
            download_dir = Path(os.path.join(BASE_DIR, clip_folder_path))
            logger.info(f"this is {download_dir}")
            download_dir.mkdir(parents=True, exist_ok=True)
            self.download_dir = download_dir

            prefs = {
                "download.default_directory": str(download_dir),
                "download.prompt_for_download": False,
                "directory_upgrade": True,
            }
            options.add_experimental_option("prefs", prefs)

            logger.info("Initializing Chrome driver...")
            self.driver = Chrome(options=options)
            logger.info(
                f"Scraping service initialized. Download directory: {download_dir}"
            )

        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            raise Exception(f"ChromeDriver initialization failed: {e}") from e

    def accept_cookies(self):
        """
        Accept cookie consent banner if it appears on the page.
        """
        try:
            WebDriverWait(self.driver, 5).until(
                ec.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[contains(@class, 'consent-banner') or contains(text(), 'Accept') or contains(text(), 'Accepter') or contains(text(), 'Tout accepter')]",
                    )
                )
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
                ec.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[.//div[contains(text(), 'Partager') or contains(text(), 'Share')]]",
                    )
                )
            ).click()
            logger.info("Share button clicked successfully.")

            # Click the 'Download portrait version' link (supports both French and English)
            def wait_for_download_file(download_dir: Path, timeout=180):
                """
                Wait for download to complete by checking for .crdownload files.

                Args:
                    download_dir: Directory where file is being downloaded
                    timeout: Maximum time to wait in seconds

                Returns:
                    List of downloaded .mp4 files

                Raises:
                    TimeoutError: If download doesn't complete in time
                """
                end_time = time.time() + timeout
                logger.info(f"Waiting for download in {download_dir}...")

                # Phase 1: Wait for download to START (crdownload appears)
                download_started = False
                start_wait_time = time.time()
                while time.time() < end_time and (time.time() - start_wait_time) < 30:
                    files = list(download_dir.glob("*"))
                    if any(f.name.endswith(".crdownload") for f in files):
                        download_started = True
                        logger.info("Download started (.crdownload file detected)")
                        break
                    time.sleep(0.5)

                if not download_started:
                    logger.warning(
                        "Download may not have started (no .crdownload found)"
                    )

                # Phase 2: Wait for download to COMPLETE (crdownload disappears)
                while time.time() < end_time:
                    files = list(download_dir.glob("*"))
                    crdownload_files = [
                        f for f in files if f.name.endswith(".crdownload")
                    ]
                    mp4_files = [f for f in files if f.name.endswith(".mp4")]

                    # Log progress
                    if crdownload_files:
                        logger.debug(
                            f"Download in progress: {crdownload_files[0].name}"
                        )

                    # Download complete when:
                    # 1. No more .crdownload files
                    # 2. At least one .mp4 file exists
                    if not crdownload_files and mp4_files:
                        logger.info(f"Download completed: {mp4_files[0].name}")
                        # Wait a bit more for file system to stabilize
                        time.sleep(2)
                        return mp4_files

                    time.sleep(1)  # Check every second

                # Timeout - log what we found
                all_files = list(download_dir.glob("*"))
                logger.error(
                    f"Download timeout after {timeout}s. Files in directory: {[f.name for f in all_files]}"
                )
                raise TimeoutError(f"Download did not complete after {timeout}s")

            try:
                # fallback xpaths (original xpath + useful fallbacks)
                xpaths = [
                    "//a[contains(@class,'tw-interactable') and contains(., 'version portrait')]",
                    "//a[contains(@class,'tw-interactable') and contains(., 'Télécharger la version portrait')]",
                    "//a[contains(@href,'production.assets.clips.twitchcdn.net')]",
                ]

                download_link = None
                used_xp = None
                for xp in xpaths:
                    try:
                        download_link = WebDriverWait(self.driver, 6).until(
                            ec.element_to_be_clickable((By.XPATH, xp))
                        )
                        used_xp = xp
                        logger.info(f"Found download element with xpath: {xp}")
                        break
                    except TimeoutException:
                        logger.debug(f"No element for xpath: {xp}")

                if not download_link:
                    uid = uuid.uuid4().hex
                    try:
                        self.driver.save_screenshot(f"/tmp/screen_{uid}.png")
                        open(
                            f"/tmp/pagesource_{uid}.html", "w", encoding="utf-8"
                        ).write(self.driver.page_source)
                        logger.warning(
                            f"Download link not found; saved /tmp/screen_{uid}.png and /tmp/pagesource_{uid}.html"
                        )
                    except Exception:
                        logger.exception("Failed to save debug artifacts")
                    raise TimeoutException("Download link not found")

                # get href robustly
                try:
                    download_url = download_link.get_attribute(
                        "href"
                    ) or download_link.get_property("href")
                except StaleElementReferenceException:
                    # refetch then read
                    download_link = self.driver.find_element(By.XPATH, used_xp)
                    download_url = download_link.get_attribute(
                        "href"
                    ) or download_link.get_property("href")

                # final fallback with JS if still None
                if not download_url:
                    try:
                        download_url = self.driver.execute_script(
                            "return arguments[0].getAttribute('href') || arguments[0].href;",
                            download_link,
                        )
                    except Exception:
                        download_url = None

                logger.info(f"download_url: {download_url}")
                logger.debug(
                    f"element outerHTML: {download_link.get_attribute('outerHTML')[:1000]}"
                )

                # click with retries and JS fallback
                attempts = 3
                for i in range(attempts):
                    try:
                        self.driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'center'});",
                            download_link,
                        )
                        download_link.click()
                        logger.info("Clicked download link (normal click).")
                        break
                    except (
                        StaleElementReferenceException,
                        ElementClickInterceptedException,
                    ) as e:
                        logger.warning(
                            f"Click attempt {i + 1} failed: {e}; retrying with JS click"
                        )
                        try:
                            download_link = self.driver.find_element(By.XPATH, used_xp)
                            self.driver.execute_script(
                                "arguments[0].click();", download_link
                            )
                            logger.info("Clicked download link via JS fallback.")
                            break
                        except Exception as e2:
                            logger.warning(f"JS click fallback failed: {e2}")
                            if i == attempts - 1:
                                raise

                # wait for actual file
                try:
                    files = wait_for_download_file(self.download_dir, timeout=60)
                    logger.info(f"Download finished: {files}")
                except TimeoutError as e:
                    logger.warning(f"Download watch timeout: {e}")
                    raise

            except Exception as e:
                logger.error(f"Failed at download link handling: {e}")
                raise

        except Exception as e:
            logger.error(f"Failed to download clip from {clip_url}: {e}")
            raise

    def close(self):
        """
        Close the browser and clean up driver resources.
        Guaranteed to close the driver even if errors occur.
        """
        if hasattr(self, "driver") and self.driver:
            try:
                self.driver.quit()
                logger.info("Scraping service closed successfully.")
            except Exception as e:
                logger.error(f"Error while closing driver: {e}")
                # Force close anyway
                try:
                    self.driver.close()
                except Exception:
                    pass
        else:
            logger.warning("Driver was not initialized, nothing to close")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures driver is closed."""
        self.close()
        return False
