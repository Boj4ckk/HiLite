import pytest
from unittest.mock import patch
from services.twitch_service import TwitchApi


@patch("services.twitch_service.requests.post")
def test_authenticate_success(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"access_token": "token123"}
    api = TwitchApi("id", "secret")
    assert api.accessToken == "token123"
    assert api.headers["Authorization"] == "Bearer token123"


@patch("services.twitch_service.requests.post")
def test_authenticate_failure(mock_post):
    mock_post.return_value.status_code = 400
    mock_post.return_value.json.return_value = {}
    mock_post.return_value.raise_for_status.side_effect = Exception("fail")
    with pytest.raises(Exception):
        TwitchApi("id", "secret")


@patch("services.twitch_service.requests.post")
@patch.dict("os.environ", {"BASE_URL": "http://test"})
@patch("services.twitch_service.requests.get")
def test_get_broadcaster_id_success(mock_get, mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"access_token": "token123"}
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"data": [{"id": "broadcaster123"}]}
    api = TwitchApi("id", "secret")
    result = api.get_broadcaster_id("user")
    assert result == "broadcaster123"


@patch("services.twitch_service.requests.post")
@patch.dict("os.environ", {"BASE_URL": "http://test"})
@patch("services.twitch_service.requests.get")
def test_get_broadcaster_id_not_found(mock_get, mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"access_token": "token123"}
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"data": []}
    api = TwitchApi("id", "secret")
    result = api.get_broadcaster_id("user")
    assert result is None


@patch("services.twitch_service.requests.post")
@patch.dict("os.environ", {"BASE_URL": "http://test"})
@patch("services.twitch_service.requests.get")
def test_get_broadcaster_clips_success(mock_get, mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"access_token": "token123"}
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "data": [{"id": "clip1"}, {"id": "clip2"}]
    }
    api = TwitchApi("id", "secret")
    result = api.get_broadcaster_clips("broadcaster123")
    assert isinstance(result, list)


@patch("services.twitch_service.requests.post")
@patch.dict("os.environ", {"BASE_URL": "http://test"})
@patch("services.twitch_service.requests.get")
def test_get_game_info_success(mock_get, mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"access_token": "token123"}
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "data": [{"id": "game1", "name": "GameName"}]
    }
    api = TwitchApi("id", "secret")
    result = api.get_game_info("game1")
    assert result["name"] == "GameName"


@patch("services.twitch_service.requests.post")
@patch.dict("os.environ", {"BASE_URL": "http://test"})
@patch("services.twitch_service.requests.get")
def test_download_clips_success(mock_get, mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"access_token": "token123"}
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"data": ["clipdata"]}
    api = TwitchApi("id", "secret")
    result = api.download_clips("broadcaster123", "clipid123")
    assert result == ["clipdata"]
