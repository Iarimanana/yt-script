# Managed Cloud Video-Analysis Services for Per-Scene/Shot Description (state as of 2026-10-04)

Research method note: most vendor domains (twelvelabs.io, docs.twelvelabs.io, aws.amazon.com, learn.microsoft.com, docs.cloud.google.com) were blocked for direct page fetches from this environment, so nearly every finding below comes from web-search result extractions that quote those official pages. URLs point to the original official page where the search attributed the fact to it. Treat every price as "observed via search, 2026-10-04" and confirm on the live pricing page before you rely on it. Flags: **[VERIFY]** = single or indirect source, or sources conflict; **[RETIRED/DEPRECATED]** = status warning.

---

## 1. Google Cloud Video Intelligence API (features, pricing, input, status)

### Takeaway
The Video Intelligence API still offers per-shot boundaries, labels, OCR, and object tracking for $0.05–$0.15/min after 1,000 free minutes per feature per month. However, it is reportedly **officially deprecated as of 2026-09-14, with shutdown on 2027-09-14**, and Google directs users to Gemini. Do not build anything new on it. It never produced natural-language scene descriptions anyway.

### Cited Findings
- **[RETIRED/DEPRECATED] [VERIFY]** "Starting on September 14, 2026, Video Intelligence API is officially deprecated and will no longer be supported. You can continue using Video Intelligence API until September 14, 2027, when it will be shut down." Google recommends migrating to the Gemini family of models. — [Video Intelligence API Deprecations](https://docs.cloud.google.com/video-intelligence/docs/deprecations) (returned by two separate searches, also tied to the [Support](https://docs.cloud.google.com/video-intelligence/docs/support) and [docs home](https://docs.cloud.google.com/video-intelligence/docs) pages). A third search could not find this notice and said the deprecations page was "last updated March 2026", which may be a stale index. I could not fetch the page directly.
- **[RETIRED]** Celebrity Recognition was deprecated on 2024-09-16 and stopped being available on Google Cloud after 2025-09-16. — [Video Intelligence API Deprecations](https://docs.cloud.google.com/video-intelligence/docs/deprecations)
- Pricing is per minute, and partial minutes round up to the next full minute. — [Video Intelligence API pricing](https://cloud.google.com/video-intelligence/pricing)
  - Shot change detection: first 1,000 min/month free, then **$0.05/min**. — [pricing](https://cloud.google.com/video-intelligence/pricing)
  - Label detection: first 1,000 min free, then **$0.10/min**. — [pricing](https://cloud.google.com/products/video-intelligence/pricing)
  - Object tracking: first 1,000 min free, then **$0.15/min**. — [pricing](https://cloud.google.com/products/video-intelligence/pricing)
  - Text detection (OCR): first 1,000 min free, then **$0.15/min**. — [pricing](https://cloud.google.com/products/video-intelligence/pricing)
  - Above 100,000 min/month, contact sales for discounts. — [pricing](https://cloud.google.com/products/video-intelligence/pricing)
- Input: the API annotates "videos stored locally or in Cloud Storage, or live-streamed". A third-party assessment says the streaming feature has been in beta since 2019. — [Video Intelligence API documentation](https://docs.cloud.google.com/video-intelligence/docs) (search extraction)
- There is still an AutoML Video / Vertex AI video-classification doc trail. Google's own migration guidance points to Gemini models. — [Vertex AI deprecations](https://docs.cloud.google.com/vertex-ai/docs/deprecations); [Migrate to the latest Gemini models](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/migrate)

### Inferences
- Cost for a 15-min video, beyond the free tier: shot detection $0.75, labels $1.50, text $2.25, object tracking $2.25, so **≈$6.75 for all four**. Inside the 1,000 free min/month per feature, a hobby CLI pays **$0**.
- Based on the v1 API reference structure, the output is machine metadata: shot start/end time offsets, label entities with segment/shot/frame confidences, OCR text with time segments, and object tracks with bounding boxes. It has **no natural-language scene descriptions**. You would need an LLM step on top.
- Input in practice is a `gs://` URI, or inline bytes for small files. A YouTube video would have to be downloaded and re-uploaded (see the ToS discussion in section 6).
- With the deprecation, the replacement is Gemini (section 5), which can do shot listing plus per-scene descriptions from a prompt.

### Gaps
- I could not open the deprecations page directly to quote it verbatim. The 2026-09-14 date rests on search extractions, and one search contradicted it.
- I did not confirm current prices for face detection, person detection, logo recognition, explicit content, or speech transcription.
- I did not find the exact max file size or duration limits.

---

## 2. Twelve Labs (Pegasus / Marengo): models, APIs, YouTube input, pricing, limits

### Takeaway
Twelve Labs is the most purpose-built "describe video with timestamps" API. **Pegasus 1.5** (video-to-text) takes a natural-language segment definition plus a JSON schema and returns **timestamped, structured per-segment metadata** for videos up to about 2 hours, with no pre-indexing. **Marengo 3.0/3.5** handles embeddings and search. It **does not accept YouTube URLs**, so you need direct raw-file URLs or uploads. A 15-min analysis costs roughly **$0.30–$0.35** pay-as-you-go, and the free plan includes 600 minutes.

### Cited Findings
- **Pegasus 1.5** adds "Time Based Metadata Extraction (TBM)": you define a custom JSON schema and get **timestamped, structured metadata** from videos **up to two hours long**, "with no ingestion pipeline, no preprocessing, and no indexing step." — [Building Pegasus 1.5 (TwelveLabs blog)](https://www.twelvelabs.io/blog/introducing-pegasus-1-5); [PRWeb launch release](https://www.prweb.com/releases/twelvelabs-launches-pegasus-1-5--turning-raw-video-into-structured-queryable-data-at-scale-302746725.html)
- Pegasus 1.5 uses a schema-first `/analyze` API. Developers write **segment definitions**: a semantic description of what counts as a segment, the metadata fields to extract, and optional constraints such as duration. Per-definition time ranges are supported. — [Video Segmentation API blog](https://www.twelvelabs.io/blog/video-segmentation-api-how-to-extract-structured-data-from-video); [Pegasus model docs](https://docs.twelvelabs.io/docs/concepts/models/pegasus)
- Pegasus 1.5 outputs "scene boundaries, entities, temporal segments, and semantic context". — [Pegasus 1.5 page](https://www.twelvelabs.io/pegasus); [Product Hunt "making of"](https://www.producthunt.com/p/twelvelabs/pegasus-1-5-by-twelvelabs-the-making-of)
- Pegasus 1.5 can analyze video "directly from a URL, asset, or base64 string, with no pre-indexing required". **Batch analysis** (Pegasus 1.5 only) accepts up to 1,000 video analysis requests in one call. — [Pegasus docs](https://docs.twelvelabs.io/docs/concepts/models/pegasus); [Release notes](https://docs.twelvelabs.io/docs/get-started/release-notes)
- A migration guide from Pegasus 1.2 to 1.5 exists, which suggests 1.2 is the legacy model. — [Migrate from Pegasus 1.2 to 1.5](https://docs.twelvelabs.io/docs/get-started/migration-guides/pegasus-1-2-to-1-5)
- Duration limits: the synchronous `/analyze` endpoint supports videos up to **1 hour**, and the asynchronous `/analyze/tasks` endpoint supports up to **2 hours**. Public video URLs can be up to **2 GB**. — [Analyze videos guide](https://docs.twelvelabs.io/docs/guides/analyze-videos); [Analyze API reference](https://docs.twelvelabs.io/api-reference/analyze-videos/analyze)
- **YouTube is not supported**: "The ability to upload videos from YouTube is no longer supported." Video-hosting platforms and cloud-storage sharing links are also rejected. URL uploads must be "direct links to raw video files that play without user interaction or custom video players." — [Upload and manage videos (docs)](https://docs.twelvelabs.io/docs/resources/playground/upload-and-manage-videos)
- **Marengo 3.0** was announced 2025-12-01 at AWS re:Invent and is GA on the TwelveLabs API and **Amazon Bedrock**. It supports videos **up to 4 hours**, has 50% smaller embeddings, indexes 2x faster, and adds composed image+text search and entity search. Vendor-reported composite benchmark: 78.5% vs 61.8% for Amazon Nova and 50.2% for Google Vertex. — [AIwire/HPCwire](https://www.hpcwire.com/aiwire/2025/12/01/twelvelabs-launches-marengo-3-0-video-understanding-model-on-twelvelabs-and-amazon-bedrock/); [Amazon press center](https://press.aboutamazon.com/aws/2025/12/twelvelabs-launches-its-most-powerful-video-understanding-model-marengo-3-0-on-twelvelabs-and-amazon-bedrock)
- **Marengo 3.5** exists and adds "time-based metadata fusion". Timestamped text is billed on the text meter. — [Marengo 3.5 blog](https://www.twelvelabs.io/blog/marengo-3.5) **[VERIFY: release date not found]**
- Pricing on the Developer / pay-as-you-go plan (search extractions of the official pricing page):
  - Pegasus analysis: **input video $0.021/min**, **output text $0.0075 per 1K tokens**, plus indexing and infrastructure charges. — [TwelveLabs Pricing](https://www.twelvelabs.io/pricing)
  - The older listing, likely Pegasus 1.2, showed indexing at $0.042/min and infrastructure at $0.0015/min/month. — [SaaSworthy (Sept 2026)](https://www.saasworthy.com/product/twelvelabs-io) **[VERIFY: may be outdated for Pegasus 1.5, which needs no indexing]**
  - Marengo indexing per modality: Visual **$0.033/min**, Audio **$0.0083/min**, Text-in-video **$0.067/min**. — [TwelveLabs pricing (alt page)](https://www.twelvelabs.io/pricing-2)
- **Free plan: 600 minutes (10 hours) total, shared across indexing, analysis, and segmentation.** — [Analyze videos guide](https://docs.twelvelabs.io/docs/guides/analyze-videos); [TwelveLabs Pricing](https://www.twelvelabs.io/pricing)
- There is an official Python SDK, `twelvelabs`, on PyPI. — [PyPI twelvelabs](https://pypi.org/project/twelvelabs/)
- Third-party claim: typical enterprise spend is "$5K–15K+/month". This is irrelevant for a CLI hobbyist and comes from a low-quality aggregator. — [Mixpeek comparison](https://mixpeek.com/comparisons/mixpeek-vs-twelvelabs)

### Inferences
- 15-min video with Pegasus 1.5 direct analysis: 15 × $0.021 = $0.315, plus about 2–5K output tokens × $0.0075/1K ≈ $0.02–0.04, so **≈$0.33–0.36**. If you also index with Marengo visual + audio, add about $0.62. The free plan covers about 40 such videos.
- This is the closest match to "describe each scene with timestamps": you can define a segment as "each distinct visual scene" with fields like `description`, `objects`, `on_screen_text`, `people`, and get JSON back.
- A YouTube workflow has to download first (yt-dlp), then upload the file or host it at a raw URL. That carries the ToS issue in section 6.

### Gaps
- I could not fetch the live pricing page, so I can't confirm whether Pegasus 1.5 has different per-minute rates from 1.2, or whether the "infrastructure" fee still applies.
- I did not find Marengo 3.5's release date or whether it supersedes 3.0 as the default.
- I found no independent quality benchmark of Pegasus 1.5 scene descriptions against Gemini.

---

## 3. AWS: Rekognition Video, Bedrock Data Automation (BDA), Amazon Nova

### Takeaway
On AWS, **Rekognition Video** gives cheap shot and technical-cue segmentation ($0.05/min each) plus labels and OCR ($0.10/min), but no prose. **Bedrock Data Automation** adds **chapter segmentation with per-chapter natural-language summaries** for $0.050/min standard or $0.084/min custom. **Nova 2 Lite** is the cheapest promptable LLM route at about $0.08 per 15 min. Every AWS option needs the video in **S3**, except tiny inline Nova payloads.

### Cited Findings
**Rekognition Video**
- Segment detection: **Shot detection $0.05/min** and **Technical cues (black frames, end credits, color bars) $0.05/min**. — [Amazon Rekognition pricing](https://aws.amazon.com/rekognition/pricing/) (via search)
- Shot output gives the start, end, and duration of each shot plus a total shot count. Technical cues identify black frames, color bars, opening and end credits, studio logos, and primary program content. — [Detecting video segments (docs)](https://docs.aws.amazon.com/rekognition/latest/dg/segments.html)
- Stored-video **label detection, content moderation, text detection, face detection, celebrity recognition, and face search cost $0.10/min**. — [Rekognition pricing](https://aws.amazon.com/rekognition/pricing/); [Wring pricing guide](https://wring.co/blog/aws-rekognition-pricing-guide)
- Free tier: 60 free minutes of video analysis per month for 12 months, covering Label, Moderation, Face Detection, Face Search, Celebrity, Text, and Person Pathing. — [Rekognition pricing](https://aws.amazon.com/rekognition/pricing/) **[VERIFY: AWS changed its new-account free-tier model in 2025; segment detection does not appear in this list]**
- Input: the video **must be in an S3 bucket**. The API is async (`StartSegmentDetection` returns a JobId and you poll `GetSegmentDetection`). Max file size **10 GB**, max duration **6 hours**. — [StartSegmentDetection API ref](https://docs.aws.amazon.com/rekognition/latest/APIReference/API_StartSegmentDetection.html); [Working with stored video](https://docs.aws.amazon.com/rekognition/latest/dg/video.html)
- **[RETIRED/DEPRECATED]** Rekognition **people pathing was discontinued on 2025-10-31**. — [AWS ML blog: Transitioning from people pathing](https://aws.amazon.com/blogs/machine-learning/transitioning-from-amazon-rekognition-people-pathing-exploring-other-alternatives/)
- **[DEPRECATED for new customers]** **Streaming Video Analysis** and **Batch Image Content Moderation** stopped being available to new customers on **2026-04-30**. Accounts that used them in the prior 12 months keep access. — [Rekognition feature availability changes](https://docs.aws.amazon.com/rekognition/latest/dg/rekognition-availability-changes.html)

**Bedrock Data Automation (BDA), video modality**
- Standard output covers: **full-video summary, chapter segmentation with per-chapter summaries**, full audio transcript with speaker identification, detected text, logo detection, IAB taxonomy categories, and explicit-content detection. — [AWS News Blog: BDA GA](https://aws.amazon.com/blogs/aws/get-insights-from-multimodal-content-with-amazon-bedrock-data-automation-now-generally-available/); [BDA contextual advertising blog](https://aws.amazon.com/blogs/machine-learning/automate-video-insights-for-contextual-advertising-using-amazon-bedrock-data-automation/)
- BDA detects **shots** (a continuous series of frames from camera start to stop) and **chapters** (a sequence of shots forming a coherent unit of action or narrative, or a continuous conversation topic). — [BDA contextual advertising blog](https://aws.amazon.com/blogs/machine-learning/automate-video-insights-for-contextual-advertising-using-amazon-bedrock-data-automation/)
- Chapter summaries describe the speaker and visual content plus discussion topics. One reviewer saw them keep whole-video context rather than staying isolated to the chapter. — [Nicholas Griffin blog](https://nicholasgriffin.dev/blog/generating-structured-data-with-bedrock-data-automation/)
- **Video blueprints** (custom output, added May 2025) let you define fields such as scene summaries, content tags, and object detection with natural-language instructions. Limit: one video blueprint per project or request. — [What's New May 2025](https://aws.amazon.com/about-aws/whats-new/2025/05/amazon-bedrock-data-automation-custom-insights-videos); [BDA limits](https://docs.aws.amazon.com/bedrock/latest/userguide/bda-limits.html)
- Pricing: **Standard output for video $0.050/min**; **Custom output for video (1–30 fields) $0.084/min**. — [Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing/) (via [BigData Boutique](https://bigdataboutique.com/blog/aws-bedrock-pricing-guide), [Caylent](https://caylent.com/blog/amazon-bedrock-pricing-explained))
- Limits: max video length **240 min**, max file size **10,240 MB**. Input and output go through S3. — [BDA prerequisites/limits](https://docs.aws.amazon.com/bedrock/latest/userguide/bda-limits.html); [Tutorials Dojo cheat sheet](https://tutorialsdojo.com/amazon-bedrock-data-automation-cheat-sheet/)

**Amazon Nova (video understanding via Bedrock)**
- Nova 2 Lite accepts video by **S3 URI up to 1 GB**, or inline up to **25 MB**. — [Nova 2 multimodal understanding (docs)](https://docs.aws.amazon.com/nova/latest/nova2-userguide/using-multimodal-models.html)
- Sampling is **1 fps for videos ≤16 min**. Longer videos get a fixed **960 frames** total. AWS recommends staying under 1 hour for low-motion video and under 16 min for high-motion video. A 10-second clip uses about 2,880 tokens. — [Nova 2 multimodal docs](https://docs.aws.amazon.com/nova/latest/nova2-userguide/using-multimodal-models.html)
- Nova 2 Lite costs **$0.30/M input tokens, $2.50/M output tokens**. — [OpenRouter Nova 2 Lite](https://openrouter.ai/amazon/nova-2-lite-v1); [pricepertoken](https://pricepertoken.com/pricing-page/model/amazon-nova-2-lite-v1) **[VERIFY against Bedrock's pricing page]**
- TwelveLabs Marengo 3.0 is also served on Amazon Bedrock. — [Amazon press center](https://press.aboutamazon.com/aws/2025/12/twelvelabs-launches-its-most-powerful-video-understanding-model-marengo-3-0-on-twelvelabs-and-amazon-bedrock)

### Inferences
- 15-min video costs:
  - Rekognition shot + technical cues: $0.75–$1.50. Add labels for $1.50 and text for $1.50, so the full metadata stack is **≈$4.50**.
  - BDA standard: **$0.75**, which buys chapters plus summaries.
  - BDA custom blueprint (e.g. "describe each scene"): **$1.26**.
  - Nova 2 Lite: 900 frames ≈ 259K tokens × $0.30/M ≈ **$0.08**, plus negligible output. This is the cheapest by far, but you must prompt for timestamps and check them yourself.
- BDA "chapters" are semantic or narrative units, not raw camera shots. Shot data appears in the output too, but per-shot prose descriptions are not standard. You would need a blueprint or Nova for that.
- All AWS paths need an S3 upload and an IAM setup. With boto3 that is easy to drive from a Python CLI.

### Gaps
- I could not confirm whether BDA standard output includes shot-level timestamps in JSON, as opposed to chapter-level only, without fetching the docs.
- I did not confirm Nova Pro / Nova Premier video pricing, or whether a newer Nova (e.g. "Nova 2 Pro") is GA.
- I did not confirm Rekognition free-tier eligibility for segment detection under AWS's current (post-2025) free-tier model.

---

## 4. Microsoft Azure AI Video Indexer (status, scenes/shots/keyframes, OCR, generative summaries, pricing)

### Takeaway
Video Indexer is **still active and still shipping features** (GPT-5 support for textual summaries in March 2026). Its **Basic Video preset** gives scenes, shots, keyframes, OCR, labels, and objects. Its **textual video summarization** gives an LLM-written summary, but it needs a paid ARM account connected to Azure OpenAI. Classic accounts were retired in 2024. Public per-minute prices could not be confirmed, and one source says pricing is now sales-led. For a developer-friendly "describe each segment" API, Microsoft's newer **Azure Content Understanding** video analyzer is the more direct fit.

### Cited Findings
- **[RETIRED]** Video Indexer stopped creating new **classic accounts** on 2024-01-15. **Classic accounts retired on 2024-06-30**, along with Azure Media Services. Adaptive bitrate was dropped and the API changed. — [Release notes](https://learn.microsoft.com/en-us/azure/azure-video-indexer/release-notes); [Accounts overview](https://learn.microsoft.com/en-us/azure/azure-video-indexer/accounts-overview); [MS Q&A on AMS retirement](https://learn.microsoft.com/en-ie/answers/questions/1603492/ams-retirement-still-cant-find-updated-avi-api-set)
- **[RETIRED]** The animation character recognition model retired on 2023-03-01. — [Release notes](https://learn.microsoft.com/en-us/azure/azure-video-indexer/release-notes)
- Recent additions, which show active development:
  - January 2025: multimodal video summarization supports GPT-4o.
  - May 2025: an `addToEndOfSummaryInstructions` parameter customizes summaries.
  - November 2025: real-time analysis preview with agentic event detection.
  - January 2026: "Situation" custom insight for natural-language scenario detection.
  - **March 2026: GPT-5 support for cloud textual summarization.**
  - — [Release notes](https://learn.microsoft.com/en-us/azure/azure-video-indexer/release-notes); [Text summarization overview](https://learn.microsoft.com/en-us/azure/azure-video-indexer/text-summarization-overview)
- My search found **no 2025–2026 retirement of Video Indexer itself**. — [Release notes](https://learn.microsoft.com/en-us/azure/azure-video-indexer/release-notes) (search extraction). A separate product, "Azure AI Vision Video Retrieval and Summary", had a separate retirement question in 2025. — [MS Q&A](https://learn.microsoft.com/en-us/answers/questions/2151867/will-azure-ai-vision-video-retrieval-and-summary-b)
- Textual summarization uses Azure OpenAI or small language models such as Phi-3.5. It **requires a paid Video Indexer account connected to an Azure OpenAI resource**. — [Use textual summarization](https://learn.microsoft.com/en-us/azure/azure-video-indexer/text-summarization-task)
- Presets: the **Basic Video** preset covers object detection, visual labels, OCR, **keyframe extraction, and scene and shot detection**. **Standard Video** adds face and celebrity recognition, OCR keywords, topics, and named entities. **Advanced** includes every model. Audio has Basic, Standard, and Advanced presets as well. — [Azure Video Indexer pricing page](https://azure.microsoft.com/en-us/pricing/details/video-indexer/); [Indexing configuration guide](https://learn.microsoft.com/en-us/azure/azure-video-indexer/indexing-configuration-guide)
- Billing is based on input-file duration, charged for audio analysis, video analysis, or both. — [Pricing page](https://azure.microsoft.com/en-us/pricing/details/video-indexer/)
- **[VERIFY]** "As of May 2026" pricing is described as sales-led, with a contact form instead of self-serve rates. — [xpay.sh](https://www.xpay.sh/saas-pricing/azure-video-indexer/); [SpotSaaS: "Custom Quote Required 2026"](https://www.spotsaas.com/product/azure-video-indexer/pricing). These are low-quality aggregators. The official pricing page URL still exists, but the search tool could not extract numbers from it.
- Trial: up to **600 free minutes** on the website, or **2,400 minutes** via the API developer portal. — [Video Indexer overview](https://learn.microsoft.com/en-us/azure/azure-video-indexer/video-indexer-overview) (via search)
- **Azure Content Understanding** (Foundry Tools) has a video analyzer billed per hour of content, prorated per minute. **Content extraction costs $1/hour**. Field or segment extraction is billed in tokens: about 7,500 input tokens per minute at $2/M and about 900 output tokens per minute at $8/M in Microsoft's worked example. — [Content Understanding pricing explainer](https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/pricing-explainer); [GitHub source of that page](https://github.com/MicrosoftDocs/azure-ai-docs/blob/main/articles/ai-services/content-understanding/pricing-explainer.md); [Video overview](https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/video/overview). **[VERIFY: one extraction still labels it "preview"; GA status in Oct 2026 unclear]**
- Cloudinary sells a Microsoft Azure Video Indexer add-on, so Video Indexer can also be reached through Cloudinary. — [Cloudinary docs: Azure Video Indexer add-on](https://cloudinary.com/documentation/microsoft_azure_video_indexer_addon)

### Inferences
- 15-min video on Content Understanding, using Microsoft's per-minute ratios: extraction $0.25, input tokens 112.5K × $2/M = $0.225, output tokens 13.5K × $8/M ≈ $0.11, so **≈$0.58**.
- 15-min video on Video Indexer: I can't compute a cost without confirmed per-minute rates. The trial minutes (600–2,400) would cover testing.
- Video Indexer's JSON includes `scenes`, `shots`, and `keyframes` with start/end times, plus OCR, labels, and objects with time instances. That is good structure. Its natural-language output is a whole-video summary, not per-scene prose.
- Face identification and celebrity recognition on Azure are gated by Microsoft's Limited Access policy, so expect an application process.

### Gaps
- I could not retrieve Video Indexer per-minute USD prices from the official page. Sources conflict on whether self-serve pricing is still published.
- I did not verify the "prompt content" / video-to-text API that produces LLM-ready per-section text (an earlier Video Indexer feature), or its current status.
- I did not confirm Content Understanding's GA date or whether its video analyzer outputs per-segment descriptions by default.
- I did not verify the Limited Access requirements for faces and celebrities.

---

## 5. Others: Gemini (Google AI / Vertex), VideoDB, Mux, Memories.ai, Hive, Clarifai, Cloudinary, newer entrants

### Takeaway
**Gemini** is now Google's official successor path. It is the **only major service that takes a YouTube URL directly**, so you avoid download and re-upload. For about $0.15–$0.45 per 15-min video it can return timestamped per-scene prose from a single prompt, and the September 2026 "agentic video understanding" mode cuts tokens further. Among smaller entrants, **VideoDB** (scene index plus describe API with timestamps) and **Mux Robots** (chapters, scenes, summaries) are the most relevant. Memories.ai is a consumer and prosumer option with per-minute scene detection.

### Cited Findings
**Google Gemini (Gemini API / Vertex AI)**
- On **2026-09-01** Google added **agentic video understanding** to the Gemini API: the model chooses which parts of the video to look at instead of ingesting at a fixed frame rate. It works for **uploaded files and YouTube URLs** on Gemini 3.7 Flash, 3.6 Flash, and 3.5 Flash-Lite. It cuts tokens by up to 88% and cost per query by up to 66%, with no extra feature fee. — [MarkTechPost, 2026-09-04](https://www.marktechpost.com/2026/09/04/google-agentic-video-understanding-gemini-flash-models/); [NYU Shanghai RITS summary](https://rits.shanghai.nyu.edu/ai/gemini-agentic-video-understanding); [Gemini API video understanding docs](https://ai.google.dev/gemini-api/docs/interactions/video-understanding). An independent test reported trade-offs. — [MLQ.ai](https://mlq.ai/news/google-expands-geminis-agentic-video-analysis-but-early-testing-finds-trade-offs/)
- Standard video tokenization is about **300 tokens per second at default media resolution**, or **100 tokens per second at low resolution**. — [Gemini API video understanding](https://ai.google.dev/gemini-api/docs/interactions/video-understanding) (via search)
- Pricing (two sources disagree on which model is current, so both are listed):
  - **Gemini 3.5 Flash**: $1.50/M input tokens (video frames at the same rate), $9/M output. Batch and Flex: $0.75 / $4.50. — [aicostcheck](https://aicostcheck.com/model/gemini-3-5-flash); [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)
  - **Gemini 3.7 Flash**: $0.75/M input, $3.75/M output, **introductory until 2026-12-31**. — [search extraction citing Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing); [The Rundown: 3.5 Flash → 3.7 migration](https://www.therundown.ai/tools/gemini-3-5-flash)
  - **[VERIFY]** Model names and prices change quickly. Vertex AI pricing appears to now live under a "Gemini Enterprise Agent Platform" URL. — [Agent Platform pricing](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing)
- YouTube URL limits (aggregator): on the free tier, **8 hours of YouTube video per day**, up to 10 videos per request, and roughly 1 hour max per video at default resolution (about 3 hours at low resolution) within a 1M context. — [tkmxai "Gemini API in Production"](https://www.tkmxai.it.com/gemini-api-in-production-4) **[VERIFY against official docs; my background knowledge says only public videos are supported]**
- **[VERIFY / ambiguous]** One aggregator says "As of September 30, 2026, video models have no free tier". This probably refers to video-generation models (Veo/Omni), not video input. — [yingtu.ai](https://yingtu.ai/en/blog/google-gemini-api-free-tier-limits-2026)
- Google's official recommendation for Video Intelligence API users is to migrate to Gemini. Google also hosts a "extract video chapters" prompt sample for Vertex Gemini. — [VI deprecations](https://docs.cloud.google.com/video-intelligence/docs/deprecations); [Vertex prompt gallery: extract video chapters](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/prompt-gallery/samples/extract_extract_video_chapters?authuser=0)

**VideoDB**
- VideoDB's **scene index** runs vision models over extracted frames or scenes. A **Describe Video Scene** API accepts `prompt`, `model_name`, and `model_config`, and returns scene records with **AI descriptions plus start and end timestamps**. Scene and frame extraction algorithms are configurable. — [Describe Video Scene (VideoDB docs)](https://docs.videodb.io/api-reference/videos/scenes/describe_video_scene); [Scene Index Guide](https://docs.videodb.io/scene-index-guide-80); [Multimodal indexing](https://docs.videodb.io/pages/understand/indexing-pipelines/multimodal-indexing)
- Integrations exist with LlamaIndex (VideoDB retriever and multimodal RAG). — [LlamaIndex VideoDB example](https://developers.llamaindex.ai/python/examples/multi_modal/multi_modal_videorag_videodb/)

**Mux**
- **Mux Robots** offers hosted AI workflows: summarization, chapter generation, "breaking content into chapters and scenes", summaries and tags, moderation, thumbnails, and translation or dubbing. It launched as a **technical preview in April 2026, free through mid-June 2026**. — [Mux Robots](https://www.mux.com/robots); [Mux: Best Video APIs (2026)](https://www.mux.com/articles/the-best-video-apis-right-now)
- There is an open-source `@mux/ai` library and docs for AI-generated chapters (mostly transcript-driven). — [Mux blog: @mux/ai](https://www.mux.com/blog/video-ai-shouldn-t-be-hard-so-we-built-mux-ai); [Generating video chapters using AI](https://www.mux.com/docs/integrations/ai-generated-chapters)

**Memories.ai**
- An API for video search, summarization, and captioning. It advertises scene detection, OCR, object recognition, and **timestamped summaries across "20+ video platforms"**. Pricing: 100 free credits/month; Plus $15/month (annual) for 5,000 credits; scene detection **$0.15/min**. — [Memories.ai](https://memories.ai/); [Memories.ai pricing](https://memories.ai/pricing); [AI video recognition](https://memories.ai/tools/ai-video-recognition)

**Hive / Clarifai / Cloudinary**
- Hive focuses on trust and safety (moderation with video timestamps). Example prices: OCR moderation $0.13/min, logo recognition $0.50/min. — [Eden AI: Best Video Analysis APIs 2026](https://www.edenai.co/post/best-video-analysis-apis)
- Clarifai is a customizable vision platform with pay-as-you-go pricing. I found no scene-description-specific product. — [Eden AI](https://www.edenai.co/post/best-video-analysis-apis)
- Cloudinary: I found no native "describe each scene" API. It offers the Azure Video Indexer add-on. — [Cloudinary add-on docs](https://cloudinary.com/documentation/microsoft_azure_video_indexer_addon); [Gumlet comparison](https://www.gumlet.com/learn/video-api-platforms-for-developers/)

**Comparison roundups (2026)**
- These exist but I could not fetch them: [Primate Intelligence: Best Video Understanding APIs 2026](https://primateintelligence.ai/compare/best-video-understanding-apis-2026), [Mixpeek: Best Video Intelligence APIs 2026](https://mixpeek.com/curated-lists/best-video-intelligence-apis), [Eden AI 2026](https://www.edenai.co/post/best-video-analysis-apis).

### Inferences
- 15-min video on Gemini, prompted to "list each scene with start/end timestamps and a description":
  - 3.5 Flash at default resolution: 900 s × ~300 tok/s ≈ 270K input tokens × $1.50/M ≈ **$0.41**.
  - 3.5 Flash at low resolution: ~90K tokens ≈ **$0.14**.
  - 3.7 Flash at intro pricing: about half of the above.
  - Agentic mode: potentially less again.
  - Output (~3–5K tokens) adds $0.03–0.05.
- Gemini has no dedicated shot-boundary detector. Timestamps come from the model and can drift on fast-cut content. A common hybrid is local PySceneDetect for exact cuts plus Gemini or Pegasus for the descriptions.
- Gemini's YouTube-URL input is the cleanest legal path for YouTube content, because Google's own service fetches the video and you never download it.

### Gaps
- I could not confirm from an official Google page: the exact current YouTube-URL rules (public only, daily caps on paid tiers), or which Flash model is the GA default in October 2026.
- I found no pricing for VideoDB or for Mux Robots after the preview.
- I found no reliable data on whether Memories.ai's "20+ platforms" includes direct YouTube ingestion, or on its ToS posture.
- I found no independent head-to-head quality benchmark of scene descriptions across Gemini, Pegasus, BDA, and Content Understanding.

---

## 6. Cross-cutting: per-scene timestamps, description quality, YouTube download/ToS, 15-min cost

### Takeaway
Only the LLM-backed services produce natural-language per-scene descriptions: Gemini, TwelveLabs Pegasus 1.5, BDA (chapter summaries or blueprints), Azure Content Understanding, Nova, and VideoDB. The classic vision APIs (Google VI, Rekognition, Video Indexer Basic) produce precise but label-only shot metadata. **Gemini is the only option that ingests YouTube URLs natively.** Every other service requires downloading the video, which YouTube's Terms of Service prohibit without a YouTube-provided download link or permission.

### Cited Findings
- YouTube's Terms of Service (archived versions) say: "You shall not download any Content unless you see a 'download' or similar link displayed by YouTube on the Service for that Content." — [YouTube Terms, archived 2016](https://web-wp.archive.org/web/20160402095011/https:/www.youtube.com/t/terms); [archived 2017](https://web-wp.archive.org/web/20170811164130/https:/www.youtube.com/t/terms); [archived 2013 (UNT)](https://webarchive.library.unt.edu/web/20130213220921mp_/http://www.youtube.com/t/terms)
- TwelveLabs explicitly dropped YouTube ingestion and requires raw-file URLs or uploads. — [TwelveLabs upload docs](https://docs.twelvelabs.io/docs/resources/playground/upload-and-manage-videos)
- Gemini accepts YouTube URLs, including in the new agentic mode. — [MarkTechPost](https://www.marktechpost.com/2026/09/04/google-agentic-video-understanding-gemini-flash-models/)
- Timestamped outputs:
  - Rekognition: per-shot start, end, and duration. — [Rekognition segments](https://docs.aws.amazon.com/rekognition/latest/dg/segments.html)
  - TwelveLabs Pegasus 1.5: timestamped schema JSON. — [Pegasus 1.5 blog](https://www.twelvelabs.io/blog/introducing-pegasus-1-5)
  - VideoDB: start/end per scene description. — [VideoDB describe scene](https://docs.videodb.io/api-reference/videos/scenes/describe_video_scene)
  - BDA: shots plus chapters with summaries. — [BDA blog](https://aws.amazon.com/blogs/machine-learning/automate-video-insights-for-contextual-advertising-using-amazon-bedrock-data-automation/)
  - Video Indexer: scenes, shots, and keyframes. — [VI pricing presets](https://azure.microsoft.com/en-us/pricing/details/video-indexer/)

### Summary table (prices observed 2026-10-04 via search; 15-min estimates are my own arithmetic)

| Service | Shot/scene boundaries | NL per-scene description | Timestamps | Input / YouTube | Price basis | ≈15-min cost | Status |
|---|---|---|---|---|---|---|---|
| Google Video Intelligence | Yes (shot change) | No (labels only) | Yes | GCS or bytes; no YouTube | $0.05 shot, $0.10 label, $0.15 text/object per min; 1,000 min/feature/mo free | $0 (free tier) to ~$6.75 | **Deprecated 2026-09-14; shutdown 2027-09-14 [VERIFY]**; celebrity recognition shut down 2025-09-16 |
| TwelveLabs Pegasus 1.5 | Yes (user-defined segments) | **Yes**, schema-driven | Yes | Upload, raw URL, base64; **YouTube not supported** | $0.021/min input + $0.0075/1K output tokens | ~$0.33 | Active; 600 free min |
| TwelveLabs Marengo 3.0/3.5 | via search/embeddings | No (embeddings) | Yes (clips) | Same as Pegasus | Visual $0.033, audio $0.0083, text $0.067 per min | ~$0.62 (visual+audio) | Active |
| AWS Rekognition Video | Yes (shots + technical cues) | No | Yes | S3 only; ≤10 GB, ≤6 h | $0.05/min segment type; $0.10/min labels/text | $0.75–$4.50 | Active; streaming closed to new customers 2026-04-30; people pathing ended 2025-10-31 |
| AWS Bedrock Data Automation | Shots + chapters | **Yes** (chapter summaries; blueprint for custom) | Yes | S3; ≤240 min, ≤10 GB | $0.050/min standard; $0.084/min custom | $0.75 / $1.26 | Active |
| Amazon Nova 2 Lite | Via prompt | **Yes** (prompted) | Model-generated | S3 ≤1 GB or inline ≤25 MB | $0.30/M in, $2.50/M out | ~$0.08 | Active |
| Azure AI Video Indexer | Yes (scenes, shots, keyframes) | Whole-video textual summary (needs Azure OpenAI) | Yes | Upload/URL to ARM account | Per-minute presets; rates not confirmed / sales-led? | Unknown | Active (GPT-5 summaries Mar 2026); classic accounts retired 2024-06-30 |
| Azure Content Understanding | Segments | **Yes** (field extraction) | Yes | Upload/URL | $1/h extraction + tokens ($2/M in, $8/M out) | ~$0.58 | Preview vs GA unclear [VERIFY] |
| Google Gemini (API / Vertex) | Via prompt | **Yes** (prompted) | Model-generated | Files API, GCS, **YouTube URL directly** | ~300 tok/s default (100 low); 3.5 Flash $1.50/M in | ~$0.14–$0.45 | Active; agentic video mode 2026-09-01 |
| VideoDB | Scene index | **Yes** (describe API, custom prompt) | Yes | Upload/URL | Not found | Unknown | Active |
| Mux Robots | Chapters/scenes | Summaries | Yes | Mux-hosted assets | Free preview to mid-June 2026; later pricing not found | Unknown | Technical preview (Apr 2026) |
| Memories.ai | Scene detection | Timestamped summaries | Yes | "20+ platforms" | $0.15/min scene detection; credit plans | ~$2.25 | Active |

### Inferences
- For a Python CLI that must start from YouTube URLs, the lowest-friction, ToS-safest choice is Gemini's YouTube-URL input. TwelveLabs Pegasus 1.5 is the strongest dedicated alternative but needs a downloaded file. For exact cut points, pair either one with local shot detection (e.g. PySceneDetect).
- Avoid starting new work on Google Video Intelligence, given the deprecation.
- Rekognition and BDA are reasonable if the user already lives in AWS, but they require S3 staging.
- Description quality: LLM-based outputs (Gemini, Pegasus, BDA, Content Understanding, Nova) give fluent prose. Label APIs give keyword lists with confidences. In this round I found no rigorous independent benchmark ranking the prose quality. Vendor claims, such as TwelveLabs' Marengo benchmark beating Nova and Vertex, are self-reported.

### Gaps
- I could not access the current (2026) YouTube ToS text directly; only archived versions were cited. Current wording reportedly still bars downloading except as expressly authorized, but I did not verify it here.
- I found no head-to-head quality evaluation of per-scene descriptions across services.
- Pricing for Azure Video Indexer, VideoDB, and post-preview Mux could not be confirmed.
