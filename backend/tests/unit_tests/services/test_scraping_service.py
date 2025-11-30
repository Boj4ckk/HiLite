from unittest.mock import MagicMock, patch

import pytest

from src.services.scraping_service import ScrapingService


def test_init_success(monkeypatch):
    monkeypatch.setattr(
        "src.services.scraping_service.settings.TWITCH_CLIP_FOLDER_PATH",
        "./tmp/test_clips",
        raising=False,
    )
    with patch("src.services.scraping_service.Chrome") as mock_chrome:
        with patch("src.services.scraping_service.ChromeOptions"):
            with patch("pathlib.Path.mkdir") as mock_mkdir:
                service = ScrapingService()
                assert hasattr(service, "driver")
                mock_chrome.assert_called_once()
                mock_mkdir.assert_called()


def test_init_no_env(monkeypatch):
    monkeypatch.setattr(
        "src.services.scraping_service.settings.TWITCH_CLIP_FOLDER_PATH",
        "",
        raising=False,
    )
    with patch("src.services.scraping_service.ChromeOptions"):
        with patch("src.services.scraping_service.Chrome"):
            with pytest.raises(ValueError) as excinfo:
                ScrapingService()
            assert "TWITCH_CLIP_FOLDER_PATH environment variable is not set" in str(
                excinfo.value
            )


def test_close_success(monkeypatch):
    monkeypatch.setattr(
        "src.services.scraping_service.settings.TWITCH_CLIP_FOLDER_PATH",
        "./tmp/test_clips",
        raising=False,
    )
    with patch("src.services.scraping_service.Chrome"):
        with patch("src.services.scraping_service.ChromeOptions"):
            with patch("pathlib.Path.mkdir"):
                service = ScrapingService()
                service.driver = MagicMock()
                service.close()
                service.driver.quit.assert_called_once()


def test_context_manager(monkeypatch):
    monkeypatch.setattr(
        "src.services.scraping_service.settings.TWITCH_CLIP_FOLDER_PATH",
        "./tmp/test_clips",
        raising=False,
    )
    with patch("src.services.scraping_service.Chrome"):
        with patch("src.services.scraping_service.ChromeOptions"):
            with patch("pathlib.Path.mkdir"):
                with ScrapingService() as service:
                    assert hasattr(service, "driver")
