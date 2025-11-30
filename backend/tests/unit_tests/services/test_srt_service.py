import os
from unittest.mock import MagicMock, patch

import pytest

from src.services.srt_service import SrtService


def test_init_sets_output_file(monkeypatch):
    monkeypatch.setattr(
        "src.services.srt_service.settings.SRT_DIR_PATH",
        "./tmp/srt_test",
        raising=False,
    )
    service = SrtService("output.srt")
    expected_path = os.path.normpath("tmp/srt_test/output.srt")
    assert expected_path in os.path.normpath(service.srt_output_file)


@patch("builtins.open", new_callable=MagicMock)
@patch("src.services.srt_service.SrtBuisness.transcription_to_srt_lines")
def test_convert_transcription_into_srt_success(mock_lines, mock_open, monkeypatch):
    monkeypatch.setattr(
        "src.services.srt_service.settings.SRT_DIR_PATH",
        "./tmp/srt_test",
        raising=False,
    )
    mock_lines.return_value = ["1\n00:00:01,000 --> 00:00:02,000\nHello world"]
    mock_transcription = MagicMock()
    mock_transcription.words = [MagicMock()]
    service = SrtService("output.srt")
    result = service.convert_transcription_into_srt(mock_transcription)
    expected_path = os.path.normpath(result)
    assert expected_path in os.path.normpath(service.srt_output_file)
    mock_open.assert_called_once_with(service.srt_output_file, "w", encoding="utf-8")


@patch("builtins.open", new_callable=MagicMock)
@patch(
    "src.services.srt_service.SrtBuisness.transcription_to_srt_lines",
    side_effect=Exception("fail"),
)
def test_convert_transcription_into_srt_failure(mock_lines, mock_open, monkeypatch):
    monkeypatch.setattr(
        "src.services.srt_service.settings.SRT_DIR_PATH",
        "./tmp/srt_test",
        raising=False,
    )
    mock_transcription = MagicMock()
    mock_transcription.words = [MagicMock()]
    service = SrtService("output.srt")
    with pytest.raises(Exception):
        service.convert_transcription_into_srt(mock_transcription)
