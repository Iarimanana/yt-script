"""Command line: yt-script CHANNEL [--latest N | --title TITLE]."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from .channel import Video, find_video, latest_videos, resolve_channel
from .errors import YtScriptError
from .transcript import Transcript, fetch_transcript, format_script, to_paragraphs

EXAMPLE = (
    "examples:\n"
    "  yt-script https://www.youtube.com/@KarstenRunquist\n"
    "  yt-script @KarstenRunquist --latest 3 --output-dir scripts\n"
    '  yt-script @KarstenRunquist --title "Resident Evil: How To Adapt a Video Game in 2026"'
)


def positive_int(value: str) -> int:
    if not value.isdigit() or int(value) < 1:
        raise argparse.ArgumentTypeError(f"must be a whole number of 1 or more, not {value!r}")
    return int(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="yt-script",
        description="Get the script (transcript) of a YouTube channel's videos.",
        epilog=EXAMPLE,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "channel",
        nargs="?",
        help="channel URL, @handle, channel ID or name; leave out to be asked for it",
    )
    which = parser.add_mutually_exclusive_group()
    which.add_argument(
        "-n", "--latest", type=positive_int, metavar="N",
        help="get the N most recent videos (default: 1)",
    )
    which.add_argument(
        "-t", "--title",
        help="get the video with this title (close matches count)",
    )
    parser.add_argument(
        "-l", "--lang", action="append", metavar="CODE",
        help="preferred transcript language, repeat for fallbacks (default: en); "
        "if none is available, the video's own language is used",
    )
    parser.add_argument(
        "--timestamps", action="store_true",
        help="start each paragraph with its [m:ss] timestamp",
    )
    parser.add_argument(
        "--keep-cues", action="store_true",
        help='keep sound cues such as "[Music]"',
    )
    parser.add_argument(
        "-f", "--format", choices=("text", "json"), default="text",
        help="output format (default: text)",
    )
    parser.add_argument(
        "-o", "--output-dir", type=Path, metavar="DIR",
        help="save each script to a file in DIR instead of printing it",
    )
    parser.add_argument(
        "--search-depth", type=positive_int, default=500, metavar="N",
        help="how many recent videos to scan when looking for --title (default: 500)",
    )
    parser.add_argument("--proxy", metavar="URL", help="proxy for all requests to YouTube")
    return parser


def ask_for_missing(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    """Prompt for the channel and the video when they were not given."""
    args.channel = input("Channel (URL, @handle or name): ").strip()
    if args.latest is None and args.title is None:
        answer = input("Video title, or number of latest videos [1]: ").strip() or "1"
        if answer.isdigit():
            try:
                args.latest = positive_int(answer)
            except argparse.ArgumentTypeError as error:
                parser.error(str(error))
        else:
            args.title = answer


def status(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


def describe_language(transcript: Transcript) -> str:
    # Auto-generated languages are already named like "English (auto-generated)".
    if transcript.is_generated and "auto-generated" not in transcript.language:
        return f"{transcript.language} (auto-generated)"
    return transcript.language


def render_text(video: Video, transcript: Transcript, args: argparse.Namespace) -> str:
    paragraphs = to_paragraphs(transcript.lines, keep_cues=args.keep_cues)
    return (
        f"Title: {video.title}\n"
        f"URL: {video.url}\n"
        f"Transcript: {describe_language(transcript)}\n\n"
        f"{format_script(paragraphs, args.timestamps)}\n"
    )


def render_json(video: Video, transcript: Transcript, args: argparse.Namespace) -> dict:
    paragraphs = to_paragraphs(transcript.lines, keep_cues=args.keep_cues)
    return {
        "id": video.id,
        "title": video.title,
        "url": video.url,
        "language": transcript.language,
        "language_code": transcript.language_code,
        "is_generated": transcript.is_generated,
        "script": format_script(paragraphs, args.timestamps),
        "paragraphs": [{"start": p.start, "text": p.text} for p in paragraphs],
    }


def safe_filename(video: Video, extension: str) -> str:
    name = re.sub(r'[\\/:*?"<>|\x00-\x1f]', "_", video.title).strip(" .")[:150]
    return f"{name} [{video.id}].{extension}"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.channel is None:
        if not sys.stdin.isatty():
            parser.error("the channel is required")
        ask_for_missing(args, parser)
    languages = args.lang or ["en"]

    try:
        status(f"Looking up {args.channel}…")
        base_url = resolve_channel(args.channel, args.proxy)
        if args.title:
            videos = [find_video(base_url, args.title, args.search_depth, args.proxy)]
        else:
            videos = latest_videos(base_url, args.latest or 1, args.proxy)
    except YtScriptError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    texts: list[str] = []
    records: list[dict] = []
    failures = 0
    for video in videos:
        status(f"Fetching the transcript of {video.title!r} ({video.url})…")
        try:
            transcript = fetch_transcript(video.id, languages, args.proxy)
        except YtScriptError as error:
            print(f"error: {error}", file=sys.stderr)
            failures += 1
            continue

        if args.format == "json":
            record = render_json(video, transcript, args)
            content = json.dumps(record, ensure_ascii=False, indent=2) + "\n"
            records.append(record)
        else:
            content = render_text(video, transcript, args)
            texts.append(content)

        if args.output_dir:
            args.output_dir.mkdir(parents=True, exist_ok=True)
            path = args.output_dir / safe_filename(video, "json" if args.format == "json" else "txt")
            path.write_text(content, encoding="utf-8")
            status(f"Saved {path}")

    if not args.output_dir:
        if args.format == "json":
            print(json.dumps(records, ensure_ascii=False, indent=2))
        else:
            print(("\n" + "=" * 80 + "\n\n").join(texts), end="")
    return 1 if failures else 0


def run() -> None:
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
