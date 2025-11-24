import unittest
from unittest.mock import MagicMock, patch
import os
from pathlib import Path
from services.scraping_service import ScrapingService


class TestScrapingService(unittest.TestCase):
    """Unit tests for ScrapingService class with mocked Selenium."""

    @patch.dict(os.environ, {'TWITCH_CLIP_FOLDER_PATH': 'data/twitch_clips'})
    @patch('services.scraping_service.Chrome')
    @patch('services.scraping_service.Path')
    def test_init_success(self, mock_path, mock_chrome):
        """Test successful initialization of ScrapingService."""
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        
        service = ScrapingService()
        
        self.assertIsNotNone(service.driver)
        mock_path_instance.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_chrome.assert_called_once()

    @patch.dict(os.environ, {}, clear=True)
    def test_init_no_env_var(self):
        """Test initialization fails when TWITCH_CLIP_FOLDER_PATH not set."""
        with self.assertRaises(ValueError) as context:
            ScrapingService()
        
        self.assertIn("TWITCH_CLIP_FOLDER_PATH", str(context.exception))

    @patch.dict(os.environ, {'TWITCH_CLIP_FOLDER_PATH': 'data/clips'})
    @patch('services.scraping_service.Chrome')
    @patch('services.scraping_service.Path')
    def test_init_chrome_driver_failure(self, mock_path, mock_chrome):
        """Test initialization fails when Chrome driver fails."""
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_chrome.side_effect = Exception("ChromeDriver not found")
        
        with self.assertRaises(Exception) as context:
            ScrapingService()
        
        self.assertIn("ChromeDriver initialization failed", str(context.exception))

    @patch.dict(os.environ, {'TWITCH_CLIP_FOLDER_PATH': 'data/clips'})
    @patch('services.scraping_service.Chrome')
    @patch('services.scraping_service.Path')
    @patch('services.scraping_service.WebDriverWait')
    def test_accept_cookies_found(self, mock_wait, mock_path, mock_chrome):
        """Test accepting cookies when banner is present."""
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        
        mock_button = MagicMock()
        mock_wait_instance = MagicMock()
        mock_wait_instance.until.return_value = mock_button
        mock_wait.return_value = mock_wait_instance
        
        service = ScrapingService()
        service.accept_cookies()
        
        mock_button.click.assert_called_once()

    @patch.dict(os.environ, {'TWITCH_CLIP_FOLDER_PATH': 'data/clips'})
    @patch('services.scraping_service.Chrome')
    @patch('services.scraping_service.Path')
    @patch('services.scraping_service.WebDriverWait')
    def test_accept_cookies_not_found(self, mock_wait, mock_path, mock_chrome):
        """Test accept_cookies when no banner is present."""
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        
        mock_wait_instance = MagicMock()
        mock_wait_instance.until.side_effect = Exception("Timeout")
        mock_wait.return_value = mock_wait_instance
        
        service = ScrapingService()
        # Should not raise exception
        service.accept_cookies()

    @patch.dict(os.environ, {'TWITCH_CLIP_FOLDER_PATH': 'data/clips'})
    @patch('services.scraping_service.Chrome')
    @patch('services.scraping_service.Path')
    @patch('services.scraping_service.WebDriverWait')
    @patch('services.scraping_service.time.sleep')
    def test_download_clip_success(self, mock_sleep, mock_wait, mock_path, mock_chrome):
        """Test successful clip download."""
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        
        # Mock WebDriverWait for share button and download link
        mock_share_button = MagicMock()
        mock_download_link = MagicMock()
        mock_download_link.get_attribute.return_value = "https://download.link/video.mp4"
        
        mock_wait_instance = MagicMock()
        mock_wait_instance.until.side_effect = [mock_share_button, mock_download_link]
        mock_wait.return_value = mock_wait_instance
        
        service = ScrapingService()
        service.download_clip("https://clips.twitch.tv/test_clip")
        
        mock_driver.get.assert_called_with("https://clips.twitch.tv/test_clip")
        mock_share_button.click.assert_called_once()
        mock_download_link.click.assert_called_once()

    @patch.dict(os.environ, {'TWITCH_CLIP_FOLDER_PATH': 'data/clips'})
    @patch('services.scraping_service.Chrome')
    @patch('services.scraping_service.Path')
    @patch('services.scraping_service.WebDriverWait')
    def test_download_clip_share_button_not_found(self, mock_wait, mock_path, mock_chrome):
        """Test download_clip when share button not found."""
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        
        mock_wait_instance = MagicMock()
        mock_wait_instance.until.side_effect = Exception("Share button timeout")
        mock_wait.return_value = mock_wait_instance
        
        service = ScrapingService()
        
        with self.assertRaises(Exception):
            service.download_clip("https://clips.twitch.tv/test_clip")

    @patch.dict(os.environ, {'TWITCH_CLIP_FOLDER_PATH': 'data/clips'})
    @patch('services.scraping_service.Chrome')
    @patch('services.scraping_service.Path')
    def test_close_driver_success(self, mock_path, mock_chrome):
        """Test closing the driver successfully."""
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        
        service = ScrapingService()
        service.close()
        
        mock_driver.quit.assert_called_once()

    @patch.dict(os.environ, {'TWITCH_CLIP_FOLDER_PATH': 'data/clips'})
    @patch('services.scraping_service.Chrome')
    @patch('services.scraping_service.Path')
    def test_close_driver_error_during_quit(self, mock_path, mock_chrome):
        """Test close handles error during driver.quit()."""
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        
        mock_driver = MagicMock()
        mock_driver.quit.side_effect = Exception("Browser already closed")
        mock_chrome.return_value = mock_driver
        
        service = ScrapingService()
        # Should not raise exception
        service.close()
        
        mock_driver.quit.assert_called_once()

    @patch.dict(os.environ, {'TWITCH_CLIP_FOLDER_PATH': 'data/clips'})
    @patch('services.scraping_service.Chrome')
    @patch('services.scraping_service.Path')
    def test_context_manager_enter(self, mock_path, mock_chrome):
        """Test context manager __enter__."""
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        
        with ScrapingService() as service:
            self.assertIsNotNone(service)
            self.assertIsNotNone(service.driver)

    @patch.dict(os.environ, {'TWITCH_CLIP_FOLDER_PATH': 'data/clips'})
    @patch('services.scraping_service.Chrome')
    @patch('services.scraping_service.Path')
    def test_context_manager_exit(self, mock_path, mock_chrome):
        """Test context manager __exit__ calls close()."""
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        
        with ScrapingService() as service:
            pass
        
        # Verify driver was closed
        mock_driver.quit.assert_called_once()

    @patch.dict(os.environ, {'TWITCH_CLIP_FOLDER_PATH': 'data/clips'})
    @patch('services.scraping_service.Chrome')
    @patch('services.scraping_service.Path')
    @patch('services.scraping_service.WebDriverWait')
    def test_context_manager_exit_with_exception(self, mock_wait, mock_path, mock_chrome):
        """Test context manager __exit__ closes driver even with exception."""
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        
        try:
            with ScrapingService() as service:
                raise ValueError("Test error")
        except ValueError:
            pass
        
        # Verify driver was still closed
        mock_driver.quit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
