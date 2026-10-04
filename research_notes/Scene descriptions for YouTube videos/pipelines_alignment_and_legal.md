# Scene-by-scene video descriptions aligned with transcripts: pipelines, alignment techniques, and YouTube legal/ToS constraints (as of October 2026)

> Research note, method: the egress proxy blocked direct fetches of youtube.com, developers.google.com, ai.google.dev, support.google.com, docs.nvidia.com, learn.microsoft.com, arxiv.org, techcrunch.com, torrentfreak.com, freiheitsrechte.org and several law-firm blogs. Statements attributed to those pages come from search-engine snippets or summaries of them, not from full-page reads. GitHub READMEs were read in full. This is not legal advice; it reports what terms and sources say.

## (a) Proven pipeline designs and open-source projects (2024–2026)

### Takeaway
Nearly every working system uses the same skeleton. (1) Segment the video, either into fixed chunks (NVIDIA VSS, Azure sample: 16–30 s) or at detected shots (PySceneDetect or ffmpeg scene-change). (2) Sample a handful of frames per segment and deduplicate near-identical frames. (3) Get a transcript, preferring existing subtitles and falling back to Whisper or other ASR. (4) Caption each segment with a VLM, passing the transcript or previous context in. (5) Aggregate into JSON or Markdown, usually with a second LLM "summarize/reconstruct" pass. The pitfalls people report are token cost from too many frames, near-duplicate frames from static or talking-head content, over-long or hallucinated descriptions, and segmentation tuned wrongly for the content type.

### Cited Findings

**NVIDIA AI Blueprint: Video Search & Summarization (VSS)**
- VSS has two parts. An ingestion pipeline extracts "captions and scene descriptions" from video. A retrieval pipeline indexes these and uses them for summarization and Q&A. — [NVIDIA VSS docs 2.4.1 (via search snippet)](https://docs.nvidia.com/vss/2.4.1/content/architecture.html)
- Video is processed in chunks of "a few seconds or a few minutes, based on model and use case", spread across GPUs in parallel. Frames are sampled per chunk: the docs' example is 8 frames from a 30-second chunk (900 frames). — [NVIDIA VSS docs 2.4.1 (via snippet)](https://docs.nvidia.com/vss/2.4.1/content/architecture.html); [VSS docs 2.3.0](https://docs.nvidia.com/vss/2.3.0/content/architecture.html)
- When audio transcription is on, each chunk's audio is converted to 16 kHz mono and sent to Riva ASR. VLM captions, audio transcripts, optional CV metadata and per-chunk timestamps then all go to the retrieval pipeline. The VLMs listed in that doc version are Cosmos-Reason2, Cosmos-Reason1 and GPT-4o, and custom VLMs can be plugged in. — [NVIDIA VSS docs (via snippet)](https://docs.nvidia.com/vss/2.4.1/content/architecture.html)
- The current GitHub README (develop branch, about 2,748 commits) describes a three-layer architecture: real-time video intelligence, downstream analytics, and agentic/offline processing over MCP. It names "Cosmos3 Nano Reasoner" (vision) and "Nemotron 3.5 Lightning 30B A3B" (language). It describes "long video summarization through chunking and aggregation of dense captions" and marks video search as "alpha". The launchable deployment cites a minimum of 2x RTX PRO 6000 SE. — [NVIDIA-AI-Blueprints/video-search-and-summarization README](https://github.com/NVIDIA-AI-Blueprints/video-search-and-summarization)

**Microsoft / Azure**
- Azure-Samples `video-analysis-with-aoai` splits video into configurable segments (default 16 s; 0 = whole video). It samples frames at a user-set fps with timestamps embedded, optionally adds a Whisper transcript, and sends frames plus transcript to Azure OpenAI multimodal models. A resize ratio is offered "to reduce token usage". There is a hard cap of "a maximum of 50 images per request", checked as `seconds_to_split × frames_per_second ≤ 50`. The shot-analysis variant writes JSON per segment. — [Azure-Samples/video-analysis-with-aoai](https://github.com/Azure-Samples/video-analysis-with-aoai)
- Azure AI Content Understanding (video) works in two stages: "content extraction" (transcript, shots, key frames) and "field extraction", where a generative model produces custom fields and does segmentation. Output includes a WebVTT transcript with diarization, ordered key-frame thumbnails, "natural-language segment descriptions with visual and speech context", and scene segmentation by user-defined categories. — [Microsoft Learn: Content Understanding video overview (via snippet)](https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/video/overview)

**Open-source "LLM watches a video" tools**
- `byjlw/video-analyzer` runs three stages: frame extraction plus Whisper transcription; per-frame analysis with a prompt that carries context from previous frames; and "video reconstruction", which synthesizes the frame analyses and the transcript into one description, using the first frame "to set the scene". Output is JSON with metadata, transcript, frame-by-frame analysis and final description. It runs locally on Llama 3.2 11B Vision via Ollama (16 GB RAM minimum, 12 GB+ VRAM) or on OpenAI-compatible APIs. The README gives no keyframe thresholds. — [byjlw/video-analyzer](https://github.com/byjlw/video-analyzer)
- `claude-real-video` (PyPI v0.7.x–0.10.x):
  - Frames come from ffmpeg scene-change detection (`--scene` default 0.30) plus a density floor (`--fps-floor` 1.0). `--adaptive` compares each frame against a rolling neighbourhood to catch slow morphs.
  - Dedup is a sliding window over the last 4 kept frames, measured as pixel difference on downscaled RGB (default 8% of pixels must change). It also has a "settled-local" channel for small text or UI changes, and a v0.7.16 "action channel" added because a percentage comparator was "structurally blind to a subject that covers <1% of the frame".
  - A 10-minute unchanged slide collapses to 1 frame, and A-B-A cutaways are not re-sent.
  - `--text-anchors` forces frames at subtitle timestamps (at most 1 per second) for lectures and talking-head explainers.
  - Transcripts come from existing .srt/.vtt files first and Whisper (or faster-whisper/mlx-whisper) otherwise. Optional diarization adds `[SPEAKER_00]` labels.
  - Output: frames plus frames.json (timestamp, selection_reason), transcript.txt/.json, a MANIFEST.txt that tells the LLM how to read the folder, and optional 3×3 contact sheets.
  - Default frame width is 640 px. On a 3-minute 640×360 video it used about 52k tokens for 170 frames, or about 25k with `--max-frames 80`. The auto max-frames value is clamp(150, window×1.5, 600).
  - The README criticizes fixed 1-fps sampling (as Gemini does) because it over-samples static content and under-samples fast cuts. — [HUANGCHIHHUNGLeo/claude-real-video](https://github.com/HUANGCHIHHUNGLeo/claude-real-video)
- `Sriikaran/feedanalyser` pipeline: PySceneDetect AdaptiveDetector → "Shot-Aware Frame Sampler" (keyframes and temporal windows) → "Unified Timestamp Alignment → Gapless Segment Timeline" → local Ollama vision (`visual_summary`, `narrative_role`). The output analysis.json has `scenes`, `segments` and `semantic_events`, plus a 13-section Markdown report. A validator checks "timestamp ordering, boundaries, contiguity". — [feedanalyser](https://github.com/Sriikaran/feedanalyser)
- `OdakK/video_editor_agent` builds "timeline atoms: one shot, its timecodes, what is said and what is seen". It uses PySceneDetect shots, 1 keyframe per shot, optional BLIP captions, and faster-whisper word-level segments matched to the shots they overlap. — [video_editor_agent](https://github.com/OdakK/video_editor_agent)
- `cinematlas` (PyPI) takes PySceneDetect cuts (each ≤30 s), aligns faster-whisper timestamped sentences to the scenes, extracts the middle keyframe, and builds joint keyframe+transcript vectors per scene. — [cinematlas on PyPI (via snippet)](https://pypi.org/project/cinematlas/0.16.3/)

**Video RAG**
- VideoRAG (HKU + Baidu; arXiv 2502.01549, listed at KDD 2026) uses a dual-channel design: graph-based textual knowledge grounding across videos, plus multimodal context encoding that preserves visual features. It was evaluated on the "LongerVideos" benchmark (160+ videos, 134+ hours). The README claims processing of "hundreds of hours on a single RTX 3090 (24GB)" and announces a "Vimo" desktop app (Mac first). The README does not give clip length, VLM or ASR choices. — [VideoRAG paper (via snippet)](https://arxiv.org/html/2502.01549v1); [HKUDS/VideoRAG](https://github.com/HKUDS/VideoRAG)

**Automatic audio description (AD) research and tools**
- DescribePro (arXiv 2508.01092, 2025) is a human-AI AD tool. It uses Pydub silence detection, Silero VAD for speech/non-speech, and PySceneDetect for scene changes. — [DescribePro (via snippet)](https://arxiv.org/pdf/2508.01092)
- NarrAD (WACV 2025) is training-free. It passes movie-script context to a multimodal LLM and retrieves the relevant script part at scene level via "dialogue synchronization and scene recognition", because using the whole script performed poorly. It reports that LLM-generated ADs "are often too long". — [NarrAD, WACV 2025](https://openaccess.thecvf.com/content/WACV2025/papers/Park_NarrAD_Automatic_Generation_of_Audio_Descriptions_for_Movies_with_Rich_WACV_2025_paper.pdf)
- LLM-AD (Peng Chu, Jiang Wang; arXiv 2405.00983, 2024) is a GPT-4V-based AD system. Details could not be fetched. — [arXiv 2405.00983](https://arxiv.org/pdf/2405.00983)
- Recent 2026 preprints, REFRAMED (arXiv 2608.09765) and "What, When, and How: Audio Description as Constrained Global Optimization" (arXiv 2609.30121), treat when to describe (fitting dialogue gaps) as a core problem. A snippet reports that dialogue-gap assignment covers "about 90% of reference description elements". — [REFRAMED](https://arxiv.org/pdf/2608.09765); [What, When, and How](https://arxiv.org/html/2609.30121)
- A US patent covers automatically generating descriptive video service tracks: detect dialogue gaps, generate scene text, then TTS. — [USPTO 11190855](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11190855)

**Hosted "send the whole video" approach (Gemini)**
- Gemini samples video at 1 fps by default. Each frame costs about 258 tokens at default media resolution or 66 at low; audio adds about 32 tokens/s. That totals about 300 tokens/s of video at default resolution and about 100 tokens/s at low. Timestamps are referenced as MM:SS. — [Gemini video docs (via snippet)](https://ai.google.dev/gemini-api/docs/video-understanding); [s-anand.net: How does Gemini process videos](https://www.s-anand.net/blog/how-does-gemini-process-videos/)
- On 2026-09-01 Google reportedly added "agentic video understanding". The model is given `get_transcript`, `get_frames(start, end, fps)` and `get_audio(start, end)` tools and chooses what to watch. Google's benchmarks claim up to 88% fewer tokens and up to 66% lower cost per query. It is reported on Gemini 3.7 Flash, 3.6 Flash and 3.5 Flash-Lite as a single config flag with no extra fee. These are secondary sources; Google's page could not be fetched. — [NYU Shanghai RITS summary](https://rits.shanghai.nyu.edu/ai/gemini-agentic-video-understanding/); [howaiworks.ai](https://howaiworks.ai/blog/google-gemini-agentic-video-2026)

**Reported pitfalls**
- **Fixed-interval sampling:** it over-samples static slides or talking heads and under-samples fast cuts. A-B-A cutaways get re-sent. — [claude-real-video](https://github.com/HUANGCHIHHUNGLeo/claude-real-video)
- **Small subjects:** pixel-percentage dedup misses subjects that cover less than 1% of the frame. — [claude-real-video](https://github.com/HUANGCHIHHUNGLeo/claude-real-video)
- **PySceneDetect tuning:** ContentDetector's default threshold is 27.0, and one source recommends `min_scene_len` ≈ 0.6 s for Content/Adaptive detectors. Optimal parameters vary by content type: long-form broadcast footage works better with lower thresholds than short web clips. Talking-head content produces few detections. — [PySceneDetect docs index (via snippet)](https://docsearch.algolia.com/mcp/docs/repo/breakthrough/pyscenedetect); [PySceneDetect docs 0.7.1](https://www.scenedetect.com/docs/latest/)
- **Over-long descriptions:** LLM ADs come out too long for the available gaps. — [NarrAD](https://openaccess.thecvf.com/content/WACV2025/papers/Park_NarrAD_Automatic_Generation_of_Audio_Descriptions_for_Movies_with_Rich_WACV_2025_paper.pdf)
- **Request caps:** Azure OpenAI allows at most 50 images per request. — [Azure sample](https://github.com/Azure-Samples/video-analysis-with-aoai)
- **Gemini YouTube URLs:** a Google AI Developers Forum thread is titled "Recent YouTube Videos Inaccessible via Gemini-3-Flash-Preview API". Only the title was seen. — [discuss.ai.google.dev](https://discuss.ai.google.dev/t/recent-youtube-videos-inaccessible-via-gemini-3-flash-preview-api/114076)

### Inferences
- For a scene-by-scene document, the best-supported design is a hybrid: shot detection (PySceneDetect Adaptive or ffmpeg scene) with a minimum scene length, plus a time-based density floor and a maximum scene length. Long talking-head shots then still get periodic samples, and fast-cut montages don't explode into hundreds of scenes. claude-real-video and cinematlas (≤30 s cap) both implement variants of this.
- The two-pass pattern (caption each scene, then an LLM "reconstruct/summarize" pass over all scenes) appears in video-analyzer, NVIDIA VSS (caption → aggregation) and Azure Content Understanding (extraction → field extraction). It looks like the standard way to get a coherent document instead of disconnected captions.
- Talking-head and lecture videos are where pure shot detection fails. Subtitle-anchored frames (claude-real-video `--text-anchors`) or speaker-turn segmentation seem to be the reported fixes.

### Gaps
- Could not read NVIDIA VSS docs for exact prompt templates (caption, summarization, aggregation), default chunk overlap, or the current doc version's frames per chunk.
- No hard published figures on hallucination rates per pipeline. Hallucination concerns appear only qualitatively (e.g., NarrAD "too long"). Could not read LLM-AD's paper.
- LangChain's and LlamaIndex's video loaders were not examined in this session. (LangChain's YouTube loader is commonly transcript-only, but no source for that was fetched here.)

## (b) Aligning visual descriptions with transcript segments; output formats

### Takeaway
In practice, alignment means comparing timestamp intervals: each transcript snippet (start, start+duration) is assigned to the scene(s) it overlaps. Projects build "atoms" of {shot, timecodes, what is said, what is seen} and validate that the timeline is gapless and ordered. Snippets that span a cut need an explicit rule, but no project documents one. Word-level timestamps (faster-whisper/WhisperX) make it possible to split at the cut. Outputs are JSON with scenes/segments arrays plus a Markdown report. WebVTT (`kind="descriptions"`) is the web standard for text descriptions, and WCAG 1.2.7 "extended" AD pauses the video when gaps are too short.

### Cited Findings
- `youtube-transcript-api` returns snippets with `text`, `start` and `duration` fields, covering both manual and auto-generated captions. It uses "an undocumented part of the YouTube API, which is called by the YouTube web-client". — [jdepoix/youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)
- video_editor_agent assigns faster-whisper word-level segments to "the shots they overlap" to form timeline atoms (shot + timecodes + said + seen). The README does not specify a rule for segments that span multiple shots. — [OdakK/video_editor_agent](https://github.com/OdakK/video_editor_agent)
- cinematlas aligns timestamped sentences to scenes capped at 30 s and embeds each scene's middle keyframe together with its transcript. — [cinematlas (via snippet)](https://pypi.org/project/cinematlas/0.16.3/)
- feedanalyser produces a "gapless segment timeline" and validates "timestamp ordering, boundaries, contiguity". Overlap and split rules are undocumented. — [feedanalyser](https://github.com/Sriikaran/feedanalyser)
- **Transcript as model context:**
  - Azure's sample sends the Whisper transcript in the same request as the segment's frames. — [Azure sample](https://github.com/Azure-Samples/video-analysis-with-aoai)
  - video-analyzer instead captions frames with prior-frame context, then merges in the transcript in a separate reconstruction prompt. — [video-analyzer](https://github.com/byjlw/video-analyzer)
  - Azure Content Understanding produces segment descriptions "with visual and speech context". — [Microsoft Learn (via snippet)](https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/video/overview)
  - NarrAD found that retrieving only the scene-relevant script/dialogue, via dialogue synchronization, beats giving the model the full script. — [NarrAD](https://openaccess.thecvf.com/content/WACV2025/papers/Park_NarrAD_Automatic_Generation_of_Audio_Descriptions_for_Movies_with_Rich_WACV_2025_paper.pdf)
- **Merging near-duplicates:** claude-real-video dedups against a window of the last N kept frames (default 4), so returning shots aren't re-described, and collapses static slides to one frame. — [claude-real-video](https://github.com/HUANGCHIHHUNGLeo/claude-real-video)
- **Chunk-boundary transcripts:** when transcribing in chunks, a common practice is 2–5 s of audio overlap, with deduplication by timestamp proximity rather than text matching (verbose_json timestamps). — [theneuralbase: overlap handling](https://theneuralbase.com/whisper/learn/intermediate/overlap-handling/); [theneuralbase: reassembling transcripts](https://theneuralbase.com/whisper-api/learn/intermediate/reassembling-transcripts/)
- **Output formats:**
  - Azure Content Understanding emits its transcript in WebVTT. — [Microsoft Learn (via snippet)](https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/video/overview)
  - claude-real-video emits frames.json, transcript.json/.txt and a MANIFEST.txt, and lets the model cite e.g. "frame_012 @ 00:03:41". — [claude-real-video](https://github.com/HUANGCHIHHUNGLeo/claude-real-video)
  - video-analyzer emits JSON. — [video-analyzer](https://github.com/byjlw/video-analyzer)
  - feedanalyser emits JSON plus a 13-section Markdown report. — [feedanalyser](https://github.com/Sriikaran/feedanalyser)
  - Gemini prompts and answers reference times as MM:SS. — [Gemini docs (via snippet)](https://ai.google.dev/gemini-api/docs/video-understanding)
- **Accessibility standards:**
  - W3C technique H96 uses the HTML `<track>` element with a "descriptions" timed text track (WebVTT). These tracks hold "textual descriptions of the video component intended for audio synthesis". "User agents may support extended audio descriptions by halting the video until the description has been completely synthesized, then restarting the video." — [W3C WCAG 2.2 Technique H96](https://www.w3.org/WAI/WCAG22/Techniques/html/H96.html)
  - WCAG 1.2.7 Extended Audio Description (Level AAA) applies when natural pauses are too short for a complete description. Playback is paused or extended for the narration. — [WCAG 1.2.7 explainer](https://www.disabilityworld.org/toolkit/standards/wcag/1-2-7-extended-audio-description-prerecorded/)
  - AD systems detect dialogue gaps with VAD/silence detection (Silero VAD, Pydub) to place descriptions. — [DescribePro](https://arxiv.org/pdf/2508.01092); [USPTO 11190855](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11190855)

### Inferences
- Practical alignment rules follow from interval overlap. None of the projects document these exact rules; this is synthesis.
  - **Max-overlap assignment:** assign each snippet to the scene with the largest overlap of [start, start+duration] with [scene_start, scene_end]. This keeps each line in one scene and is simplest for Markdown.
  - **Split at cut:** with word-level timestamps (WhisperX/faster-whisper), split a snippet at the cut and assign words by their own timestamps.
  - **Duplicate-with-marker:** list a spanning snippet in both scenes with a continuation marker (e.g., "…").
  - YouTube caption snippets often overlap each other (auto-captions roll), so trim or merge them before assignment.
- Giving the vision model the scene's transcript lines (plus the previous scene's summary) is widely used. It helps name speakers or objects and avoid contradicting the dialogue. NarrAD suggests limiting it to scene-local text rather than the whole transcript.
- Merging near-duplicate consecutive scenes can be done before captioning (pixel/perceptual-difference dedup, as in claude-real-video) or after (merge adjacent scenes whose captions are near-identical and whose combined duration is under a cap). The pre-caption option saves the most cost.
- A WebVTT file with `kind="descriptions"` cues timed to dialogue gaps is the standard-conformant way to ship descriptions as accessibility text. A Markdown or JSON scene list is better for reading and RAG.

### Gaps
- No project README documented its exact rule for transcript snippets that cross a cut.
- No benchmark compares transcript-in-prompt with transcript-merged-later for description accuracy.

## (c) Caching and cost-control patterns

### Takeaway
Most cost savings come from sending fewer and smaller frames. The main levers are: change-based frame selection with dedup (about 50% fewer tokens in one example), low resolution (Gemini about 66 vs 258 tokens per frame; claude-real-video defaults to 640 px), batching several frames per request up to provider caps (Azure 50 images), contact-sheet grids, clipping or windowing the video, and letting the model fetch only the regions it needs (Gemini agentic mode, claimed up to 88% fewer tokens). No source gave quantified results for cheap-model-first cascades.

### Cited Findings
- **Gemini:** 1 fps default; about 300 tokens/s at default resolution vs about 100 tokens/s at low resolution (66 tokens/frame low vs 258 default). — [Gemini docs (via snippet)](https://ai.google.dev/gemini-api/docs/video-understanding); [s-anand.net](https://www.s-anand.net/blog/how-does-gemini-process-videos/)
- **claude-real-video:**
  - 640 px default width; image tokens estimated as (w×h)/750.
  - 170 frames ≈ 52k tokens vs 80 frames ≈ 25k tokens on a 3-minute video.
  - Auto max-frames cap; `--from/--to` windowing (v0.10.x); 3×3 contact sheets (`--grid`).
  - Existing subtitles are reused instead of re-running ASR. — [claude-real-video](https://github.com/HUANGCHIHHUNGLeo/claude-real-video)
- **Azure sample:** a frame resize ratio "to reduce token usage", and batching up to 50 images per request per segment. — [Azure sample](https://github.com/Azure-Samples/video-analysis-with-aoai)
- **NVIDIA VSS:** samples a few frames per chunk (8 of 900 in a 30 s chunk) and parallelizes chunks across GPUs. — [NVIDIA VSS docs (via snippet)](https://docs.nvidia.com/vss/2.4.1/content/architecture.html)
- **Gemini agentic video:** the model calls `get_transcript` first, then `get_frames` at high fps only on candidate regions. Google claims up to 88% fewer tokens and up to 66% lower cost per query. — [NYU Shanghai RITS](https://rits.shanghai.nyu.edu/ai/gemini-agentic-video-understanding/)
- **Gemini YouTube URL feature:** "in preview and is available at no charge", with pricing and limits "likely to change". The free tier is capped at 8 hours of YouTube video per day; the paid tier has no length-based limit. — [Gemini docs (via snippet)](https://ai.google.dev/gemini-api/docs/video-understanding)
- **Local models avoid API cost:** video-analyzer runs on Llama 3.2 11B Vision via Ollama, and feedanalyser uses Ollama with heuristic fallbacks. — [video-analyzer](https://github.com/byjlw/video-analyzer); [feedanalyser](https://github.com/Sriikaran/feedanalyser)

### Inferences
- A sensible cost stack, synthesized from the above:
  1. Cache the downloaded media, transcript and per-scene keyframes on disk, keyed by video ID plus scene index.
  2. Dedup frames before any model call.
  3. Send 1–3 low-resolution keyframes per scene, or one grid image per several scenes, in a single batched request with the scene's transcript lines.
  4. Cache each description keyed by a hash of (frames + transcript + prompt + model), so reruns are free.
  5. Re-describe at high resolution only for scenes flagged as text-heavy.
- Cheap-model-first cascades (a small or local VLM, escalating to a stronger model only for uncertain or text-heavy scenes) are plausible but unbenchmarked in the sources found.

### Gaps
- No source quantified prompt-caching savings for repeated system prompts in video pipelines, or cascade accuracy and cost trade-offs.

## (d) YouTube Terms of Service, API terms, Gemini YouTube URLs, and the AI-training setting

### Takeaway
YouTube's ToS forbids downloading content and automated access ("robots, botnets or scrapers") unless the Service expressly authorizes it or YouTube gives prior written permission. The YouTube API Developer Policies separately forbid API clients from downloading, caching or storing audiovisual content. YouTube says its 2024 third-party AI-training opt-in "does not change our Terms of Service": unauthorized scraping remains prohibited. So the setting is about creator consent to training, not a download licence, and is largely irrelevant to a personal description tool. Gemini's YouTube URL feature lets Google's API read a public video without the user downloading it, which sidesteps the user's own download step. That feature is still a preview with an 8 h/day free cap.

### Cited Findings
- **YouTube ToS, Permissions and Restrictions.** Users may not:
  - "access, reproduce, download, distribute, transmit, broadcast, display, sell, license, alter, modify or otherwise use any part of the Service or any Content except: (a) as expressly authorized by the Service; or (b) with prior written permission from YouTube and, if applicable, the respective rights holders". — [YouTube Terms of Service](https://www.youtube.com/static?template=terms); [archived copy](https://archives.greenairnews.com/www.youtube.com/t/terms.html)
  - "access the Service using any automated means (such as robots, botnets or scrapers) except (a) in the case of public search engines, in accordance with YouTube's robots.txt file; or (b) with YouTube's prior written permission". — [YouTube Terms of Service](https://www.youtube.com/static?template=terms)
- **ToS version history.** The third-party tracker ConductAtlas logged ToS edits on 2026-04-19 (age wording; a date reference to December 15, 2023) and 2026-05-05 (jurisdiction-specific minor ages; a royalty date reference). It describes them as administrative. No change to the download/automation clauses was reported. The primary page could not be verified because youtube.com was blocked. — [ConductAtlas change log](https://conductatlas.com/change/2026-04-19-youtube-youtube-terms-of-service-543/); [ConductAtlas YouTube ToS](https://conductatlas.com/platform/youtube-ads/youtube-terms-of-service/)
- **YouTube API Services Developer Policies.** API clients must not "download, import, backup, cache, or store copies of YouTube audiovisual content without YouTube's prior written approval", must not "make content available for offline playback", and must not "sell, purchase, lease, lend, convey, redistribute, or sublicense" YouTube API Services, including audiovisual content. — [YouTube API Services Developer Policies (via snippet)](https://developers.google.com/youtube/terms/developer-policies)
- **youtube-transcript-api** uses an undocumented web-client endpoint, not the official Data API. Its README warns that "YouTube has started blocking most IPs ... belonging to cloud providers (like AWS, Google Cloud Platform, Azure, etc.)" and recommends rotating residential proxies. — [jdepoix/youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)
- **Gemini YouTube URL feature:** pass the URL as `file_data.file_uri` and ask the model to "summarize, translate, or otherwise interact with the video content". Public videos only (not private or unlisted). 8 h/day free-tier cap. One video per request, which may vary by model. Preview, no charge. — [Gemini video understanding docs (via snippet)](https://ai.google.dev/gemini-api/docs/video-understanding); [apidog mirror](https://gemini-api.apidog.io/doc-965861)
- **Third-party AI training setting (announced 2024-12-16):**
  - Creators can opt in to letting specific third parties train on their videos. The setting is off by default.
  - The 18 companies listed include AI21 Labs, Adobe, Amazon, Anthropic, Apple, ByteDance, Cohere, IBM, Meta, Microsoft, Nvidia, OpenAI, Perplexity, Pika Labs, Runway, Stability AI and xAI. An "All third-party companies" option also exists.
  - It is available to creators with Studio Content Manager admin access. — [TechCrunch (via snippet)](https://techcrunch.com/2024/12/16/youtube-will-let-creators-opt-out-of-third-party-ai-training); [Neowin](https://www.neowin.net/news/youtube-will-let-third-parties-train-ai-models-on-your-content-but-you-have-to-opt-in/)
  - YouTube: "This update does not change our Terms of Service. Accessing creator content in unauthorized ways, such as unauthorized scraping, remains prohibited." — [YouTube Help: Your content & third-party training (via snippet)](https://support.google.com/youtube/answer/15509945?hl=en)

### Inferences
- The training opt-in covers training AI models. Producing descriptions with an inference API is not training, unless the provider retains or trains on submitted data, which depends on the AI provider's own data terms. The setting grants no download access either way, so it is mostly irrelevant to this use case.
- Using Gemini's YouTube URL feature means Google, which owns YouTube, does the fetching. The user then performs no download and no automated access to youtube.com. That arguably aligns better with the "expressly authorized by the Service" carve-out. No source found explicitly says this resolves ToS questions, so treat it as unconfirmed.
- The Developer Policies bind applications using YouTube API Services. A yt-dlp-based download is not an API use, but it falls under the general ToS download and automation prohibitions.

### Gaps
- Could not fetch the current YouTube ToS or Developer Policies to confirm effective dates, or the policy text on storing API data (e.g., 30-day refresh rules).
- Could not fetch Gemini's own terms text on YouTube URL processing. No source found states whether Google treats YouTube URL ingestion as compliant with YouTube's ToS for the caller.

## (e) Copyright and fair use; enforcement against youtube-dl/yt-dlp-style tools (to October 2026)

### Takeaway
The legal risk has shifted from copying (fair use) to anti-circumvention. US courts in 2026 have held at the pleading stage that YouTube's "rolling cipher" plausibly is an access control under DMCA §1201(a), and that §1201 liability is separate from fair use (Cordova v. Huneault, Feb 2026; Chmura/Ted Entertainment v. Snap, 2026; the Udio ruling, Apr 2026). Germany's youtube-dl/Uberspace case ended in October 2025 with the Federal Court of Justice (BGH) leaving the holdings in place. Those holdings say youtube-dl circumvents an effective technical protection measure and that hosting it creates liability. Personal analysis is not addressed directly by any ruling found. Redistributing verbatim transcripts carries clearer copyright risk than publishing original prose descriptions, but no source here specifically analyses that.

### Cited Findings
- **RIAA vs youtube-dl (2020, older):** the RIAA sent GitHub a DMCA takedown for youtube-dl in October 2020, alleging it circumvents YouTube's technological protections. GitHub reinstated the repo on 2020-11-16 after an EFF letter, which argued the tool did not circumvent DRM because the stream was not encrypted. GitHub then created a developer defense fund and said future §1201 claims would get manual review by legal and technical experts. — [EFF](https://www.eff.org/deeplinks/2020/11/github-reinstates-youtube-dl-after-riaas-abuse-dmca); [EFF letter PDF](https://www.eff.org/files/2020/11/17/eff_letter_to_github_re_youtube-dl_11152020.pdf); [Wikipedia: youtube-dl](https://en.wikipedia.org/wiki/Youtube-dl); [The Register](https://www.theregister.com/2020/11/16/github_restores_youtubedl/)
- **Germany, Uberspace:**
  - The German arms of Sony, Universal and Warner sued host Uberspace in early 2022 over hosting youtube-dl.org. The Hamburg Regional Court (LG) ruled against Uberspace at the end of March 2023. — [TorrentFreak 2023 (via snippet)](https://torrentfreak.com/music-labels-win-legal-battle-against-youtube-dls-hosting-provider-230404/); [heise](https://www.heise.de/en/news/OLG-Hamburg-Uberspace-liable-for-hosting-Youtube-DL-10179284.html)
  - The Hamburg Higher Regional Court (OLG) rejected the appeal on 2024-11-21. It held that youtube-dl bypasses YouTube's technological protections and that Uberspace could be held responsible. — [TorrentFreak (via snippet)](https://torrentfreak.com/court-rejects-appeal-of-youtube-dl-hosting-provider-uberspace-241127-1/)
  - heise headlined the decision: "Users of YouTube DL act in 'bad faith'". — [heise](https://www.heise.de/en/news/Hamburg-Higher-Regional-Court-Users-of-YouTube-DL-act-in-bad-faith-10181247.html)
  - The Hamburg court first treated YouTube's mechanism as an effective technical protection measure in 2017. — [CMU archive (via snippet)](https://archive.completemusicupdate.com/?p=217765)
  - In October 2025 the BGH rejected Uberspace's and the GFF's motion for leave to appeal (Nichtzulassungsbeschwerde). "All legal remedies have been exhausted and the case is concluded." — [GFF case page (via snippet)](https://freiheitsrechte.org/themen/starke-grundrechte-fuer-eine-lebendige-demokratie/uberspace-youtube-dl)
- **Cordova v. Huneault (California federal court, Feb 2026):** Judge DeMarchi held that "Mr. Cordova has adequately pled that YouTube applies technological measures, including 'rolling-cipher technology' designed to prevent unauthorized downloading, to videos published on its platform that effectively control access to his videos for purposes of § 1201(a)". Circumvention is a separate violation from infringement and is unaffected by a fair-use finding. This was a creator-vs-creator reaction-video dispute. — [TechSpot](https://www.techspot.com/news/111250-youtube-reaction-videos-could-face-lawsuits-over-ripped.html); [Slashdot](https://news.slashdot.org/story/26/02/05/1924252/court-rules-that-ripping-youtube-clips-can-violate-the-dmca); [TorrentFreak (via snippet)](https://torrentfreak.com/ripping-clips-for-youtube-reaction-videos-can-violate-the-dmca-court-rules/)
- **2026 creator class actions against AI companies:** filed against Meta (V-JEPA), Snap, Runway (by Ace Cam) and Amazon (Nova Reel), plus Apple (April 2026). Each alleges §1201 circumvention of YouTube's TPMs to scrape videos for training. — [Copyright Alliance, Feb 2026](https://copyrightalliance.org/copyright-stories-february-2026/); [The Next Web: Amazon suit](https://thenextweb.com/news/amazon-nova-reel-youtubers-dmca-lawsuit)
- **Snap ruling (C.D. Cal., Judge André Birotte Jr.):** the court denied Snap's motion to dismiss the DMCA claim (plaintiffs Ted Entertainment, Matt Fisher, Golfholics, Nicole Chmura). Snap argued there was no access barrier because videos are viewable without paying, authenticating or a password. The court found the creators plausibly alleged protective measures. Sigma Law's post is dated 2026-08-26. — [windowsforum summary](https://windowsforum.com/windows-news.4/snap-loses-bid-to-dismiss-youtube-ai-scraping-dmca-claim.443435/); [Sigma Law Group (via snippet)](https://sigmalawgroup.com/blog/2026-08-26-snap-dmca-scraping/)
- **Apple:** Apple moved to dismiss on 2026-07-02, arguing that publicly viewable videos are not "access-controlled" under §1201(a). The dispute concerns the Panda-70M dataset used to train Apple's STIV model. Undecided as of the sources found. — [AppleInsider](https://appleinsider.com/articles/26/07/03/apple-says-public-youtube-videos-can-be-used-in-ai-lawsuit-defense); [iThinkDiff](https://www.ithinkdiff.com/apple-youtube-dmca-ai-training-dismissal/)
- **Udio (SDNY, 2026-04-15):** Judge Hellerstein denied dismissal of the labels' DMCA anti-circumvention claim, which alleges that Udio circumvented YouTube's platform protections to download recordings. — [Sher Tremonte client alert (via snippet)](https://shertremonte.com/2026/05/11/client-alert-for-ai-companies-how-you-get-your-training-data-matters-sdny-allows-dmca-claim-to-proceed-against-ai-music-generator-udio/)
- **Technical enforcement (2025):**
  - yt-dlp announced (around 2025-09-25) that YouTube downloads will require an external JavaScript runtime, with Deno recommended because it is sandboxed and Node 21+ as an option. YouTube's JS challenges outgrew its built-in interpreter.
  - Some YouTube clients need PO tokens for sustained playback, and YouTube is forcing SABR streaming on some clients. — [GIGAZINE](https://gigazine.net/gsc_news/en/20250925-yt-dlp-deno-javascript-runtime); [yt-dlp issue #15043](https://github.com/yt-dlp/yt-dlp/issues/15043); [yt-dlp issue #15897](https://github.com/yt-dlp/yt-dlp/issues/15897)
- **Fair use in general:** fair use weighs purpose and transformativeness, amount used, and market effect. Commentary and criticism are classic fair uses. No source found analysed AI-generated scene descriptions or republished transcripts specifically. — [Univ. of Delaware: Copyright, Fair Use, and Content ID](https://www.udel.edu/edtech/youtube/modules/09-copyright.html); [US Copyright Office fair-use summary, Hosseinzadeh v. Klein (S.D.N.Y. 2017)](https://www.copyright.gov/fair-use/summaries/hosseinzadeh-klein-sdny2017.pdf)

### Inferences
- **Downloading is now the riskiest step,** separate from what is done with the content. Under the 2026 US pleading-stage rulings, ripping via yt-dlp-style tools can plausibly support a §1201(a) claim even when the end use is fair. All these rulings are early-stage (motions to dismiss), not final merits decisions. They were mostly brought against commercial bulk scrapers or republishers; no enforcement against an individual doing private analysis was found.
- **Lower-risk routes, in descending order of ToS alignment:**
  1. Gemini's YouTube URL feature: Google fetches the video and the user does not download.
  2. The user's own videos, or videos with permission, processed from local files.
  3. Transcript-only, using official captions.
  4. Local download with yt-dlp. This conflicts with the ToS text and, in Germany and in US pleading-stage rulings, raises circumvention issues.
- **Publishing:** original prose descriptions of what is on screen are more transformative and less substitutive than a verbatim transcript. Republishing full transcripts or many frames carries more copyright risk than private use. This is reasoning from general fair-use factors, not from a specific ruling.
- **Sending frames to a third-party AI API** is a copy transmitted to a processor. Whether that is fair use, or permitted under the ToS's "as expressly authorized by the Service" clause, is untested in the sources found. The AI provider's data-retention and training terms matter for the creator-consent question.

### Gaps
- No ruling found addressing individuals' personal, non-commercial downloading for analysis, or AI inference (not training) on YouTube frames.
- No final merits decision in the 2026 US §1201/YouTube cases as of October 2026. The Apple motion was pending per the sources found.
- Could not fetch the BGH decision itself (date, docket) or GFF's full statement. The October 2025 BGH outcome rests on a GFF-page snippet.
- No authoritative legal analysis (EFF or law firm) found specifically on whether Gemini's YouTube-URL ingestion changes a caller's ToS position.
