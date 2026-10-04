import pytest

from yt_script import channel
from yt_script.channel import (
    Video,
    channel_url,
    find_video,
    latest_videos,
    normalize_title,
    resolve_channel,
    title_score,
)
from yt_script.errors import YtScriptError

BASE = "https://www.youtube.com/@KarstenRunquist"
TITLE = "Resident Evil: How To Adapt a Video Game in 2026"


def entry(video_id, title):
    return {"id": video_id, "title": title, "url": f"https://www.youtube.com/watch?v={video_id}"}


UPLOADS = [
    entry("aaaaaaaaaa1", "Why Every Movie Looks The Same"),
    entry("aaaaaaaaaa2", TITLE),
    entry("aaaaaaaaaa3", "The Problem With Sequels"),
    entry("aaaaaaaaaa4", "Resident Evil: The Final Chapter Review"),
]


@pytest.fixture
def fake_youtube(monkeypatch):
    """Serve listings from a dict of URL -> entries; record the requests made."""
    pages = {}
    calls = []

    def fake_entries(url, limit, proxy=None):
        calls.append((url, limit))
        if url not in pages:
            raise YtScriptError(f"Could not read {url}: HTTP Error 404")
        return pages[url][:limit]

    monkeypatch.setattr(channel, "_playlist_entries", fake_entries)
    return pages, calls


@pytest.mark.parametrize(
    "given",
    [
        "https://www.youtube.com/@KarstenRunquist",
        "https://www.youtube.com/@KarstenRunquist/videos",
        "https://m.youtube.com/@KarstenRunquist/",
        "youtube.com/@KarstenRunquist",
        "  @KarstenRunquist  ",
    ],
)
def test_channel_url_handles(given):
    assert channel_url(given) == BASE


@pytest.mark.parametrize(
    "given, expected",
    [
        ("UCabcdefghijklmnopqrstuv", "https://www.youtube.com/channel/UCabcdefghijklmnopqrstuv"),
        (
            "https://www.youtube.com/channel/UCabcdefghijklmnopqrstuv/streams",
            "https://www.youtube.com/channel/UCabcdefghijklmnopqrstuv",
        ),
        ("https://www.youtube.com/c/SomeName/about", "https://www.youtube.com/c/SomeName"),
        ("https://youtube.com/user/somename", "https://www.youtube.com/user/somename"),
    ],
)
def test_channel_url_other_forms(given, expected):
    assert channel_url(given) == expected


@pytest.mark.parametrize("given", ["Karsten Runquist", "KarstenRunquist", ""])
def test_channel_url_needs_lookup_for_names(given):
    assert channel_url(given) is None


@pytest.mark.parametrize(
    "given", ["https://www.youtube.com/watch?v=aaaaaaaaaa1", "https://youtu.be/aaaaaaaaaa1"]
)
def test_channel_url_rejects_video_links(given):
    with pytest.raises(YtScriptError):
        channel_url(given)


def test_resolve_channel_tries_bare_word_as_handle(fake_youtube):
    pages, _ = fake_youtube
    pages[f"{BASE}/videos"] = UPLOADS
    assert resolve_channel("KarstenRunquist") == BASE


def test_resolve_channel_searches_by_name(fake_youtube):
    pages, calls = fake_youtube
    search = "https://www.youtube.com/results?search_query=Karsten+Runquist&sp=EgIQAg%253D%253D"
    pages[search] = [
        {
            "_type": "url",
            "id": "UCabcdefghijklmnopqrstuv",
            "url": "https://www.youtube.com/channel/UCabcdefghijklmnopqrstuv",
            "title": "Karsten Runquist",
        }
    ]
    assert resolve_channel("Karsten Runquist") == (
        "https://www.youtube.com/channel/UCabcdefghijklmnopqrstuv"
    )
    assert [url for url, _ in calls] == [search]


def test_resolve_channel_not_found(fake_youtube):
    pages, _ = fake_youtube
    name = "No Such Channel Anywhere"
    pages["https://www.youtube.com/results?search_query=No+Such+Channel+Anywhere&sp=EgIQAg%253D%253D"] = []
    with pytest.raises(YtScriptError, match="No YouTube channel found"):
        resolve_channel(name)


def test_latest_videos_returns_newest_first(fake_youtube):
    pages, calls = fake_youtube
    pages[f"{BASE}/videos"] = UPLOADS
    videos = latest_videos(BASE, 2)
    assert videos == [Video("aaaaaaaaaa1", UPLOADS[0]["title"]), Video("aaaaaaaaaa2", TITLE)]
    assert calls == [(f"{BASE}/videos", 2)]


def test_latest_videos_empty_channel(fake_youtube):
    pages, _ = fake_youtube
    pages[f"{BASE}/videos"] = []
    with pytest.raises(YtScriptError, match="No videos found"):
        latest_videos(BASE, 1)


def test_normalize_title():
    assert normalize_title("  Résident  EVIL: How-To!  ") == "resident evil how to"


def test_title_score_ranks_exact_and_partial_titles():
    assert title_score(TITLE, TITLE) == 1.0
    assert title_score("resident evil how to adapt a video game in 2026", TITLE) == 1.0
    assert title_score("How To Adapt a Video Game", TITLE) >= 0.9
    assert title_score("Resident Evil - how to adapt a videogame", TITLE) > 0.6
    assert title_score(TITLE, "The Problem With Sequels") < 0.6


def test_find_video_uses_channel_search_first(fake_youtube):
    pages, calls = fake_youtube
    search = f"{BASE}/search?query=Resident+Evil%3A+How+To+Adapt+a+Video+Game+in+2026"
    # The channel search lists the closest title first and can include playlists.
    pages[search] = [
        UPLOADS[3],
        {"id": "PLxxxxxxxxxxxxxxxx", "title": TITLE, "url": "https://www.youtube.com/playlist"},
        UPLOADS[1],
    ]
    assert find_video(BASE, TITLE) == Video("aaaaaaaaaa2", TITLE)
    assert [url for url, _ in calls] == [search]


def test_find_video_falls_back_to_scanning_uploads(fake_youtube):
    pages, calls = fake_youtube
    pages[f"{BASE}/videos"] = UPLOADS  # The channel search is unavailable (404).
    assert find_video(BASE, "how to adapt a video game", search_depth=50).id == "aaaaaaaaaa2"
    assert calls[-1] == (f"{BASE}/videos", 50)


def test_find_video_reports_closest_titles(fake_youtube):
    pages, _ = fake_youtube
    pages[f"{BASE}/videos"] = UPLOADS
    with pytest.raises(YtScriptError) as error:
        find_video(BASE, "Resident Evil Village Analysis")
    assert "No video titled" in str(error.value)
    assert "Resident Evil: The Final Chapter Review" in str(error.value)
