"""Resolve a YouTube channel and find its videos, using yt-dlp."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
from urllib.parse import quote, quote_plus, urlparse

import yt_dlp

from .errors import YtScriptError

YOUTUBE = "https://www.youtube.com"

# A channel ID is "UC" followed by 22 URL-safe base64 characters.
_CHANNEL_ID_RE = re.compile(r"UC[\w-]{22}")
# Handles are 3-30 letters, digits, underscores, hyphens or periods.
_HANDLE_RE = re.compile(r"@?[\w.-]{3,30}")
# The part of a channel URL's path that identifies the channel; the rest is a tab.
_CHANNEL_PATH_RE = re.compile(r"/(@[^/]+|channel/[^/]+|c/[^/]+|user/[^/]+)")
_VIDEO_ID_RE = re.compile(r"[\w-]{11}")
# YouTube's "Channels" filter for search results.
_CHANNEL_FILTER = "EgIQAg%253D%253D"

# Minimum similarity for a title to count as a match.
MATCH_THRESHOLD = 0.6


@dataclass
class Video:
    id: str
    title: str

    @property
    def url(self) -> str:
        return f"{YOUTUBE}/watch?v={self.id}"


@dataclass
class TitleMatch:
    video: Video
    score: float


def channel_url(channel: str) -> str | None:
    """Return the base URL for a channel URL, @handle or channel ID.

    Returns None for anything else (a plain name such as "Karsten Runquist"),
    which has to be looked up with a search.
    """
    text = channel.strip()
    if "youtube.com" in text or "youtu.be" in text:
        parsed = urlparse(text if "://" in text else f"https://{text}")
        host = parsed.hostname or ""
        match = _CHANNEL_PATH_RE.match(parsed.path)
        if not host.endswith("youtube.com") or not match:
            raise YtScriptError(f"Not a YouTube channel URL: {channel}")
        return f"{YOUTUBE}/{match.group(1)}"
    if _CHANNEL_ID_RE.fullmatch(text):
        return f"{YOUTUBE}/channel/{text}"
    if text.startswith("@") and _HANDLE_RE.fullmatch(text):
        return f"{YOUTUBE}/{quote(text, safe='@')}"
    return None


class _SilentLogger:
    """Keeps yt-dlp quiet; its errors are raised and reported by this tool instead."""

    def debug(self, message: str) -> None:
        pass

    info = warning = error = debug


def _playlist_entries(url: str, limit: int, proxy: str | None = None) -> list[dict]:
    """List the entries of a YouTube channel tab or search page without downloading."""
    options = {
        "quiet": True,
        "no_warnings": True,
        "logger": _SilentLogger(),
        "skip_download": True,
        "extract_flat": "in_playlist",
        "playlistend": limit,
    }
    if proxy:
        options["proxy"] = proxy
    with yt_dlp.YoutubeDL(options) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except yt_dlp.utils.DownloadError as error:
            message = re.sub(r"^ERROR:\s*|;?\s*please report this issue.*$", "", str(error))
            raise YtScriptError(f"Could not read {url}: {message}") from error
    return [entry for entry in info.get("entries") or [] if entry]


def resolve_channel(channel: str, proxy: str | None = None) -> str:
    """Return the base URL of a channel given as a URL, handle, ID or name."""
    url = channel_url(channel)
    if url:
        return url

    name = channel.strip()
    if not name:
        raise YtScriptError("No channel given.")
    if _HANDLE_RE.fullmatch(name):
        # A single word is most likely a handle typed without the "@".
        handle_url = f"{YOUTUBE}/@{quote(name)}"
        try:
            _playlist_entries(f"{handle_url}/videos", 1, proxy)
            return handle_url
        except YtScriptError:
            pass

    search_url = f"{YOUTUBE}/results?search_query={quote_plus(name)}&sp={_CHANNEL_FILTER}"
    for entry in _playlist_entries(search_url, 5, proxy):
        url = entry.get("channel_url") or entry.get("url") or ""
        if "/channel/" in url or "/@" in url:
            return channel_url(url)
    raise YtScriptError(f"No YouTube channel found for {channel!r}.")


def _to_video(entry: dict) -> Video | None:
    """Turn a listing entry into a Video, skipping playlists and channels."""
    if not _VIDEO_ID_RE.fullmatch(entry.get("id") or "") or not entry.get("title"):
        return None
    return Video(id=entry["id"], title=entry["title"])


def latest_videos(base_url: str, count: int, proxy: str | None = None) -> list[Video]:
    """Return the channel's `count` most recent videos, newest first."""
    entries = _playlist_entries(f"{base_url}/videos", count, proxy)
    videos = [video for video in map(_to_video, entries) if video]
    if not videos:
        raise YtScriptError(f"No videos found on {base_url}.")
    return videos[:count]


def normalize_title(title: str) -> str:
    """Lowercase, strip accents and punctuation, and collapse whitespace."""
    text = unicodedata.normalize("NFKD", title.casefold())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(re.sub(r"[^\w\s]", " ", text).split())


def title_score(query: str, title: str) -> float:
    """Score from 0 to 1 for how well a video title matches the requested title."""
    query, title = normalize_title(query), normalize_title(title)
    if not query or not title:
        return 0.0
    if query == title:
        return 1.0
    ratio = SequenceMatcher(None, query, title).ratio()
    if f" {query} " in f" {title} ":
        # The requested title is a whole-word part of this one.
        ratio = max(ratio, 0.9)
    query_words = set(query.split())
    coverage = len(query_words & set(title.split())) / len(query_words)
    return max(ratio, 0.85 * coverage)


def rank_titles(query: str, videos: list[Video]) -> list[TitleMatch]:
    """Return the videos ranked by how well their title matches, best first."""
    matches = [TitleMatch(video, title_score(query, video.title)) for video in videos]
    return sorted(matches, key=lambda match: match.score, reverse=True)


def find_video(
    base_url: str, title: str, search_depth: int = 500, proxy: str | None = None
) -> Video:
    """Find the channel's video whose title best matches `title`.

    Tries the channel's own search first, then scans up to `search_depth` of the
    channel's most recent videos.
    """

    def channel_search() -> list[dict]:
        try:
            return _playlist_entries(f"{base_url}/search?query={quote_plus(title)}", 30, proxy)
        except YtScriptError:
            return []  # Fall back to scanning the uploads.

    candidates: dict[str, Video] = {}
    ranked: list[TitleMatch] = []
    for entries in (
        channel_search,
        lambda: _playlist_entries(f"{base_url}/videos", search_depth, proxy),
    ):
        for video in map(_to_video, entries()):
            if video:
                candidates.setdefault(video.id, video)
        ranked = rank_titles(title, list(candidates.values()))
        if ranked and ranked[0].score >= MATCH_THRESHOLD:
            return ranked[0].video

    message = f"No video titled {title!r} found on {base_url}."
    closest = [match.video.title for match in ranked[:5] if match.score > 0.3]
    if closest:
        message += " Closest titles:\n" + "\n".join(f"  - {name}" for name in closest)
    raise YtScriptError(message)
