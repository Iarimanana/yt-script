import pytest
import requests
from youtube_transcript_api import FetchedTranscript, FetchedTranscriptSnippet, TranscriptsDisabled

from yt_script import transcript
from yt_script.errors import YtScriptError
from yt_script.transcript import (
    Line,
    clean_text,
    fetch_transcript,
    format_script,
    format_timestamp,
    to_paragraphs,
)


class FakeTranscript:
    def __init__(self, language_code, is_generated, texts):
        self.language_code = language_code
        self.language = {"en": "English", "fr": "French"}[language_code]
        if is_generated:
            self.language += " (auto-generated)"
        self.is_generated = is_generated
        self.texts = texts

    def fetch(self):
        return FetchedTranscript(
            snippets=[
                FetchedTranscriptSnippet(text=text, start=i * 2.0, duration=2.0)
                for i, text in enumerate(self.texts)
            ],
            video_id="aaaaaaaaaa1",
            language=self.language,
            language_code=self.language_code,
            is_generated=self.is_generated,
        )


class FakeTranscriptList:
    def __init__(self, transcripts):
        self.transcripts = transcripts

    def __iter__(self):
        return iter(sorted(self.transcripts, key=lambda t: t.is_generated))

    def find_transcript(self, codes):
        for code in codes:
            for t in self:
                if t.language_code == code:
                    return t
        from youtube_transcript_api import NoTranscriptFound

        raise NoTranscriptFound("aaaaaaaaaa1", codes, self)


def use_transcripts(monkeypatch, transcripts=None, error=None):
    class FakeApi:
        def __init__(self, proxy_config=None):
            self.proxy_config = proxy_config

        def list(self, video_id):
            if error:
                raise error
            return FakeTranscriptList(transcripts)

    monkeypatch.setattr(transcript, "YouTubeTranscriptApi", FakeApi)


def test_fetch_prefers_requested_language(monkeypatch):
    use_transcripts(
        monkeypatch,
        [FakeTranscript("fr", False, ["Bonjour."]), FakeTranscript("en", True, ["Hello."])],
    )
    result = fetch_transcript("aaaaaaaaaa1", ["en"])
    assert result.language_code == "en"
    assert result.is_generated
    assert [line.text for line in result.lines] == ["Hello."]


def test_fetch_falls_back_to_any_language_preferring_manual(monkeypatch):
    use_transcripts(
        monkeypatch,
        [FakeTranscript("en", True, ["auto"]), FakeTranscript("fr", False, ["Bonjour."])],
    )
    result = fetch_transcript("aaaaaaaaaa1", ["de"])
    assert result.language_code == "fr"
    assert not result.is_generated


def test_fetch_reports_missing_transcript(monkeypatch):
    use_transcripts(monkeypatch, error=TranscriptsDisabled("aaaaaaaaaa1"))
    with pytest.raises(YtScriptError, match="Subtitles are disabled"):
        fetch_transcript("aaaaaaaaaa1")


def test_fetch_reports_network_errors(monkeypatch):
    use_transcripts(monkeypatch, error=requests.ConnectionError("connection refused"))
    with pytest.raises(YtScriptError, match="Could not reach YouTube.*connection refused"):
        fetch_transcript("aaaaaaaaaa1")


def test_fetch_reports_video_without_any_transcript(monkeypatch):
    use_transcripts(monkeypatch, [])
    with pytest.raises(YtScriptError, match="No transcript for video aaaaaaaaaa1"):
        fetch_transcript("aaaaaaaaaa1", ["en"])


def test_clean_text_drops_cues_and_line_breaks():
    assert clean_text("[Music]\nsome  words\n[Applause]") == "some words"
    assert clean_text("[Music] hi", keep_cues=True) == "[Music] hi"
    assert clean_text("[Music]") == ""


def test_paragraphs_break_after_sentence_end():
    lines = [Line(0, "One."), Line(20, "Two."), Line(31, "Three"), Line(35, "four."), Line(40, "Five.")]
    paragraphs = to_paragraphs(lines, paragraph_seconds=30)
    assert [p.text for p in paragraphs] == ["One. Two. Three four.", "Five."]
    assert [p.start for p in paragraphs] == [0, 40]


def test_paragraphs_break_without_punctuation():
    lines = [Line(t, "word") for t in range(0, 130, 10)]
    paragraphs = to_paragraphs(lines, paragraph_seconds=30)
    assert [p.start for p in paragraphs] == [0, 70]


def test_paragraphs_skip_cue_only_lines():
    paragraphs = to_paragraphs([Line(0, "[Music]"), Line(5, "Hi there.")])
    assert [(p.start, p.text) for p in paragraphs] == [(5, "Hi there.")]


@pytest.mark.parametrize("seconds, expected", [(0, "0:00"), (65.9, "1:05"), (3725, "1:02:05")])
def test_format_timestamp(seconds, expected):
    assert format_timestamp(seconds) == expected


def test_format_script():
    paragraphs = to_paragraphs([Line(0, "A."), Line(75, "B.")], paragraph_seconds=30)
    assert format_script(paragraphs) == "A. B."
    paragraphs = to_paragraphs([Line(0, "A."), Line(45, "B."), Line(50, "C.")], paragraph_seconds=30)
    assert format_script(paragraphs, timestamps=True) == "[0:00] A. B.\n\n[0:50] C."
