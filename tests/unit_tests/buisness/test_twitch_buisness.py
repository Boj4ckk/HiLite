import json
from buisness.twitch_buisness import TwitchBuisness


def test_extract_clips_ids():
    clips = [{"id": "abc123", "url": "url1"}, {"id": "def456", "url": "url2"}]
    result = TwitchBuisness.extract_clips_ids(clips)
    assert result == ["abc123", "def456"]


def test_extract_clips_url():
    clips = [{"id": "abc123", "url": "url1"}, {"id": "def456", "url": "url2"}]
    result = TwitchBuisness.extract_clips_url(clips)
    assert result == ["url1", "url2"]


def test_generate_short_title_success(monkeypatch):
    class DummyTwitchApi:
        def get_game_info(self, game_id):
            return {"name": "GameName"}

    # Patch environment variable and file existence
    monkeypatch.setenv("TITLES_TEMPLATE_PATH", "titles_template.json")
    monkeypatch.setattr("os.path.exists", lambda path: True)
    # Patch open and json.load
    dummy_templates = {"templates": ["{broadcaster_name} - {game} - {clip_title}"]}

    def dummy_open(*args, **kwargs):
        from io import StringIO

        return StringIO(json.dumps(dummy_templates))

    monkeypatch.setattr("builtins.open", dummy_open)
    monkeypatch.setattr("json.load", lambda f: dummy_templates)

    clip = {"broadcaster_name": "Streamer", "game_id": "1", "title": "Epic Clip"}
    twitch_service = DummyTwitchApi()
    result = TwitchBuisness.generate_short_title(twitch_service, clip)
    assert result == "Streamer - GameName - Epic Clip"
