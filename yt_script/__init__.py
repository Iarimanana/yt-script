"""Get the script (transcript) of a YouTube channel's videos."""

from .channel import Video, find_video, latest_videos, resolve_channel
from .errors import YtScriptError
from .transcript import fetch_transcript, format_script, to_paragraphs

__all__ = [
    "Video",
    "YtScriptError",
    "fetch_transcript",
    "find_video",
    "format_script",
    "latest_videos",
    "resolve_channel",
    "to_paragraphs",
]
