from unittest.mock import AsyncMock, Mock, patch

import pytest

from services.twitch_service import TwitchApi


@pytest.mark.asyncio
@patch("services.twitch_service.httpx.AsyncClient")
async def test_get_access_token_success(mock_async_client):
    # Configure le mock de la réponse HTTP
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "token123",
        "expires_in": 5184000,
    }

    # Configure le context manager async
    mock_client_instance = Mock()
    mock_client_instance.post = AsyncMock(return_value=mock_response)
    mock_async_client.return_value.__aenter__.return_value = mock_client_instance

    # Instancie et teste
    api = TwitchApi("client_id", "client_secret")
    token = await api.get_access_token()

    # Assertions
    assert token == "token123"
    assert api._access_token == "token123"
    assert api._token_expiry is not None


@pytest.mark.asyncio
async def test_get_headers():
    api = TwitchApi("client_id", "client_secret")

    # Mock get_access_token directement sur l'instance
    api.get_access_token = AsyncMock(return_value="token123")

    headers = await api.get_headers()

    assert headers["Client-Id"] == "client_id"
    assert headers["Authorization"] == "Bearer token123"


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


@patch("services.twitch_service.requests.get")
def test_download_broadcaster_clips_success(mock_get):
    """Test successful clip download with all parameters."""
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [
            {"id": "clip123", "url": "https://twitch.tv/clip123", "title": "Epic Play"},
            {
                "id": "clip456",
                "url": "https://twitch.tv/clip456",
                "title": "Great Moment",
            },
        ]
    }
    mock_get.return_value = mock_response

    api = TwitchApi(client_id="test_client_id", client_secret="test_secret")

    # Act
    result = api.download_broadcaster_clips(
        editor_id="editor123",
        broadcaster_id="broadcaster456",
        clip_id="clip789",
        user_token="user_token_abc",
    )

    # Assert
    assert len(result) == 2
    assert result[0]["id"] == "clip123"
    assert result[1]["title"] == "Great Moment"

    # Verify the request was made correctly
    mock_get.assert_called_once()
    call_args = mock_get.call_args

    assert call_args.kwargs["headers"]["Client-Id"] == "test_client_id"
    assert call_args.kwargs["headers"]["Authorization"] == "Bearer user_token_abc"
    assert call_args.kwargs["params"]["broadcaster_id"] == "broadcaster456"
    assert call_args.kwargs["params"]["editor_id"] == "editor123"
    assert call_args.kwargs["params"]["clip_id"] == "clip789"
    assert call_args.kwargs["timeout"] == 10
