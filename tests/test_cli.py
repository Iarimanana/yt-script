import json

import pytest

from yt_script import cli
from yt_script.channel import Video
from yt_script.errors import YtScriptError
from yt_script.transcript import Line, Transcript

BASE = "https://www.youtube.com/@KarstenRunquist"
TITLE = "Resident Evil: How To Adapt a Video Game in 2026"
VIDEOS = [Video("aaaaaaaaaa1", TITLE), Video("aaaaaaaaaa2", "Another Video"), Video("aaaaaaaaaa3", "Third")]


@pytest.fixture
def fake_backend(monkeypatch):
    calls = {}

    def resolve_channel(channel, proxy=None):
        calls["channel"] = channel
        return BASE

    def latest_videos(base_url, count, proxy=None):
        calls["latest"] = count
        return VIDEOS[:count]

    def find_video(base_url, title, search_depth=500, proxy=None):
        calls["title"] = title
        return VIDEOS[0]

    def fetch_transcript(video_id, languages=("en",), proxy=None):
        calls.setdefault("languages", languages)
        if video_id == "aaaaaaaaaa3":
            raise YtScriptError(f"No transcript for video {video_id}: Subtitles are disabled")
        return Transcript(
            language="English (auto-generated)",
            language_code="en",
            is_generated=True,
            lines=[Line(0, "[Music]"), Line(1, f"Script of {video_id}.")],
        )

    for name, fake in [
        ("resolve_channel", resolve_channel),
        ("latest_videos", latest_videos),
        ("find_video", find_video),
        ("fetch_transcript", fetch_transcript),
    ]:
        monkeypatch.setattr(cli, name, fake)
    return calls


def test_title_prints_script(fake_backend, capsys):
    assert cli.main([BASE, "--title", TITLE]) == 0
    out = capsys.readouterr().out
    assert out == (
        f"Title: {TITLE}\n"
        "URL: https://www.youtube.com/watch?v=aaaaaaaaaa1\n"
        "Transcript: English (auto-generated)\n\n"
        "Script of aaaaaaaaaa1.\n"
    )
    assert fake_backend["title"] == TITLE
    assert fake_backend["languages"] == ["en"]


def test_defaults_to_latest_video(fake_backend, capsys):
    assert cli.main(["@KarstenRunquist"]) == 0
    assert fake_backend["latest"] == 1
    assert "Script of aaaaaaaaaa1." in capsys.readouterr().out


def test_latest_n_separates_videos(fake_backend, capsys):
    assert cli.main([BASE, "-n", "2", "--timestamps", "--keep-cues", "-l", "fr", "-l", "en"]) == 0
    out = capsys.readouterr().out
    assert out.count("=" * 80) == 1
    assert "[0:00] [Music] Script of aaaaaaaaaa2." in out
    assert fake_backend["languages"] == ["fr", "en"]


def test_failed_transcript_is_reported_and_others_still_print(fake_backend, capsys):
    assert cli.main([BASE, "--latest", "3"]) == 1
    captured = capsys.readouterr()
    assert "Script of aaaaaaaaaa1." in captured.out
    assert "Script of aaaaaaaaaa2." in captured.out
    assert "error: No transcript for video aaaaaaaaaa3" in captured.err


def test_json_output(fake_backend, capsys):
    assert cli.main([BASE, "--title", TITLE, "--format", "json"]) == 0
    [record] = json.loads(capsys.readouterr().out)
    assert record["title"] == TITLE
    assert record["url"] == "https://www.youtube.com/watch?v=aaaaaaaaaa1"
    assert record["script"] == "Script of aaaaaaaaaa1."
    assert record["paragraphs"] == [{"start": 1, "text": "Script of aaaaaaaaaa1."}]


def test_output_dir_writes_one_file_per_video(fake_backend, tmp_path, capsys):
    assert cli.main([BASE, "-n", "2", "-o", str(tmp_path / "scripts")]) == 0
    files = sorted(path.name for path in (tmp_path / "scripts").iterdir())
    assert files == [
        "Another Video [aaaaaaaaaa2].txt",
        "Resident Evil_ How To Adapt a Video Game in 2026 [aaaaaaaaaa1].txt",
    ]
    assert capsys.readouterr().out == ""


def test_channel_errors_are_reported(monkeypatch, capsys):
    def resolve_channel(channel, proxy=None):
        raise YtScriptError("No YouTube channel found for 'nobody'.")

    monkeypatch.setattr(cli, "resolve_channel", resolve_channel)
    assert cli.main(["nobody"]) == 1
    assert "error: No YouTube channel found" in capsys.readouterr().err


@pytest.mark.parametrize("args", [[BASE, "--latest", "0"], [BASE, "-n", "2", "-t", TITLE]])
def test_invalid_arguments(args):
    with pytest.raises(SystemExit) as exit_info:
        cli.main(args)
    assert exit_info.value.code == 2


def test_asks_for_channel_and_title_when_run_without_arguments(fake_backend, monkeypatch, capsys):
    answers = iter([BASE, TITLE])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    assert cli.main([]) == 0
    assert fake_backend["channel"] == BASE
    assert fake_backend["title"] == TITLE


def test_asks_and_accepts_a_number_of_latest_videos(fake_backend, monkeypatch, capsys):
    answers = iter([BASE, "2"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    assert cli.main([]) == 0
    assert fake_backend["latest"] == 2
