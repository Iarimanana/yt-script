# Hosted multimodal AI APIs (Gemini, Claude, OpenAI) for per-scene visual descriptions of YouTube videos — state as of 2026-10-04

> **Method / reliability note (read first).** Research date: 2026-10-04. The egress proxy in this environment blocked direct fetches of ai.google.dev, docs.cloud.google.com, blog.google, platform.openai.com, developers.openai.com, openai.com, arxiv.org, benchlm.ai, costgoat.com, medium.com and most aggregators. **Anthropic docs (platform.claude.com) and GitHub were fetched directly and are verbatim-reliable.** Google and OpenAI facts below come from web-search result summaries of the official pages (the URL cited is the page the search engine summarized) or from third-party pricing aggregators; these are marked **[search-summary]** or **[aggregator]** and should be re-verified against the official page before hard-coding numbers into the CLI. Anything I believe is older than 2026 is marked **[possibly outdated]**.

## 1. Google Gemini — native YouTube URL input, video sampling, tokens, limits, pricing, timestamp reliability

### Takeaway
Gemini is the only one of the three providers whose API ingests video directly, including a public YouTube URL passed as a `file_data`/`file_uri` part (still labelled **preview**, public videos only, 8 h/day of YouTube video on the free tier, no length cap on paid tier). It samples at 1 fps by default; on Gemini 3.x a video frame costs 70 tokens at low/medium `media_resolution` and 280 at high, so a 15-minute video is roughly 90k–280k input tokens, i.e. about **$0.05–$0.15 on Gemini 3 Flash, ~$0.16–$0.45 on Gemini 3.5 Flash, ~$0.22–$1.20 on Gemini 3.1 Pro** — but timestamps on YouTube-URL input are documented to drift, so timestamps should be validated or anchored.

### Cited Findings

**YouTube URL input (status, limits)**
- The Gemini API accepts YouTube URLs for video understanding; "the YouTube URL feature is in preview and is available at no charge," and "pricing and rate limits are likely to change." **[search-summary]** — [Gemini API: Video understanding](https://ai.google.dev/gemini-api/docs/video-understanding)
- Free tier: "you can't upload more than 8 hours of YouTube video per day"; paid tier: "no limit based on video length." **[search-summary]** — [Gemini API: Video understanding](https://ai.google.dev/gemini-api/docs/video-understanding)
- "For models prior to Gemini 2.5, you can upload only 1 video per request" (i.e., 2.5+ accept multiple videos per request). **[search-summary]** — [Gemini API: Video understanding](https://ai.google.dev/gemini-api/docs/video-understanding)
- Only **public** YouTube videos are accepted (not private or unlisted). **[search-summary]** — [Gemini API: Video understanding](https://ai.google.dev/gemini-api/docs/video-understanding); developers have an open request to allow unlisted videos — [Google AI Developers Forum: "Allow Gemini API to analyze unlisted YouTube videos"](https://discuss.ai.google.dev/t/request-allow-gemini-api-to-analyze-unlisted-youtube-videos/105083)
- The YouTube URL is passed "as a video part" via the `google-genai` Python SDK and AI Studio (issue reporter's description). — [googleapis/python-genai issue #1359](https://github.com/googleapis/python-genai/issues/1359)
- Public YouTube URLs also work with the newer **agentic video mode** (see below), via the Gemini API in Google AI Studio and the "Gemini Enterprise Agent Platform" (apparently the current name of Vertex AI's generative surface). **[search-summary]** — [Google blog: Introducing agentic video understanding with Gemini](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-agentic-video-in-gemini/); [Google Cloud docs: Video understanding (Gemini Enterprise Agent Platform)](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/video-understanding)

**Max length / context**
- "Models with a 1M context window can process videos up to 1 hour long at default media resolution or 3 hours long at low media resolution." **[search-summary]** — [Gemini API: Video understanding](https://ai.google.dev/gemini-api/docs/video-understanding)

**Sampling and tokens per second**
- Default pipeline: frames extracted at **1 fps**, audio at 1 Kbps mono, with a timestamp added every second. **[search-summary, possibly outdated — describes 1.5/2.x-era docs]** — [s-anand.net: How does Gemini process videos?](https://www.s-anand.net/blog/how-does-gemini-process-videos/)
- Classic (Gemini 2.x-era) token accounting: 258 tokens/frame at default media resolution or 66 tokens/frame at low, plus ~32 tokens/s audio ⇒ **~300 tokens per second of video (default) or ~100 tokens/s (low)**. **[search-summary, possibly outdated for Gemini 3.x]** — [s-anand.net](https://www.s-anand.net/blog/how-does-gemini-process-videos/); [Gemini API: Video understanding](https://ai.google.dev/gemini-api/docs/video-understanding)
- **Gemini 3.x**: video frames cost **70 tokens/frame at `media_resolution` low or medium** (treated identically for video, "sufficient for most action recognition and description tasks") and **280 tokens/frame at high** (recommended for text-heavy video). **[search-summary]** — [Gemini API: Media resolution](https://ai.google.dev/gemini-api/docs/media-resolution?hl=en); [Gemini 3 Developer Guide](https://ai.google.dev/gemini-api/docs/gemini-3?authuser=0)
- There is a developer-forum thread on best practices for video pre-processing with `media_resolution` on Gemini 3.0. — [Google AI Developers Forum thread 109808](https://discuss.ai.google.dev/t/best-practices-for-video-pre-processing-resolution-with-media-resolution-parameter-in-gemini-3-0/109808)
- Custom fps and clipping (`videoMetadata` with `fps`, `start_offset`, `end_offset`): I could not open the official page to confirm current field names/limits — see Gaps.

**Agentic video understanding (new in 2026)**
- "Agentic video understanding" was released for **Gemini 3.5 Flash-Lite** across the Interactions and GenerateContent APIs: the model navigates the video timeline on demand — searching transcripts, fetching targeted frame sequences at adaptive frame rates, isolating audio — rather than loading every frame upfront; Google claims **up to 88% fewer tokens** and **~7% higher quality on long-form content**. **[search-summary]** — [Google blog: Introducing agentic video understanding](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-agentic-video-in-gemini/); [AI Studio: Agentic video understanding developer guide](https://aistudio.google.com/learn/agentic-video-understanding-with-gemini); [howaiworks.ai: "Gemini Now Picks Which Parts of a Video to Watch"](https://howaiworks.ai/blog/google-gemini-agentic-video-2026)
- An independent write-up found agentic mode labelled a recurring scene at **10:41 when it was actually at 10:50**, repeatedly off by a large margin (timestamp drift). **[search-summary]** — [Han Qi, Medium: "Unlocking Gemini's Agentic Video Mode: Schema Design, Timestamp Drift…"](https://hanqi01.medium.com/unlocking-geminis-agentic-video-mode-schema-design-timestamp-drift-and-jay-chou-s-secret-215715dfcdb7)

**Files API vs inline vs YouTube URL**
- A third-party guide describes "3 methods for handling 100MB to 2GB videos" (inline vs Files API vs URL), and a search summary states Google "significantly boosted Gemini API's file handling capabilities" in January 2026. **[aggregator / search-summary — exact current limits not verified]** — [wentuo.ai guide](https://blog.wentuo.ai/en/gemini-large-video-understanding-api-guide-en.html); [Gemini API: Video understanding](https://ai.google.dev/gemini-api/docs/video-understanding)
- A reporter on python-genai found that **downloading the video and uploading it (Files API) produced accurate timestamps, while passing the YouTube URL directly produced drift**. — [googleapis/python-genai issue #1359](https://github.com/googleapis/python-genai/issues/1359)

**Current models and prices (per 1M tokens, paid tier, USD)**
- **Gemini 3.1 Pro**: $2.00 input / $12.00 output for prompts ≤200k tokens; $4.00 / $18.00 above 200k. **[aggregator, 2026]** — [morphllm Gemini API pricing](https://www.morphllm.com/gemini-api-pricing); [metacto: Gemini API Pricing May 2026](https://www.metacto.com/blogs/the-true-cost-of-google-gemini-a-guide-to-api-pricing-and-integration)
- **Gemini 3 Flash**: $0.50 input / $3.00 output. **[aggregator, 2026]** — [morphllm Gemini API pricing](https://www.morphllm.com/gemini-api-pricing); [pricepertoken: Gemini 3 Flash Preview](https://pricepertoken.com/pricing-page/model/google-gemini-3-flash-preview)
- **Gemini 3.5 Flash**: $1.50 input / $9.00 output; cached input $0.15; Batch ≈ $0.75 / $4.50 (~50% off); 1M context, ~66k max output. **[aggregator, May 2026]** — [devtk.ai: Gemini 3.5 Flash pricing](https://devtk.ai/en/models/gemini-3-5-flash/); [OpenRouter: Gemini 3.5 Flash](https://openrouter.ai/google/gemini-3.5-flash); [apidog: Gemini 3.5 Flash pricing](https://apidog.com/blog/gemini-3-5-flash-pricing/)
- **Gemini 3.5 Pro**: announced at Google I/O (May 19, 2026) but, per one aggregator, "has not shipped" and has no API price yet. **[aggregator — date of article unclear; re-check]** — [eesel.ai: Gemini 3.5 Pro pricing](https://www.eesel.ai/blog/gemini-3-5-pro-pricing)
- **Gemini Omni (1.1) Flash** is a video-*generation* model (preview Aug 27, 2026): $1.50/M input, $9/M text output, $17.50/M video output, with video **output** billed at 5,792 tokens per second of 720p. This "5,792 tokens/s" figure is for generated video and is **not** a video-input rate (one search summary conflated them). — [eesel.ai: Gemini Omni 1.1 Flash pricing](https://www.eesel.ai/blog/gemini-omni-1-1-flash-pricing)
- Official price table: [Gemini Developer API pricing](https://ai.google.dev/gemini-api/docs/pricing) (blocked here; could not confirm separate audio-input rates or thinking-token billing for 3.x).

**Timestamp reliability**
- python-genai #1359 (opened 2025-09-10, Gemini 2.5 Pro/Flash, YouTube URL input): timestamps drift **5–10 minutes over a 30-minute video** and output ended prematurely (~17 min of 30). Closed "not planned", no maintainer workaround. **[2025, possibly outdated for 3.x]** — [googleapis/python-genai issue #1359](https://github.com/googleapis/python-genai/issues/1359)
- Forum bug: **Gemini 3 Flash and 3.1 Pro** show *progressive* timestamp drift in audio transcription; an 11:49 clip was mapped onto 0:00–9:14 (model's clock ~22% too fast, drift grows linearly). **[search-summary]** — [Google AI Developers Forum: progressive timestamp drift (3 Flash / 3.1 Pro)](https://discuss.ai.google.dev/t/bug-gemini-3-flash-and-3-1-pro-progressive-timestamp-drift-in-audio-transcription/129501)
- Gemini 2.5 Pro: "severe timestamp/timecode jumping" in video transcription. **[2025]** — [Google AI Developers Forum thread 87242](https://discuss.ai.google.dev/t/gemini-2-5-pro-severe-timestamp-timecode-jumping-issues-in-video-transcription-need-workarounds/87242)

### Inferences
- **Token/cost estimate for a 15-minute (900 s) video at 1 fps, Gemini 3.x token rates** (frames + ~32 tok/s audio; audio rate taken from the older docs and assumed unchanged):
  - low/medium (70 tok/frame): 900 × (70 + 32) ≈ **91,800 input tokens**
  - high (280 tok/frame): 900 × (280 + 32) ≈ **280,800 input tokens**
  - legacy 2.x accounting: ~270,000 (default) / ~90,000 (low)
  - Assuming ~3,000 visible output tokens for ~40–60 scene entries (thinking tokens extra, billed as output):
    - Gemini 3 Flash: ≈ $0.046 + $0.009 ≈ **$0.055** (low) / ≈ $0.14 + $0.009 ≈ **$0.15** (high)
    - Gemini 3.5 Flash: ≈ $0.138 + $0.027 ≈ **$0.17** (low) / ≈ $0.42 + $0.027 ≈ **$0.45** (high)
    - Gemini 3.1 Pro: ≈ $0.18 + $0.04 ≈ **$0.22** (low) / high-res 280.8k tokens crosses the 200k tier ⇒ ≈ $1.12 + $0.05 ≈ **$1.18**
    - Batch mode roughly halves these. If the YouTube-URL path is truly "no charge" during preview, cost could be lower still — but that phrase is ambiguous (see Gaps).
- For a CLI, the YouTube-URL path removes the need to download the video (no yt-dlp/ffmpeg), which is a large practical advantage; the cost is weaker timestamp accuracy and dependency on a preview feature that only works for public videos.
- A robust pattern is to **chunk the video with start/end offsets (e.g., 2–5 min windows) and ask for timestamps relative to the window**, then add the offset in code; this bounds drift. This is an engineering inference from the drift reports, not a documented Google recommendation.
- Low/medium resolution (70 tok/frame) should be fine for scene/setting/action descriptions; switch to high (280) only if on-screen text (slides, captions, code) must be read.

### Gaps
- Could not open ai.google.dev to confirm: the exact current list of models that accept YouTube URLs (assumed all Gemini 2.5+/3.x), the max number of YouTube URLs per request on 2.5+/3.x (older docs said up to 10 — unverified), exact `videoMetadata` field names (`fps`, `start_offset`, `end_offset`) and allowed fps range, the MM:SS timestamp prompting guidance, inline-request size limit (was 20 MB, reportedly raised in Jan 2026) and Files API limits (2 GB/file, 48 h retention in older docs).
- "Available at no charge" for YouTube URLs: unclear whether the video tokens are free or only the URL-fetching feature is free. Needs confirming against a billed request.
- No official per-model audio-input price for Gemini 3.x found (2.5 Flash historically charged more for audio).
- No published quantitative temporal-grounding accuracy (e.g., Charades-STA mIoU) for Gemini 3.x found in this session.

## 2. Anthropic Claude — image-only input, limits, token formula, pricing, batches/caching, 60-keyframe cost

### Takeaway
Claude has **no video input**; you must extract keyframes yourself and send them as `image` blocks (base64, URL, or Files API `file_id`), up to **600 images per request** on 1M-context models (100 on 200k-context models), 32 MB request cap. Image cost is now **⌈w/28⌉ × ⌈h/28⌉ visual tokens** (the old `w·h/750` formula is outdated). Sixty 1280×720 keyframes ≈ 72k image tokens ⇒ roughly **$0.11 (Haiku 4.5), $0.21 (Sonnet 5/5.5), $0.43 (Opus 5.5)** per video including prompt and output, halved with the Batch API.

### Cited Findings

**Input mechanics and limits (fetched verbatim, 2026-10-04)**
- Images are sent as `image` content blocks via three source types: base64, URL, or `file_id` from the Files API; on Bedrock and Google Cloud only base64 is available. — [Claude docs: Vision](https://platform.claude.com/docs/en/build-with-claude/vision)
- Max images: **20 per message on claude.ai; 100 per API request for models with a 200k-token context window; 600 per API request for all other models.** Max dimensions 8000×8000 px. — [Claude docs: Vision](https://platform.claude.com/docs/en/build-with-claude/vision)
- If a request contains **more than 20 images**, a stricter per-image dimension limit applies ("many-image requests"); to be safe, keep each image ≤ **2000 px** on both sides or send ≤20 images. — [Claude docs: Vision](https://platform.claude.com/docs/en/build-with-claude/vision)
- Max size per image: 10 MB base64 on the Claude API (5 MB on Bedrock/Google Cloud); request size limit **32 MB** for standard endpoints can be reached before 600 images — Files API recommended for many images. — [Claude docs: Vision](https://platform.claude.com/docs/en/build-with-claude/vision)
- Formats: JPEG, PNG, GIF, WebP; animations unsupported (first frame only). Claude does not read image metadata (so EXIF/timecodes must be given as text). — [Claude docs: Vision](https://platform.claude.com/docs/en/build-with-claude/vision)

**Token formula and resolution**
- Current formula: Claude "views images in patches"; each patch is 28×28 px, so an image costs **`⌈width/28⌉ × ⌈height/28⌉` visual tokens**. — [Claude docs: Vision](https://platform.claude.com/docs/en/build-with-claude/vision)
- Resolution tiers: **High-resolution (Claude 4.7 and later models): max long edge 2576 px, max 4,784 visual tokens. Standard (all other models): 1568 px, 1,568 tokens.** Larger images are downscaled preserving aspect ratio. — [Claude docs: Vision](https://platform.claude.com/docs/en/build-with-claude/vision)
- Worked examples from the docs: 1000×1000 → 1,296 tokens (both tiers); **1920×1080 → 1,560 tokens (standard, downsized to 1456×819) or 2,691 tokens (high-res, not resized)**; 3840×2160 → 1,560 (standard) / 4,784 (high-res). — [Claude docs: Vision](https://platform.claude.com/docs/en/build-with-claude/vision)
- Docs' cost examples: 1000×1000 image ≈ $1.30 per thousand images on Haiku 4.5; ≈ $6.48/thousand on Opus 5 (high-res tier); a 4K image ≈ $23.92/thousand on Opus 5. High-res can use ~3× the tokens of standard tier; "downsample images before sending to control token costs." — [Claude docs: Vision](https://platform.claude.com/docs/en/build-with-claude/vision)
- The `w·h/750` formula requested in the brief is the **older** rule **[outdated]**; the 28-px-patch rule (784 px²/token) gives similar numbers but is what the current docs specify. — [Claude docs: Vision](https://platform.claude.com/docs/en/build-with-claude/vision)

**Multi-image guidance and limitations**
- Multiple images in one request are "analyzed jointly", useful "for working with a sequence"; docs recommend labelling each image (`Image 1:`, `Image 2:` …) and placing images before the text question. — [Claude docs: Vision](https://platform.claude.com/docs/en/build-with-claude/vision)
- Documented limitations: will not identify people by name; may hallucinate on low-quality, rotated, or <200 px images; approximate spatial reasoning and counting; heavy JPEG compression can make text unreadable. — [Claude docs: Vision](https://platform.claude.com/docs/en/build-with-claude/vision)

**Pricing (per 1M tokens, USD, fetched 2026-10-04)**

| Model | Input | Output | Batch in/out | Cache hit |
|---|---|---|---|---|
| Claude Fable 5.1 | $10 | $50 | $5 / $25 | $0.25 |
| Claude Opus 5.5 | $4 | $20 | $2 / $10 | $0.20 |
| Claude Opus 5 / 4.8 / 4.7 / 4.6 / 4.5 | $5 | $25 | $2.50 / $12.50 | $0.50 |
| Claude Sonnet 5.5 | $2 | $10 | $1 / $5 | $0.20 |
| Claude Sonnet 5 | $2 | $10 | $1 / $5 | $0.20 |
| Claude Sonnet 4.6 / 4.5 | $3 | $15 | $1.50 / $7.50 | $0.30 |
| Claude Haiku 4.5 | $1 | $5 | $0.50 / $2.50 | $0.10 |
— [Claude docs: Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- Sonnet 5's $2/$10 introductory price became the standard price; the planned Sept 1, 2026 rise to $3/$15 "will not occur." — [Claude docs: Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- **Batch API: 50% discount** on input and output; stacks with prompt caching. — [Claude docs: Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- **Prompt caching**: 5-min write 1.25× base input, 1-h write 2×, cache hit 0.1× (0.05× on Opus 5.5; 0.025× on Fable/Mythos 5.1). — [Claude docs: Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- Claude 4.6+ models include the full **1M-token context at standard pricing** (no long-context surcharge). — [Claude docs: Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- Claude 4.7+ use a newer tokenizer producing ~30% more tokens for the same **text**. — [Claude docs: Pricing](https://platform.claude.com/docs/en/about-claude/pricing)

### Inferences
- **60 keyframes at 1280×720**: ⌈1280/28⌉ × ⌈720/28⌉ = 46 × 26 = **1,196 tokens/frame** (no downscale on either tier) ⇒ 71,760 image tokens. Adding ~5,000 tokens of instructions + transcript and ~6,000 output tokens (≈100 tokens per scene):
  - Haiku 4.5: ≈ $0.077 + $0.030 ≈ **$0.11** (batch ≈ $0.05)
  - Sonnet 5 / 5.5: ≈ $0.154 + $0.060 ≈ **$0.21** (batch ≈ $0.11)
  - Sonnet 4.6: ≈ $0.230 + $0.090 ≈ **$0.32**
  - Opus 5.5: ≈ $0.307 + $0.120 ≈ **$0.43** (batch ≈ $0.21)
  - Opus 5: ≈ $0.384 + $0.150 ≈ **$0.53**
  - Fable 5.1: ≈ $0.77 + $0.30 ≈ **$1.07**
- At 1920×1080 on a high-res-tier model (4.7+), each frame is 2,691 tokens (≈2.25× more); at 768×432 it is 28 × 16 = 448 tokens. Downscaling keyframes to ~1024–1280 px wide is the main cost lever.
- With 60 frames you exceed 20 images, so keep frames ≤2000 px per side. 60 JPEGs at 1280×720 (~100–200 KB each) fit under the 32 MB request cap even as base64.
- Since Claude cannot see the timecode of a frame, the CLI must interleave a text label like `Frame 12 @ 03:41` before each image; this makes timestamps exact by construction (they come from ffmpeg, not the model), which sidesteps Gemini-style drift.
- Prompt caching helps if you split frames across several requests that share a long system prompt + transcript, or if you ask follow-up questions over the same frames.

### Gaps
- No published, Claude-specific benchmark of multi-image *sequence* description quality (e.g., ordered keyframes → scene captions) was found in this session; see Q4 for third-party Video-MME numbers that include Claude (frames-based).
- Whether `claude-haiku-4-5` is on the high-res or standard tier: the docs say high-res is "Claude 4.7 and later", so Haiku 4.5 and Sonnet 4.5/4.6 are standard tier; Sonnet 5/5.5 and Opus 4.7+ are high-res (inference from the tier rule, not an explicit per-model table).

## 3. OpenAI GPT — vision models, video support, image token costs, limits, Batch, 60-keyframe cost

### Takeaway
No OpenAI API accepts video (a March 2026 SDK feature request for native video input was closed "not planned"); you send frames as images. Current flagships are **GPT-5.5 ($5/$30)** and the **GPT-5.6 family** (reported as Sol $5/$30, Terra $2/$12, Luna $0.20/$1.20), plus GPT-5.4-mini/nano; Batch is 50% off. Images are billed by 32×32-px patches (GPT-5.5 "high" detail caps at 2,500 patches / 2048 px), so 60 frames at 1280×720 ≈ 55k image tokens ⇒ roughly **$0.48 on GPT-5.5** (≈$0.24 batch) or a few cents on mini/nano tiers.

### Cited Findings

**Video support**
- "There is no video input path in any OpenAI API"; vision only accepts arrays of frames, without audio. **[search-summary; vendor blog with competing product]** — [Primate Intelligence: Primate Vision vs. OpenAI (2026)](https://primateintelligence.ai/blog/primate-vision-vs-openai)
- GitHub feature request "Native video file input support in Responses API (parity with Google Gemini…)" opened **2026-03-18**, noting "nearly 2 years later, the API still has no video input support"; status **closed as not planned**. — [openai/openai-node issue #1778](https://github.com/openai/openai-node/issues/1778)
- ChatGPT (consumer app) reportedly accepts MP4/MOV/WebM uploads with GPT-5.5, which is distinct from the API. **[search-summary, low-authority source]** — [framia.converge.ai: GPT-5.5 multimodal capabilities](https://framia.converge.ai/page/en-US/news/gpt-5-5-multimodal-capabilities)
- Common workaround: feed a video "as a sequence of JPEG frames" to a vision LLM (e.g., Simon Willison's `llm-video-frames` plugin). **[2025]** — [Simon Willison: Feed a video to a vision LLM as a sequence of JPEG frames](https://simonwillison.net/2025/May/5/llm-video-frames/)

**Image token accounting**
- Images are covered by **32×32-px patches**: `patches = ceil(width/32) × ceil(height/32)`; if over the model's patch budget or max dimension, the image is resized proportionally and recounted; a per-model token multiplier is then applied (example uses 1.2×). **[search-summary]** — [OpenAI: Image input token and cost calculator](https://developers.openai.com/api/docs/guides/image-cost-calculator)
- **GPT-5.5**: `detail: "high"` allows up to **2,500 patches or 2,048 px** max dimension; `detail: "original"` allows up to **10,000 patches or 6,000 px**. **[search-summary]** — [OpenAI: Image input token and cost calculator](https://developers.openai.com/api/docs/guides/image-cost-calculator)
- `detail: "low"` processes the image "with a budget of 85 tokens". **[search-summary; possibly outdated — this is the tile-based rule from GPT-4o-era docs]** — [OpenAI: Images and vision guide](https://developers.openai.com/docs/guides/images-vision)
- Limits: current docs reportedly allow **up to 1,500 image inputs per request with a 512 MB total payload**; older docs said 500 images / 50 MB. **[search-summary — conflicting versions]** — [OpenAI: Images and vision guide](https://developers.openai.com/api/docs/guides/images-vision/index.html); older figure via [Databricks: Query vision models](https://docs.databricks.com/aws/en/machine-learning/model-serving/query-vision-models)

**Models and pricing (per 1M tokens, USD)**
- **GPT-5.5**: $5.00 input, $0.50 cached input, $30.00 output; accepts file, image, text input. **[aggregator, 2026]** — [OpenRouter: GPT-5.5](https://openrouter.ai/openai/gpt-5.5); [metacto: OpenAI API Pricing May 2026](https://www.metacto.com/blogs/unlocking-the-true-cost-of-openai-api-a-deep-dive-into-usage-integration-and-maintenance)
- **GPT-5.6** family: "Sol" $5/$30, "Terra" $2/$12, "Luna" $0.20/$1.20; long-context rates Sol $10/$45, Terra $4/$18, Luna $0.40/$1.80. **[aggregator — not verified against openai.com]** — [morphllm: OpenAI API pricing](https://www.morphllm.com/openai-api-pricing)
- **GPT-5.4-mini**: $0.75 in / $0.075 cached / $4.50 out; **GPT-5.4-nano**: $0.20 / $0.02 / $1.25. **[aggregator]** — [morphllm: OpenAI API pricing](https://www.morphllm.com/openai-api-pricing)
- **Batch API: 50% off** (e.g., GPT-5.5 $2.50/$15). **[aggregator]** — [morphllm: OpenAI API pricing](https://www.morphllm.com/openai-api-pricing)
- Conflict: another aggregator's page title references "GPT-6.1 Sol & Astra" pricing — I could not open it; the naming of OpenAI's newest flagship as of Oct 2026 is **unverified**. — [aipricing.guru: OpenAI pricing](https://www.aipricing.guru/openai-pricing/)

### Inferences
- **60 keyframes at 1280×720 on GPT-5.5 (high detail)**: ceil(1280/32) × ceil(720/32) = 40 × 23 = **920 patches/frame** (under the 2,500 cap, no resize) ⇒ 55,200 image tokens × multiplier (assume 1.0 for the flagship; unknown). With ~5,000 prompt tokens and ~6,000 output tokens:
  - GPT-5.5 / GPT-5.6 Sol: ≈ $0.30 + $0.18 ≈ **$0.48** (batch ≈ $0.24)
  - GPT-5.6 Terra: ≈ $0.12 + $0.07 ≈ **$0.19**
  - GPT-5.4-mini: ≈ $0.045 + $0.027 ≈ **$0.07** before any image multiplier (mini/nano models historically carry multipliers >1×, so treat as a lower bound)
  - GPT-5.4-nano / GPT-5.6 Luna: ≈ **$0.02**, lower bound
  - `detail: "low"` (85 tok/frame if still applicable): 60 × 85 = 5,100 tokens — very cheap but too coarse for on-screen text.
- OpenAI and Claude per-frame token counts are similar (920 vs 1,196 for 720p); the cost difference is driven mainly by per-token price and output price.
- As with Claude, timestamps come from the frame extractor, so accuracy is exact by construction; the model only has to describe frames.

### Gaps
- Could not open OpenAI's official pricing or vision pages; the exact per-model image-token multipliers for GPT-5.5/5.6/5.4-mini/nano, whether `low` is still 85 tokens under the patch scheme, and the 1,500-image/512 MB limit all need confirming against the official page.
- The identity of the current OpenAI flagship (GPT-5.5 vs GPT-5.6 Sol vs "GPT-6.1") is inconsistent across aggregators.

## 4. Benchmarks (Video-MME etc.) and known failure modes

### Takeaway
On video benchmarks Gemini leads (it ingests video + audio natively); GPT and Claude are evaluated on sampled frames and score lower. Even the best model is far below humans on the stricter Video-MME-v2. The most relevant failure mode for per-scene descriptions is **timestamp drift on Gemini** (documented on 2.5, 3 Flash, 3.1 Pro, and agentic mode); the frames-based approach (Claude/OpenAI) avoids drift but can miss motion between sampled frames.

### Cited Findings
- **Video-MME-v2** (released **2026-04-07**, >3,300 human-hours of annotation): Gemini-3-Pro and Gemini-3-Flash reach **66.1% and 61.1%** average accuracy, but their grouped non-linear scores (which require answering all related questions in a group correctly) are only **49.4 and 42.5**; "even SOTA models rarely answer all related questions in a group correctly." Evaluation modes include 64-frame sampling, 1 fps, subtitles concatenated or interleaved. — [GitHub: MME-Benchmarks/Video-MME-v2](https://github.com/MME-Benchmarks/Video-MME-v2)
- Video-MME-v2 non-linear score: **GPT-5 = 37.0** vs Gemini-3-Pro 49.4; human experts **90.7**. **[search-summary of the paper]** — [arXiv 2604.05015: Video-MME-v2](https://arxiv.org/html/2604.05015v1)
- Third-party compilations (search summaries; I could not open the pages to confirm which page reported which number or the evaluation settings):
  - VideoMME long-form: Gemini 3 Deep Think 78.4%, **GPT-5.5 71.2%, Claude Opus 4.7 67.8%** — [Digital Applied: Multimodal AI Benchmarks 2026](https://www.digitalapplied.com/blog/multimodal-ai-benchmarks-2026-vision-audio-code)
  - VideoMME: **Gemini 3.1 Pro Preview 87.2%, GPT-5.1 81.3%, Claude Opus 4.5 79.2%** — [WhatLLM: Gemini 3.1 Pro Preview benchmarks](https://whatllm.org/blog/gemini-3-1-pro-preview); [Vellum: GPT-5.1 vs Gemini 3 Pro vs Claude Opus 4.5](https://www.vellum.ai/blog/flagship-model-report)
  - Leaderboards: [llm-stats Video-MME](https://llm-stats.com/benchmarks/video-mme); [benchmarklist Video-MME](https://benchmarklist.com/benchmarks/video_mme/); [benchlm VideoMMMU (Sept 2026)](https://benchlm.ai/benchmarks/videommmu)
- Gemini 3 Flash / 3.1 Pro: progressive timestamp drift, ~22% clock error (11:49 audio mapped to 0:00–9:14). — [Google AI Developers Forum](https://discuss.ai.google.dev/t/bug-gemini-3-flash-and-3-1-pro-progressive-timestamp-drift-in-audio-transcription/129501)
- Gemini 2.5 Pro/Flash on YouTube URLs: 5–10 min drift over 30 min; uploading the file instead fixed it for the reporter. — [googleapis/python-genai #1359](https://github.com/googleapis/python-genai/issues/1359)
- Gemini agentic video mode: a recurring scene labelled 10:41 vs actual 10:50. — [Han Qi, Medium](https://hanqi01.medium.com/unlocking-geminis-agentic-video-mode-schema-design-timestamp-drift-and-jay-chou-s-secret-215715dfcdb7)
- Earlier models: Gemini 1.5 Flash-002 "completely hallucinates timestamps" in audio transcription **[2024, outdated]** — [google-gemini/deprecated-generative-ai-js #269](https://github.com/google-gemini/deprecated-generative-ai-js/issues/269); Gemini 2.0 forced-alignment timestamps "still broken" **[2025]** — [Google AI Developers Forum thread 79553](https://discuss.ai.google.dev/t/timestamp-generation-forced-alignment-on-2-0-production-models-is-still-broken/79553)
- Frame-extraction workaround (OpenAI/Claude) "loses audio, temporal context, and motion." **[vendor blog]** — [Primate Intelligence](https://primateintelligence.ai/blog/primate-vision-vs-openai)
- Claude: hallucination risk on low-quality/small images; approximate counting/spatial reasoning; heavy compression harms text legibility (OCR). — [Claude docs: Vision](https://platform.claude.com/docs/en/build-with-claude/vision)
- Gemini 3 guidance: use `media_resolution` high (280 tok/frame) for text-heavy video, implying OCR degrades at the 70-token default. **[search-summary]** — [Gemini API: Media resolution](https://ai.google.dev/gemini-api/docs/media-resolution?hl=en)

### Inferences
- Video-MME numbers measure QA, not dense captioning with timestamps; they show Gemini understands whole videos (with audio) best, but they don't directly measure per-scene timestamp precision.
- For a "describe each scene with timestamps" CLI, a hybrid is attractive: detect scene boundaries locally (e.g., PySceneDetect / ffmpeg scene filter), so timestamps are exact, then send each scene's keyframe(s) (Claude/OpenAI) or the scene's clip via start/end offsets (Gemini) for description.
- 1 fps sampling means very short shots (<1 s, fast cuts in music videos/trailers) may be skipped by Gemini's default sampling; raising fps (if supported) or local scene detection mitigates this.

### Gaps
- No credible, current (2026) head-to-head on **temporal localization / dense video captioning** (e.g., Charades-STA, ActivityNet Captions, YouCook2) for Gemini 3.x vs GPT-5.x vs Claude 5.x was found.
- Claude-specific Video-MME results are only from third-party compilations whose frame-sampling settings are unknown.
- No quantitative OCR-on-video benchmark per provider was found.

## 5. Prompting patterns for per-scene description

### Takeaway
The patterns that the sources support are: label each frame with its index and timestamp, put images before the instruction, request structured JSON per scene (timestamp, shot type, setting, people/actions, on-screen text), raise image resolution only where text must be read, and for Gemini, bound timestamps by chunking. Giving the transcript as context is useful but should be marked as audio context so the model doesn't "describe" what is only said.

### Cited Findings
- Claude: introduce each image with a short text label (`Image 1:` …) to refer to them by name; images before text works best; Claude analyzes multiple images jointly for sequences. — [Claude docs: Vision](https://platform.claude.com/docs/en/build-with-claude/vision)
- Claude does not parse image metadata, so frame timestamps must be provided as text. — [Claude docs: Vision](https://platform.claude.com/docs/en/build-with-claude/vision)
- Gemini 3: low/medium resolution (70 tok/frame) is "sufficient for most action recognition and description tasks"; high (280) for text-heavy video. **[search-summary]** — [Gemini API: Media resolution](https://ai.google.dev/gemini-api/docs/media-resolution?hl=en)
- A Medium write-up on Gemini agentic video mode focuses on **response-schema design** for timestamped output and on timestamp drift. **[title/summary only]** — [Han Qi, Medium](https://hanqi01.medium.com/unlocking-geminis-agentic-video-mode-schema-design-timestamp-drift-and-jay-chou-s-secret-215715dfcdb7)
- Video-MME-v2 evaluates subtitle integration "concatenated or interleaved" with frames, i.e., transcript-as-context is a standard evaluation condition. — [GitHub: MME-Benchmarks/Video-MME-v2](https://github.com/MME-Benchmarks/Video-MME-v2)
- Reporter found accurate timestamps when the video was uploaded rather than passed as a YouTube URL. — [googleapis/python-genai #1359](https://github.com/googleapis/python-genai/issues/1359)

### Inferences
- Suggested JSON schema per scene (works with Gemini `response_schema`, Claude structured outputs/tool schema, OpenAI Structured Outputs — structured-output support itself was not re-verified in this session): `{start: "MM:SS", end: "MM:SS", shot_type: "wide|medium|close-up|screen-recording|b-roll|…", setting, people: [{description, action}], objects, on_screen_text, camera_motion, visual_summary, confidence}`.
- For Claude/OpenAI, interleave `Frame k — t=MM:SS (scene n)` labels with images and instruct the model to copy, not invent, timestamps; send 20–60 frames per call to keep the request small and provide local context (adjacent frames) for continuity.
- For Gemini, ask for timestamps in MM:SS and either (a) process in 2–5 minute windows with start/end offsets and add offsets in code, or (b) provide your own scene boundaries and ask the model only to describe each span.
- Provide the transcript (with timestamps) as separate, clearly labelled context and instruct: "describe only what is visible; use the transcript only to disambiguate names/terms" — reduces hallucinated visual details sourced from speech.
- Ask explicitly for `on_screen_text` verbatim and allow `null`; use higher resolution frames (or Gemini `media_resolution: high`) only for scenes flagged as text-heavy to control cost.

### Gaps
- No official Google page on prompting for timestamped scene descriptions (MM:SS guidance) could be fetched in this session.
- No controlled study found comparing "transcript-as-context" vs "frames-only" on hallucination rates for scene description.
