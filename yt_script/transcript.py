"""Fetch a video's transcript and lay it out as a readable script."""

from __future__ import annotations

import re
from dataclasses import dataclass

import requests
from youtube_transcript_api import (
    CouldNotRetrieveTranscript,
    NoTranscriptFound,
    YouTubeTranscriptApi,
)
from youtube_transcript_api.proxies import GenericProxyConfig

from .errors import YtScriptError

# Sound cues in captions, such as "[Music]" or "[Applause]".
_CUE_RE = re.compile(r"\[[^\]]*\]")
_SENTENCE_END_RE = re.compile(r"[.!?…][\"')\]]*$")


@dataclass
class Line:
    start: float
    text: str


@dataclass
class Transcript:
    language: str
    language_code: str
    is_generated: bool
    lines: list[Line]


@dataclass
class Paragraph:
    start: float
    text: str


def fetch_transcript(
    video_id: str, languages: list[str] | tuple[str, ...] = ("en",), proxy: str | None = None
) -> Transcript:
    """Fetch the transcript in the first available language from `languages`.

    If none of them exists, falls back to whatever transcript the video has,
    preferring one written by a person over an auto-generated one.
    """
    proxy_config = GenericProxyConfig(http_url=proxy, https_url=proxy) if proxy else None
    api = YouTubeTranscriptApi(proxy_config=proxy_config)
    try:
        available = api.list(video_id)
        try:
            chosen = available.find_transcript(languages)
        except NoTranscriptFound:
            chosen = next(iter(available), None)
            if chosen is None:
                raise
        fetched = chosen.fetch()
    except CouldNotRetrieveTranscript as error:
        reason = error.cause.strip() or type(error).__name__
        raise YtScriptError(f"No transcript for video {video_id}: {reason}") from error
    except requests.RequestException as error:
        raise YtScriptError(f"Could not reach YouTube for video {video_id}: {error}") from error
    return Transcript(
        language=fetched.language,
        language_code=fetched.language_code,
        is_generated=fetched.is_generated,
        lines=[Line(snippet.start, snippet.text) for snippet in fetched.snippets],
    )


def clean_text(text: str, keep_cues: bool = False) -> str:
    """Join a caption's lines and drop sound cues such as "[Music]"."""
    if not keep_cues:
        text = _CUE_RE.sub(" ", text)
    return " ".join(text.split())


def to_paragraphs(
    lines: list[Line], paragraph_seconds: float = 30.0, keep_cues: bool = False
) -> list[Paragraph]:
    """Group caption lines into paragraphs of roughly `paragraph_seconds` each.

    A paragraph ends at the first sentence end after `paragraph_seconds`, or at
    twice that if the captions have no punctuation (common in auto-generated ones).
    """
    paragraphs: list[Paragraph] = []
    start: float | None = None
    words: list[str] = []
    for line in lines:
        text = clean_text(line.text, keep_cues)
        if not text:
            continue
        if start is None:
            start = line.start
        words.append(text)
        elapsed = line.start - start
        if (elapsed >= paragraph_seconds and _SENTENCE_END_RE.search(text)) or (
            elapsed >= 2 * paragraph_seconds
        ):
            paragraphs.append(Paragraph(start, " ".join(words)))
            start, words = None, []
    if words:
        paragraphs.append(Paragraph(start, " ".join(words)))
    return paragraphs


def format_timestamp(seconds: float) -> str:
    """Format seconds as m:ss, or h:mm:ss for an hour or more."""
    minutes, secs = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}" if hours else f"{minutes}:{secs:02d}"


def format_script(paragraphs: list[Paragraph], timestamps: bool = False) -> str:
    """Render paragraphs as plain text separated by blank lines."""
    return "\n\n".join(
        f"[{format_timestamp(p.start)}] {p.text}" if timestamps else p.text
        for p in paragraphs
    )
