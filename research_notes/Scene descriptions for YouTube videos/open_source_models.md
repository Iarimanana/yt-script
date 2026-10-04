# Open-Source / Self-Hostable Models and Research for Per-Scene Video Description (as of October 2026)

> Research note on method: huggingface.co, arxiv.org, ollama.com, docs.vllm.ai, Google/NVIDIA blogs and most leaderboard sites were blocked by this session's egress proxy. Primary facts below therefore come mostly from **official GitHub READMEs/docs fetched from raw.githubusercontent.com**: Qwen, OpenGVLab, OpenBMB, vLLM, llama.cpp, Ollama, NVIDIA, Meta, Ai2, LLaVA, Video-MME. Where a fact comes only from a web-search snippet or an aggregator (benchlm.ai, llm-stats, roboflow, codersera, spheron), it is labelled as such. Treat those as lower confidence.

## 1. Image/frame captioners (Florence-2, BLIP-2, Moondream, SmolVLM, PaliGemma 2, LLaVA-OneVision, InternVL, MiniCPM-V, Gemma 3/3n/4): detail level, VRAM, CPU/Apple Silicon, licenses

### Takeaway
By October 2026 the frame-captioning picture has changed. The 2024-era specialists (Florence-2, PaliGemma 2, BLIP-2, LLaVA-OneVision-1) are superseded for *detailed* scene descriptions by general small VLMs:
- **Qwen3.5** (0.8B–27B dense, Apache-2.0, natively multimodal, Feb–Mar 2026)
- **Gemma 4** (E2B/E4B/26B-A4B/31B, now Apache-2.0, Apr 2026)
- **MiniCPM-V 4.6** (1.3B, Apache-2.0, May 2026)
- **Moondream 3** (9B MoE / 2B active, BSL)

All of these except possibly Moondream 3 run in llama.cpp, and most also run on Mac via MLX. Florence-2 and SmolVLM2 are still the cheapest options for CPU-only short captions.

### Cited Findings

**Qwen3.5 / 3.6 / 3.8 (Alibaba): the new default general VLM family**
- Qwen3.5 was released 2026-02-16, starting with a 397B-A17B MoE. 122B-A10B, 35B-A3B and 27B followed on 2026-02-24, and 9B, 4B, 2B and 0.8B on 2026-03-02. Qwen3.6-35B-A3B came on 2026-04-16 and Qwen3.6-27B on 2026-04-22. Qwen3.8-2.4T-A95B came on 2026-08-12 and Qwen3.8-27B on 2026-08-14. — [QwenLM/Qwen3.6 (now Qwen3.8) README](https://github.com/QwenLM/Qwen3.6)
- Qwen3.5 is a "Unified Vision-Language Foundation". Its README says "Early fusion training on trillions of multimodal tokens… outperforms Qwen3-VL models across reasoning, coding, agents, and visual understanding benchmarks". It uses a hybrid of Gated Delta Networks and sparse MoE. — [QwenLM README](https://github.com/QwenLM/Qwen3.6)
- Runtime support stated by Qwen: "llama.cpp supports the Qwen3.5 open model series (text & vision)", and "mlx-vlm (vision + text) support the Qwen3.5 open model series" on Apple Silicon. It also lists vLLM, SGLang, Transformers and Unsloth. Ollama is not mentioned in the official README. — [QwenLM README](https://github.com/QwenLM/Qwen3.6)
- License: Apache-2.0. Context is 262,144 tokens. — [QwenLM README (via WebFetch summary)](https://github.com/QwenLM/Qwen3.6)
- MiniCPM-V's README claims MiniCPM-V 4.6 is about 1.5x faster in token throughput than Qwen3.5-0.8B. This implies the 0.8B Qwen3.5 is the reference edge model. — [OpenBMB/MiniCPM-V](https://github.com/OpenBMB/MiniCPM-V)

**Gemma 4 (Google, April 2026): supersedes Gemma 3 and Gemma 3n**
- Released early April 2026 in four sizes: E2B (2.3B effective), E4B (4.5B effective), 26B A4B MoE and 31B dense. All are under **Apache 2.0**, a change from the earlier Gemma terms. — [DataNorth](https://datanorth.ai/news/google-releases-gemma-4-open-models); [Gigazine 2026-04-03](https://gigazine.net/gsc_news/en/20260403-google-released-gemma-4); [Noze](https://www.noze.it/en/insights/gemma-new-release/)
- All sizes accept images and video. E2B and E4B take video with audio; 26B and 31B take video without audio. Visual token budgets are configurable at 70/140/280/560/1120. — [Novita / search summary](https://blogs.novita.ai/gemma-4-novita-ai/)
- The 31B model processes video as frames. It handles up to 60 seconds of video at 1 fps. Google suggests lower token budgets for captioning or classification over many frames. — [NVIDIA NIM model card for Gemma 4 31B (search snippet)](https://build.nvidia.com/google/gemma-4-31b-it/modelcard)
- vLLM notes that Gemma 4 "does not ingest videos directly". vLLM splits video into text and image frames internally. A separate encoder-free "Gemma 4 Unified" (e.g. `gemma-4-12B-it`) supports image, video and audio natively. — [vLLM supported_models.md](https://github.com/vllm-project/vllm/blob/main/docs/models/supported_models.md)
- llama.cpp ships official GGUFs for gemma-4-E2B, E4B, 26B-A4B and 31B, with audio input on E2B and E4B. — [llama.cpp docs/multimodal.md](https://github.com/ggml-org/llama.cpp/blob/master/docs/multimodal.md)
- Ollama's own vision docs now use `gemma4` as the example vision model. — [ollama docs/capabilities/vision.mdx](https://github.com/ollama/ollama/blob/main/docs/capabilities/vision.mdx)
- Gemma 3n: vLLM supports text, image and audio but not video. Its vLLM performance is "not yet fully optimized". — [vLLM supported_models.md](https://github.com/vllm-project/vllm/blob/main/docs/models/supported_models.md)

**MiniCPM-V / MiniCPM-o (OpenBMB): best on-device/phone option**
- **MiniCPM-V 4.6** was open-sourced 2026-05-11. It has 1.3B parameters and "mixed 4x/16x visual token compression". OpenBMB says it "surpasses larger models like Gemma4-E2B-it". It was merged into Ollama's official library on 2026-06-25 ("image and video understanding"). — [OpenBMB/MiniCPM-V](https://github.com/OpenBMB/MiniCPM-V)
- **MiniCPM-o 4.5** (9B) was released 2026-02-03. OpenBMB says it "approaches Gemini 2.5 Flash in vision, speech, and full-duplex multimodal live streaming". It handles "high-FPS videos (up to 10fps)". — [OpenBMB/MiniCPM-V](https://github.com/OpenBMB/MiniCPM-V)
- MiniCPM-V 4.5 (2025-08-26) has had official llama.cpp and vLLM support since 2025-09-01. — [OpenBMB/MiniCPM-V](https://github.com/OpenBMB/MiniCPM-V)
- Video parameters: `max_num_frames` defaults to 128. `stack_frames` composites N−1 extra sub-frames per second into a grid image (recommended value 3 or 5). — [OpenBMB/MiniCPM-V](https://github.com/OpenBMB/MiniCPM-V)
- License: "The MiniCPM-o/V model weights and code are open-sourced under the Apache-2.0 license." — [OpenBMB/MiniCPM-V](https://github.com/OpenBMB/MiniCPM-V)

**InternVL (OpenGVLab)**
- InternVL3.5 was introduced 2025-08-26. The flagship is InternVL3.5-241B-A28B. There is also a 20B-A4B version built on GPT-OSS. — [OpenGVLab/InternVL](https://github.com/OpenGVLab/InternVL)
- InternVL3 (2025-04-11) Video-MME scores, without/with subtitles: 14B 70.4/73.0, 38B 72.7/75.0, 78B 72.7/75.7. — [InternVL3 report, arXiv 2504.10479 (search snippet)](https://arxiv.org/pdf/2504.10479)
- In vLLM, only InternVL2.5 (Qwen2.5 backbone), InternVL3 and InternVL3.5 support video input. — [vLLM supported_models.md](https://github.com/vllm-project/vllm/blob/main/docs/models/supported_models.md)
- llama.cpp has GGUFs for InternVL2.5 1B/4B and InternVL3 1B/2B/8B/14B. — [llama.cpp multimodal.md](https://github.com/ggml-org/llama.cpp/blob/master/docs/multimodal.md)

**Moondream**
- Moondream 2 (2B) and 0.5B: "captioning, visual question answering, and object detection". — [vikhyat/moondream](https://github.com/vikhyat/moondream)
- Moondream 3 Preview (announced 2025-09-18) is a 9B MoE with 64 experts and 2B active parameters. Context grew from 2K to 32K. Built-in skills include detection, pointing, counting, captioning and segmentation. — [moondream.ai blog (search snippet)](https://moondream.ai/blog/moondream-3-preview)
- License: Moondream 2 was Apache-2.0. Moondream 3 Preview is under **BSL**, which converts to Apache 2 after two years. — [moondream.ai / HN discussion (search snippet)](https://news.hada.io/topic?id=23322)
- vLLM supports `moondream3-preview` with `caption` and `query` prompt templates, but not detect/point. — [vLLM supported_models.md](https://github.com/vllm-project/vllm/blob/main/docs/models/supported_models.md)
- llama.cpp has a GGUF for `moondream2-20250414`. — [llama.cpp multimodal.md](https://github.com/ggml-org/llama.cpp/blob/master/docs/multimodal.md)

**Florence-2 (Microsoft, 2024)**
- Sizes are base (~230M) and large (~770M), under the **MIT** license. Tasks include captioning, detection, segmentation, OCR and grounding. — [Roboflow model page (aggregator)](https://playground.roboflow.com/models/microsoft/florence-2)
- vLLM supports Florence-2 only through an external `bart-plugin`. — [vLLM supported_models.md](https://github.com/vllm-project/vllm/blob/main/docs/models/supported_models.md)

**SmolVLM2 (Hugging Face, Feb 2025)**
- Apache-2.0, sizes 256M–2.2B. VRAM is about 0.8 GB for 256M, 1.2 GB for 500M and 4.9 GB for 2.2B. The 256M-Video model needs 1.38 GB for video inference. It runs on CPU, including Raspberry Pi and AI PCs. — [Roboflow SmolVLM2 page (aggregator)](https://roboflow.com/model/smolvlm2)
- llama.cpp ships GGUFs for SmolVLM2-2.2B, SmolVLM2-256M-Video and SmolVLM2-500M-Video. — [llama.cpp multimodal.md](https://github.com/ggml-org/llama.cpp/blob/master/docs/multimodal.md)
- vLLM lists SmolVLM2 as text + image only. — [vLLM supported_models.md](https://github.com/vllm-project/vllm/blob/main/docs/models/supported_models.md)

**PaliGemma 2 (Google, Dec 2024)**
- Built on Gemma 2 {2B, 9B, 27B} backbones at 224/448/896 px. It is described as handling "image and short video caption". — [big_vision PaliGemma README](https://github.com/google-research/big_vision/blob/main/big_vision/configs/proj/paligemma/README.md)
- There is a DOCCI-finetuned long-caption checkpoint, `google/paligemma2-3b-ft-docci-448`. vLLM supports it with text + image input. — [vLLM supported_models.md](https://github.com/vllm-project/vllm/blob/main/docs/models/supported_models.md)
- License: "released under the same open license as the Gemma models… require manual acknowledgement". — [big_vision README](https://github.com/google-research/big_vision/blob/main/big_vision/configs/proj/paligemma/README.md)

**LLaVA-OneVision → LLaVA-OneVision-2**
- LLaVA-OneVision (0.5B/7B/72B) dates from 2024-08. LLaVA-Video 7B/72B and the LLaVA-Video-178K dataset date from 2024-10. The repo marks its training pipeline as "legacy". — [LLaVA-VL/LLaVA-NeXT](https://github.com/LLaVA-VL/LLaVA-NeXT)
- **LLaVA-OneVision-2** was released 2026-04-30. It is a "fully open 8B multimodal model that unifies image, long-form video, and spatial understanding", released with data, encoders, training code, checkpoints and logs.
  - It uses codec-aligned "OneVision-Encoder" input: dense I-frames plus only the motion-rich patches of P-frames. For the same 54-token budget it covers "18 frames instead of 6".
  - It releases a "LLaVA-OneVision-2-VideoCaption" dataset of "extremely dense video captions", including 10–15 min captions.
  - [EvolvingLMMs-Lab/LLaVA-OneVision-2](https://github.com/EvolvingLMMs-Lab/LLaVA-OneVision-2)
- vLLM supports LLaVA-OneVision-2 for image + video. — [vLLM supported_models.md](https://github.com/vllm-project/vllm/blob/main/docs/models/supported_models.md)

**Meta PerceptionLM (PLM, Apr 2025)**
- Sizes 1B/3B/8B on Llama 3.x. Model license is the **FAIR Research License** (non-commercial); code is Apache-2.0. Meta calls its datasets "the largest spatiotemporally annotated video dense captioning… datasets to ever exist". — [facebookresearch/perception_models](https://github.com/facebookresearch/perception_models)

### Inferences
- **Detailed vs short captions:**
  - *Short or tag-like captions:* Florence-2 (its `<CAPTION>`/`<DETAILED_CAPTION>`-style task prompts give fairly short output), SmolVLM2-256M/500M and Moondream 2's caption skill.
  - *Paragraph-level scene descriptions:* Qwen3.5 (4B/9B/27B), Gemma 4 (E4B/31B), MiniCPM-V 4.6 / MiniCPM-o 4.5, InternVL3.5, LLaVA-OneVision-2 and PaliGemma2-DOCCI. These are general instruction-following VLMs you can prompt for "describe setting, people, actions, on-screen text, camera shot".
- **VRAM rule of thumb**, based on the Qwen2.5-VL table in §2 and the GGUF numbers in §4:
  - A 2–4B model fits in about 4–10 GB.
  - A 7–9B model fits in about 16–20 GB at BF16, or 6–12 GB at 4-bit.
  - 27–32B dense models need about 24 GB at 4-bit (one RTX 4090/5090), or BF16 on an 80 GB A100/H100.
  - MoE models such as Qwen3.5-35B-A3B and Gemma 4 26B-A4B run fast like small models but need memory for all weights.
- **CPU/Mac-friendly choices:**
  - Mac: llama.cpp GGUFs (Qwen3.5, Gemma 4, InternVL3, SmolVLM2, Moondream2, MiniCPM-V) and mlx-vlm (Qwen3.5, Qwen2.5-VL, LLaVA-OV).
  - Ollama: Gemma 4 and MiniCPM-V 4.6 for frame captioning.
  - Pure CPU: SmolVLM2-256M/500M, Florence-2 and Moondream 0.5B/2B are the realistic options.
- **Superseded** for this use case: BLIP-2 (2023), Florence-2 (2024; still fine as a fast detector/short captioner), PaliGemma 2, LLaVA-OneVision-1, InternVL2.5/3, Gemma 3/3n, MiniCPM-V 2.6/4.5 and Moondream 2.

### Gaps
- I could not open Hugging Face model cards. Exact per-model VRAM for Qwen3.5-4B/9B/27B, Gemma 4 and MiniCPM-V 4.6 comes from secondary sources or inference, not the cards.
- I collected no fresh source on BLIP-2. Its "superseded" status is my inference.
- Licenses not verified: InternVL3.5 weights (Qwen-backbone sizes are usually Apache/MIT, but unconfirmed), LLaVA-OneVision-2 and Molmo2.
- Whether Ollama's MiniCPM-V 4.6 / Gemma 4 entries accept actual video files is unconfirmed. Ollama's API docs show only an `images` array (see §4).
- No head-to-head benchmark of caption quality on keyframes (DOCCI/DREAM-1K/CapsBench) was found for the 2026 models.

## 2. Video-native models (Qwen2.5-VL, Qwen3-VL, Qwen3.5/3.6, LLaVA-Video, InternVideo2.5/3, VideoLLaMA3, Apollo, NVIDIA Cosmos/Eagle/Nemotron, 2026 releases): long videos and timestamps

### Takeaway
The Qwen line is the de-facto open standard for video with timestamps:
- **Qwen3-VL** (Sep–Oct 2025, 2B–235B, Apache-2.0) added explicit text-timestamp alignment, 256K→1M context and "second-level indexing" over hours-long video.
- **Qwen3.5/3.6** (2026) fold vision into the main LLM and report Video-MME of about 78–88 for sizes a single developer can run (9B–35B-A3B).

The strongest video specialists in 2026 are built on Qwen backbones:
- **InternVideo3-8B** (June 2026, Apache-2.0), built on Qwen3-VL.
- NVIDIA's **Cosmos-Reason2 / Cosmos 3** and **Nemotron 3 Nano Omni**, under NVIDIA licenses.

Superseded: LLaVA-Video, VideoLLaMA3, Apollo and InternVideo2.5 (2024–early 2025).

### Cited Findings

**Qwen2.5-VL (Jan 2025, superseded)**
- Sizes 3B/7B/72B (Jan 2025), plus 32B (Mar 2025) and AWQ quants. — [QwenLM/Qwen3-VL README news](https://github.com/QwenLM/Qwen3-VL)
- Minimum inference VRAM with transformers. Qwen notes real usage is "at least 1.2 times higher". — [QwenLM/Qwen3-VL README](https://github.com/QwenLM/Qwen3-VL)

  | Precision | 3B | 7B | 72B |
  |---|---|---|---|
  | BF16 | 5.75 GB | 13.17 GB | 133.11 GB |
  | INT4 | 1.44 GB | 3.29 GB | 33.28 GB |

**Qwen3-VL (Sep–Oct 2025)**
- Release dates: 235B-A22B on 2025-09-23; 30B-A3B plus FP8 versions on 2025-10-04; 4B and 8B on 2025-10-15; 2B and 32B on 2025-10-21. Instruct and Thinking editions exist for each. The tech report came out 2025-11-27 (arXiv 2511.21631). — [QwenLM/Qwen3-VL](https://github.com/QwenLM/Qwen3-VL)
- Architecture: "Interleaved-MRoPE… enhancing long-horizon video reasoning", DeepStack, and "Text–Timestamp Alignment: Moves beyond T-RoPE to precise, timestamp-grounded event localization". — [QwenLM/Qwen3-VL](https://github.com/QwenLM/Qwen3-VL)
- "Native 256K context, expandable to 1M; handles books and hours-long video with full recall and second-level indexing." — [QwenLM/Qwen3-VL](https://github.com/QwenLM/Qwen3-VL)
- Video settings:
  - Default sampling is fps=2, configurable with `fps` or `num_frames`.
  - Per-video token budget is configurable at 256–16,384 visual tokens (32x spatial plus 2x temporal compression).
  - Qwen recommends keeping `total_pixels` below 24576×32×32.
  - A video can be passed as a list of pre-extracted frames with `sample_fps`, "used to determine timestamps for each frame". This is directly useful for feeding scene-cut frames.
  - [QwenLM/Qwen3-VL](https://github.com/QwenLM/Qwen3-VL)
- Recommended decoder is `torchcodec`. `decord` "has known issues, such as decoding hangs, and its project is no longer actively maintained". — [QwenLM/Qwen3-VL](https://github.com/QwenLM/Qwen3-VL)
- License is Apache-2.0. vLLM ≥0.11.0 and SGLang are supported. The large FP8 checkpoints are aimed at 8×H100. — [QwenLM/Qwen3-VL (WebFetch summary)](https://github.com/QwenLM/Qwen3-VL)
- VRAM, from aggregators: Qwen3-VL-8B at Q4_K_M needs about 12 GB and Qwen3-VL-4B at Q4_K_M about 6 GB. Spheron lists minimums of 10 GB for 4B and 18 GB for 8B. — [codersera (aggregator)](https://codersera.com/blog/qwen3-vl-4b-vs-qwen3-vl-8b-benchmarks-vram-guide/amp/); [Spheron docs (aggregator)](https://docs.spheron.network/guide-to-deploy/llms/qwen3-vl-4b-8b)
- Qwen3-VL-235B-A22B-Instruct scores **64.8 mIoU on Charades-STA** (temporal grounding). — [llm-stats (aggregator)](https://llm-stats.com/models/compare/qwen2.5-vl-7b-vs-qwen3-vl-235b-a22b-thinking)
- A search snippet attributes Video-MME (w/o subs) **71.4** to Qwen3-VL-8B. The source table could not be opened, so this is unverified. — [search result citing Leum-VL / DynFrame papers](https://arxiv.org/pdf/2603.20354)

**Qwen3.5 / Qwen3.6 (2026): natively multimodal and strongest open video scores**
- Qwen3.5-9B: Video-MME with subs **84.5**, without subs **78.4**, MLVU **84.4**. — [HF model card Qwen3.5-9B (search snippet)](https://huggingface.co/Qwen/Qwen3.5-9B)
- Qwen3.5-27B: Video-MME with subs **87.0**, without subs **82.8**, MLVU **85.9**. — [HF model card Qwen3.5-27B (search snippet)](https://huggingface.co/Qwen/Qwen3.5-27B)
- Qwen3.6, per aggregator snapshots:
  - Qwen3.6-27B: **87.7** Video-MME with subs.
  - Qwen3.6-35B-A3B: **86.6** with subs and **82.5** without subs.
  - Proprietary Qwen3.7 Plus: 88.0 with subs.
  - [benchlm.ai Video-MME w/ sub (aggregator)](https://benchlm.ai/benchmarks/videoMmeWithSub); [benchlm.ai w/o sub](https://benchlm.ai/benchmarks/videoMmeNoSub)
- Reproducibility caveat: a user running Qwen3.5-9B through HF transformers 5.2.0 on an H100 got a Video-MME average of **69.81**, against the official **78.4**. The issue was closed "as not planned" with no maintainer explanation. — [QwenLM/Qwen3.6 issue #86](https://github.com/QwenLM/Qwen3.6/issues/86)
- One article says Qwen3.5 handles video up to about 2 hours. This is a secondary source. — [dev.to article](https://dev.to/akaranjkar08/qwen-35-alibabas-open-weight-ai-is-quietly-challenging-gpt-54-and-gemini-31-2026-guide-39bl)

**InternVideo family (OpenGVLab)**
- InternVideo2.5 (2025-01, HiCo) → InternVideo-Next (2025-12) → **InternVideo3** (2026-06). InternVideo3 shipped with a tech report (arXiv 2606.12195), an 8B instruct model, a 380K-video long-video SFT dataset and the Vidify agent. — [OpenGVLab/InternVideo](https://github.com/OpenGVLab/InternVideo)
- InternVideo3 converts a Qwen3-VL backbone to "Multimodal Multi-head Latent Attention (M^2LA)", which compresses the KV cache.
  - On a single H200, decode throughput improves 1.84x at 32K prefill tokens, 4.12x at 128K, 4.77x at 256K and 5.01x at 384K.
  - "The original Qwen3-VL backbone runs out of memory at 512K prefill tokens."
  - It claims the best open-weight results on Video-MME, MLVU, VRBench and EgoSchema.
  - The example uses fps=4 and max_pixels=256×2×32×32. License is Apache-2.0.
  - [InternVideo3 README](https://github.com/OpenGVLab/InternVideo/tree/main/InternVideo3)
- InternVideo3-8B is reported at **73.8** on Video-MME, against **88.6** for Gemini 3 Pro and **83.3** for GPT-5. It is also said to lead Qwen3-VL-8B on 12 of 15 video benchmarks in the paper. This is a search summary of a 2026 guide; the page was not opened. — [BentoML/SiliconFlow 2026 guides (search snippet)](https://www.bentoml.com/blog/multimodal-ai-a-guide-to-open-source-vision-language-models)

**VideoLLaMA3 (Jan 2025, superseded)**
- 2B (Qwen2.5-1.5B) and 7B (Qwen2.5-7B), Apache-2.0. The example uses `fps: 1, max_frames: 180`. As of January 2025 it was "the best 7B-sized model" on the VideoMME and LVBench leaderboards. — [DAMO-NLP-SG/VideoLLaMA3](https://github.com/DAMO-NLP-SG/VideoLLaMA3)

**LLaVA-Video (Oct 2024, superseded by LLaVA-OneVision-2)**
- 7B/72B models plus the LLaVA-Video-178K synthetic dataset. — [LLaVA-NeXT](https://github.com/LLaVA-VL/LLaVA-NeXT)

**Apollo (Meta + Stanford, Dec 2024, superseded)**
- Sizes 1.5B/3B/7B; "excelling at handling hour-long videos". Weights circulate through community re-uploads, e.g. GoodiesHere on HF. — [smol.ai news](https://news.smol.ai/frozen-issues/24-12-16-ainews-meta-apollo-video-understanding-up-to-1-hour-sota-open-weights.html); [HF re-upload](https://huggingface.co/GoodiesHere/Apollo-LMMs-Apollo-3B-t32)

**Meta PLM-8B**
- Video-MME 58.3, MVBench 77.1, Charades-STA 58.6, DREAM-1K (detailed video captioning) 35.9, VATEX 99.7. — [perception_models README](https://github.com/facebookresearch/perception_models)

**Ai2 Molmo2**
- "State-of-the-art video understanding, pointing, and tracking". Checkpoints are 4B, 8B and O-7B. Long-context SFT uses "36k+ tokens, 384 frames". vLLM supports it. — [allenai/molmo2](https://github.com/allenai/molmo2); [vLLM supported_models.md](https://github.com/vllm-project/vllm/blob/main/docs/models/supported_models.md)

**NVIDIA**
- **Eagle 2.5-8B** (released 2025-07): Qwen2.5-7B with SigLIP2, 128K context. Code is Apache-2.0; the model is under an "NVIDIA License". vLLM lists it as text + image only. — [NVlabs/Eagle](https://github.com/NVlabs/Eagle); [vLLM](https://github.com/vllm-project/vllm/blob/main/docs/models/supported_models.md)
- **Nemotron Nano 12B v2 VL** (2025-10-28): hybrid Transformer-Mamba. Efficient Video Sampling (EVS) handles long videos at lower cost. Released under a "permissive NVIDIA open license". — [NVIDIA build model card (search snippet)](https://build.nvidia.com/nvidia/nemotron-nano-12b-v2-vl/modelcard)
- **Nemotron 3 Nano Omni 30B-A3B** (2026-04-28): Mamba-Transformer MoE with about 3B active parameters, covering image, video, audio and text.
  - "Conv3D-based temporal compression for video" gives a 2x reduction in temporal tokens.
  - NVIDIA claims "up to 9x higher multimodal throughput".
  - License is the NVIDIA Open Model Agreement, with commercial use allowed.
  - vLLM supports it.
  - [NVIDIA blog](https://blogs.nvidia.com/blog/nemotron); [BibiGPT summary](https://bibigpt.co/en/features/nvidia-nemotron-3-nano-omni-explained); [vLLM](https://github.com/vllm-project/vllm/blob/main/docs/models/supported_models.md)
- **Cosmos-Reason2**: 2B and 8B released 2025-12-19, 32B on 2026-04-29.
  - Minimum GPU memory is 24 GB for 2B and 32 GB for 8B.
  - It ships "Caption a video" and "Temporally caption a video" (temporal localization) recipes at fps 4 via vLLM.
  - Source code is Apache-2.0.
  - [nvidia-cosmos/cosmos-reason2](https://github.com/nvidia-cosmos/cosmos-reason2)
- **Cosmos 3** (May 2026):
  - Sizes: Super 64B (H200/B200/GB200), Nano 16B (RTX Pro 6000/H100/B200) and Edge 4B (released July 2026, for Jetson AGX Orin/Thor).
  - Its "Reasoner" tier covers world understanding and grounding over images and video.
  - License is OpenMDW-1.1.
  - [NVIDIA/cosmos](https://github.com/NVIDIA/cosmos)
  - vLLM supports the Cosmos3 understanding tower with video. — [vLLM](https://github.com/vllm-project/vllm/blob/main/docs/models/supported_models.md)

**Other 2026 video-capable open models listed in vLLM**
- MiMo-V2.5-Omni, MiniMax-M3, Muse Glimmer 30B (`meta-models/Muse-Glimmer-30B`), Ovis2.6 (2B, 30B-A3B), Intern-S2, Keye-VL-1.5-8B, GLM-4.5V and GLM-4.1V-Thinking. — [vLLM supported_models.md](https://github.com/vllm-project/vllm/blob/main/docs/models/supported_models.md)
- GLM-4.6V (Z.ai) has a 128K context and native multimodal tool use. — [SiliconFlow guide (search snippet)](https://www.siliconflow.com/articles/en/best-open-source-models-for-video-summarization)

### Inferences
- **Timestamps:**
  - Qwen3-VL and Qwen3.5 (and InternVideo3, which inherits Qwen3-VL) are the models built to emit "mm:ss"-style timestamps from absolute-time encoding. This is the right family when you want the model itself to segment a long clip.
  - If scenes are already cut (e.g. with PySceneDetect), timestamps can come from the cutter. Each scene is then a short clip, which any VLM can describe, including Gemma 4's 60-second window.
- **Long videos:** the realistic approach is per-scene chunks at 1–2 fps with a capped token budget. Full-video single passes over hours of video need 256K+ contexts and lots of KV cache. InternVideo3's M^2LA work shows that standard Qwen3-VL runs out of memory at 512K tokens even on an H200.
- **Single-developer sweet spot:**
  - 24 GB GPU: Qwen3.5-9B, Qwen3-VL-8B or InternVideo3-8B at BF16/FP8, or Qwen3.5-27B / Qwen3.6-27B at 4-bit.
  - Smaller budgets: Qwen3.5-4B and MiniCPM-V 4.6.
- **License watch:**
  - Permissive: Qwen (Apache-2.0), Gemma 4 (Apache-2.0), MiniCPM (Apache-2.0), InternVideo3 (Apache-2.0).
  - NVIDIA-specific terms: Nemotron, Eagle, Cosmos.
  - Research-only: PLM (FAIR non-commercial).
  - BSL: Moondream 3.

### Gaps
- The full Qwen3-VL tech report video table (Video-MME, MLVU, LVBench, Charades-STA per size) could not be opened because arXiv was blocked. Only scattered numbers were obtained.
- Exact Qwen3.5 recommended video fps and max frames were not confirmed (the HF model cards were blocked).
- No official Video-MME or Charades numbers were found for Gemma 4, Nemotron 3 Nano Omni, Cosmos 3 or LLaVA-OneVision-2.
- Whether Apollo's official weights were withdrawn could not be confirmed. Only community re-uploads were found.
- No Qwen3.8-27B video benchmarks were found. Its README emphasises coding and agents.

## 3. Dense video captioning research (Vid2Seq → 2024–2026): segment + caption with timestamps; YouCook2 / ActivityNet Captions / ViTT; open vs proprietary

### Takeaway
Classic dense video captioning (DVC) has gone from specialist models fine-tuned per dataset to general Video-LLMs plus temporal-grounding tricks:
- Specialist models: Vid2Seq (2023), Streaming DVC (2024).
- Video-LLM approaches: TimeChat, TRACE, VTG-LLM, TA-Prompting (WACV 2026), and the native timestamp alignment in Qwen3-VL.
- Newer 2026 work focuses on caption *fidelity*: CodecCap's keyframe-plus-residual captions and very dense caption datasets such as PLM RDCap and LLaVA-OV-2 VideoCaption.

Zero-shot open Video-LLMs still score far below fine-tuned specialists on YouCook2 (TRACE 2.2 SODA_c zero-shot vs Vid2Seq 7.7 SODA fine-tuned). Gemini 2.5 Pro is reported to rival fine-tuned specialists. No standardized 2026 leaderboard compares open and proprietary models on DVC.

### Cited Findings
- **Vid2Seq** (CVPR 2023, Google):
  - "Takes frames and transcribed speech from an untrimmed minutes-long video as input, and outputs dense event captions together with their temporal localization… by predicting a single sequence of tokens".
  - Pre-trained on YT-Temporal-1B using speech transcripts as pseudo event captions.
  - Released SODA scores: **5.8 on ActivityNet Captions** and **7.7 on YouCook2**. Code is in Scenic (JAX).
  - [google-research/scenic vid2seq README](https://github.com/google-research/scenic/tree/main/scenic/projects/vid2seq)
- **Streaming Dense Video Captioning** (Google, CVPR 2024) improves CIDEr by up to 11.0 on ActivityNet and 4.0 on YouCook2 over the prior state of the art, across ActivityNet, YouCook2 and ViTT. — [arXiv 2404.01297](https://arxiv.org/html/2404.01297v1)
- **TimeChat** (CVPR 2024, 7B) beats prior VidLLMs in zero-shot YouCook2 DVC by +1.0 SODA_c, +2.8 CIDEr and +9.2 F1. — [arXiv 2312.02051](https://arxiv.org/pdf/2312.02051)
- YouCook2 has about 2K untrimmed cooking videos averaging 320 s, with about 7.7 annotated steps each. — [TimeChat paper (search snippet)](https://arxiv.org/pdf/2312.02051)
- **TRACE** (ICLR 2025, causal event modelling: timestamps + salient scores + captions) has these released numbers:
  - YouCook2 zero-shot: CIDEr **8.1**, METEOR 2.8, SODA_c **2.2**, F1 22.4. TRACE-uni reaches CIDEr 8.6.
  - ActivityNet DVC: CIDEr 25.9, SODA_c 6.4, F1 39.3. TRACE-uni reaches CIDEr 29.2.
  - Charades-STA zero-shot mIoU 38.7. TRACE-uni reaches 41.5.
  - [gyxxyg/TRACE README](https://github.com/gyxxyg/TRACE)
- **VTG-LLM** (AAAI 2025) introduces the VTG-IT-120K instruction dataset, which includes 37.2K dense-captioning samples. — [VTG-LLM GitHub](https://github.com/gyxxyg/VTG-LLM)
- **Grounded-VideoLLM** (EMNLP Findings 2025) targets fine-grained temporal grounding. — [ACL Anthology](https://aclanthology.org/2025.findings-emnlp.50.pdf)
- **TA-Prompting** (WACV 2026, NTU + NVIDIA) adds learned "Temporal Anchors" that localize events and then prompt a VideoLLM. An "event coherent sampling" step selects captions. The paper says "existing VideoLLMs remain challenging in identifying precise event boundaries in untrimmed videos". — [NVIDIA Research page](https://research.nvidia.com/labs/twn/publication/wacv_2026_taprompting); [arXiv 2601.02908](https://arxiv.org/html/2601.02908v1)
- Other 2024–2025 specialist work:
  - State-space DVC with transfer state (Sep 2025) reports large SODA/METEOR gains on YouCook2 and ActivityNet, and CIDEr/METEOR gains on ViTT. — [arXiv 2509.03426](https://arxiv.org/html/2509.03426v1)
  - MCCL reports state of the art on ActivityNet Captions and YouCook2. — [arXiv 2412.11467](https://arxiv.org/html/2412.11467v1)
  - Sali4Vid reports state of the art on YouCook2 and ViTT. — [search summary](https://www.catalyzex.com/s/Dense%20Video%20Captioning)
- **CodecCap** (Baidu ERNIE, 2026-05-26):
  - Represents video as exhaustive *keyframe captions* plus *residual captions* for localized actions and changes.
  - Introduces **VidCapQA**, a 1,000-question caption-then-QA benchmark across 14 dimensions. It finds that "captions directly generated by strong VLMs still miss many visual details".
  - Releases CodecVDC-100K, a dense captioning dataset.
  - [CodecCap (search summary of arXiv 2605.26967)](https://www.emergentmind.com/papers/2605.26967)
- **DenseStep2M** (2026) is a "Scalable, Training-Free Pipeline for Dense Instructional Video Annotation". — [arXiv 2604.26565](https://arxiv.org/pdf/2604.26565)
- **Meta PLM** releases RDCap (Region Dense Temporal Captioning) and RCap as part of PLM-VideoBench / PLM-Video-Human. — [perception_models](https://github.com/facebookresearch/perception_models)
- **LLaVA-OneVision-2** releases "extremely dense video captions", trained with a 30s → 30–180s → 10–15 min caption curriculum. — [LLaVA-OneVision-2](https://github.com/EvolvingLMMs-Lab/LLaVA-OneVision-2)
- **Cosmos-Reason2** has a ready-made "temporally caption a video" recipe that outputs timestamped events. — [cosmos-reason2](https://github.com/nvidia-cosmos/cosmos-reason2)
- **Proprietary reference:** Google (May 2025) says Gemini 2.5 Pro "rivals specialized fine-tuned models on… YouCook2 dense captioning and QVHighlights moment retrieval", measured by CIDEr on YouCook2 and R1@0.5 on QVHighlights. — [Google Developers Blog](https://developers.googleblog.com/en/gemini-2-5-video-understanding/)
- A 2026 benchmark paper evaluated "nine recent Video-MLLMs released in 2025–2026" zero-shot. These included Gemini-3.0-Pro-Preview via API, and Kimi-VL, InternVL3, Ovis2.5 and Qwen models via vLLM. — [VidOmni-Bench (search snippet)](https://www.alphaxiv.org/abs/2609.21521)

### Inferences
- **Score gap:**
  - Zero-shot open 7B Video-LLMs from 2024–25 (TimeChat, TRACE) reach only about 8 CIDEr and about 2 SODA_c on YouCook2.
  - Fine-tuned specialists (Vid2Seq lineage) reach about 7.7–8 SODA on YouCook2, more than 3x TRACE's zero-shot 2.2 SODA_c. Vid2Seq's CIDEr is not cited here; see Gaps.
  - Gemini 2.5 Pro is claimed to rival the fine-tuned specialists.
  - So open models were well behind proprietary ones on single-pass DVC as of 2025. I found no 2026 head-to-head numbers for Qwen3.5 or InternVideo3 on YouCook2/ViTT.
- **Practical recipe for YouTube scene descriptions:** don't rely on a model to both segment and caption in one pass. Instead:
  1. Use shot/scene detection for boundaries.
  2. Optionally merge shots with an LLM.
  3. Caption each scene with a strong VLM.
  4. Optionally ask Qwen3-VL/3.5 for intra-scene timestamped sub-events.

  This mirrors the CodecCap idea of keyframe plus residual captions, and avoids the boundary-precision weakness TA-Prompting describes.
- The standard DVC metrics (CIDEr, SODA_c, METEOR) reward matching terse dataset-style captions. They are poor proxies for the rich descriptions a YouTube script needs. Caption-fidelity benchmarks such as VidCapQA and DREAM-1K are more relevant.

### Gaps
- No 2025–2026 DVC numbers on YouCook2, ActivityNet or ViTT were found for Qwen3-VL, Qwen3.5, InternVideo3 or Gemini 3. The exact Gemini 2.5 Pro YouCook2 CIDEr was not retrieved; the blog figure is an image.
- TA-Prompting's and CodecCap's result tables could not be opened (arXiv and CVF were blocked).
- Vid2Seq's CIDEr values (vs SODA) were not re-verified from a primary source in this session.

## 4. Practical serving: vLLM / SGLang / Ollama / llama.cpp / MLX video support and throughput

### Takeaway
**Serving support:**
- **vLLM** is the most complete server for *video* input. It accepts `video_url` and handles Qwen2.5-VL/3-VL/3.5, InternVL3/3.5, LLaVA-OV-1/2, MiniCPM-V, Molmo2, Gemma 4, Nemotron and Cosmos 3. Since 2026 it can also prune video tokens (EVS/VidCom2).
- **llama.cpp** now takes video directly in `llama-server`. It defaults to 4 fps, inserts text timestamps every 5 s, and needs ffmpeg. This makes it the best Mac/CPU path for video.
- **Ollama**'s documented API is still images-only, so you send keyframes.
- **mlx-vlm** supports video for a subset of models.

**Throughput:** published "seconds of video per second" numbers basically don't exist. The only figures found are a few secondary ones.

### Cited Findings
- **vLLM:**
  - Video is passed as `video_url` in OpenAI-style chat. — [vLLM multimodal_inputs.md](https://github.com/vllm-project/vllm/blob/main/docs/features/multimodal_inputs.md)
  - `--video-pruning-rate <q>` with `--video-pruning-method evs|vidcom2` prunes video tokens "to reduce prefill time and KV cache usage, at some cost in accuracy". `vidcom2` is "currently supported by Qwen3-VL only". Pruning disables encoder CUDA graphs. — [vLLM multimodal_inputs.md](https://github.com/vllm-project/vllm/blob/main/docs/features/multimodal_inputs.md)
  - Video-capable entries in vLLM's model table include Qwen2-VL, Qwen2.5-VL, Qwen2.5-Omni, Qwen3-VL (dense and MoE), Qwen3-Omni, Qwen3.5 (dense and MoE), InternVL (2.5-Qwen/3/3.5, InternVideo2.5), LLaVA-OneVision, LLaVA-OneVision-2, LLaVA-NeXT-Video, MiniCPM-V/o, Molmo2, Gemma 4 / Gemma 4 Unified, GLM-4.1V/4.5V, Keye-VL, Ovis2.5/2.6, Nemotron Nano V2 VL / Nemotron 3 Nano Omni, Cosmos3, MiMo-V2.5-Omni, MiniMax-M3 and Muse Glimmer. — [vLLM supported_models.md](https://github.com/vllm-project/vllm/blob/main/docs/models/supported_models.md)
  - Caveat: "`Qwen*-VL` officially uses `qwen_vl_utils`… while vLLM uses `transformers`' `video_processing_qwen*`, which leads to slightly different results." — [vLLM supported_models.md](https://github.com/vllm-project/vllm/blob/main/docs/models/supported_models.md)
  - vLLM can load Qwen3.5 text-only (`--language-model-only`) to free GPU memory. — [vLLM supported_models.md](https://github.com/vllm-project/vllm/blob/main/docs/models/supported_models.md)
  - Qwen3-VL needs vLLM ≥0.11.0. A Docker image `qwenllm/qwenvl:qwen3vl-cu128` is available. — [QwenLM/Qwen3-VL](https://github.com/QwenLM/Qwen3-VL)
- **SGLang:**
  - Qwen3-VL is supported, with a dedicated SGLang cookbook page. — [SGLang cookbook](https://cookbook.sglang.io/autoregressive/Qwen/Qwen3-VL)
  - Qwen3.5–3.8 are served with `sglang serve … --context-length 262144`. — [QwenLM README](https://github.com/QwenLM/Qwen3.6)
- **llama.cpp:**
  - `libmtmd` "support[s] **image**, **audio** and **video** input" via `llama-server` (OpenAI-compatible) and `llama-cli`. — [llama.cpp docs/multimodal.md](https://github.com/ggml-org/llama.cpp/blob/master/docs/multimodal.md)
  - Server flags: `--video-fps N` ("target video frame rate (default: 4.0)"), `--video-timestamp-interval N` ("interval in milliseconds between text timestamps (default: 5000)") and `--video-ffmpeg-dir`. Requests use `{"type":"input_video","input_video":{"url":…}}`, which "requires a model with audio or video support". — [llama.cpp tools/server/README.md](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)
  - Official pre-quantized GGUFs (mostly Q4_K_M) cover Gemma 3/4, SmolVLM/SmolVLM2 (including Video variants), Pixtral, Qwen2-VL, Qwen2.5-VL (3B–72B), InternVL2.5/3, Llama 4 Scout, Moondream2, Qwen2.5-Omni and Qwen3-Omni. — [llama.cpp multimodal.md](https://github.com/ggml-org/llama.cpp/blob/master/docs/multimodal.md)
  - Qwen3.5 vision is supported per Qwen. — [QwenLM README](https://github.com/QwenLM/Qwen3.6)
  - MiniCPM-V 4.5 has been supported since 2025-09. — [MiniCPM-V](https://github.com/OpenBMB/MiniCPM-V)
- **Ollama:**
  - Vision docs: "Provide an `images` array… the REST API expects base64-encoded image data." The example model is `gemma4`. No video field appears in the vision docs, the API docs or the FAQ, as checked in October 2026. — [ollama docs/capabilities/vision.mdx](https://github.com/ollama/ollama/blob/main/docs/capabilities/vision.mdx)
  - MiniCPM-V 4.6 was added to Ollama's official library on 2026-06-25. — [MiniCPM-V](https://github.com/OpenBMB/MiniCPM-V)
- **MLX (Apple Silicon):**
  - mlx-vlm "supports video analysis such as captioning, summarization" for Qwen2-VL, Qwen2.5-VL, Idefics3, LLaVA, MiniMax M3, LLaVA-OneVision and Mage-VL. Example: `mlx_vlm.generate … --video path.mp4 --fps 1.0`. — [Blaizzy/mlx-vlm README](https://github.com/Blaizzy/mlx-vlm)
  - mlx-vlm also supports Qwen3.5 vision. — [QwenLM README](https://github.com/QwenLM/Qwen3.6)
- **Throughput and latency data found:**
  - Qwen3-VL-8B on an H100 SXM5: about **140 tokens/s** of text output and about **3.8 images/s** (April 2026). — [Spheron blog (aggregator)](https://www.spheron.network/blog/deploy-vision-language-models-gpu-cloud/)
  - InternVideo3 M^2LA decoding on a single H200 is 1.84x–5.01x faster than baseline at 32K–384K prefill. — [InternVideo3 README](https://github.com/OpenGVLab/InternVideo/tree/main/InternVideo3)
  - A paper reports that more efficient video representations give 2.7x faster prefill and 1.4x faster decoding for Qwen2.5-VL-7B on an RTX 4090. — [search snippet, arXiv 2504.10068 / 2505.16175](https://arxiv.org/pdf/2505.16175)
  - Vendor claims: Nemotron 3 Nano Omni "up to 9x" throughput ([NVIDIA](https://blogs.nvidia.com/blog/nemotron)); MiniCPM-V 4.6 about 1.5x token throughput vs Qwen3.5-0.8B ([MiniCPM-V](https://github.com/OpenBMB/MiniCPM-V)).
- **Hardware floors stated by vendors:**
  - Cosmos-Reason2: 24 GB minimum (2B) and 32 GB (8B). — [cosmos-reason2](https://github.com/nvidia-cosmos/cosmos-reason2)
  - Cosmos 3: Nano 16B targets RTX Pro 6000/H100; Edge 4B targets Jetson. — [NVIDIA/cosmos](https://github.com/NVIDIA/cosmos)
  - SmolVLM2 runs on CPU, including Raspberry Pi. — [Roboflow (aggregator)](https://roboflow.com/model/smolvlm2)

### Inferences
- **Token arithmetic for Qwen3-VL/3.5-style models.** Each token covers a 32×32 pixel block across 2 frames.
  - A 448×252 frame at 2 fps is about 14×8 = 112 tokens per second of video.
  - A 60-second scene is therefore about 6.7K visual tokens.
  - At 640×360, 2 fps, it is about 220 tokens per second, or about 13K tokens per minute.
  - Prefill for a few thousand to ten thousand tokens on an 8B model takes well under a second to a few seconds on an H100 or RTX 4090. Output generation (about 150–300 tokens per description at about 100+ tok/s) will dominate.
  - Rough estimate: about 2–5 s per scene for an 8B model on a 4090 or H100. A 10-minute video with about 50 scenes would take a few minutes unbatched, and less with vLLM batching. This is derived, not measured; benchmark it locally.
- **CPU/Mac:** captioning a few keyframes per scene with Gemma 4 E4B, Qwen3.5-4B or MiniCPM-V 4.6 GGUF through llama.cpp, Ollama or MLX is feasible. Sending full clips at 4 fps through llama-server multiplies token counts. Lowering `--video-fps` to 1 is advisable for long content.
- vLLM plus `--video-pruning-rate` is the main lever for throughput on long or static (talking-head) YouTube footage, where frames are highly redundant.

### Gaps
- No primary benchmark gives "seconds of video processed per second" for any model on an RTX 4090, A100/H100, L4, CPU or Mac. These numbers have to be measured locally.
- No L4-specific numbers were found.
- Whether Ollama added video input between the docs snapshot and October 2026 is not fully certain. The docs show none.
- The extent of SGLang video support for Qwen3.5, Gemma 4 and InternVL3.5 was not verified (docs.sglang.io was blocked).

## 5. Benchmarks: Video-MME, MVBench, LongVideoBench, MLVU, Charades-STA — open vs Gemini/GPT/Claude

### Takeaway
On the original **Video-MME**, the gap between open and closed models has largely closed:
- Mid-size open models like Qwen3.5-27B and Qwen3.6-27B score about 87–88 with subtitles, against about 88.6 for Gemini 3 Pro and about 83 for GPT-5. These figures come mostly from aggregators and vendor cards.

The harder, de-saturated **Video-MME-v2** (April 2026) still shows a large gap:
- Gemini-3-Pro scores 49.4 non-linear (66.1% average accuracy) against a 90.7 human baseline.
- Open models drop much more under grouped scoring, e.g. InternVL3.5-241B keeps only about 56% of its accuracy.

Gemini leads on audio-visual fusion, ordering and long-horizon reasoning. Claude and GPT rely on frames (Claude has no native video input). For temporal grounding, open models (Qwen3-VL about 64.8 mIoU on Charades-STA) are strong.

### Cited Findings
- **Video-MME (v1):** 900 videos (254 h) and 2,700 QA pairs. It is used by Gemini 3 Pro (2025-12-05), GPT-5 (2025-08-07), Gemini 2.5 Pro and GPT-4.1 as their video benchmark. — [MME-Benchmarks/Video-MME README](https://github.com/MME-Benchmarks/Video-MME); [awesomepapers summary](https://awesomepapers.io/multimodal/datasets/video-mme)
- **Video-MME scores, open vs closed:**
  - Open: Qwen3.5-27B 87.0 / 82.8 and Qwen3.5-9B 84.5 / 78.4 (with / without subs). — [HF model cards (search snippets)](https://huggingface.co/Qwen/Qwen3.5-27B)
  - Open: Qwen3.6-27B 87.7 with subs; Qwen3.6-35B-A3B 82.5 without subs. — [benchlm.ai (aggregator)](https://benchlm.ai/benchmarks/videoMmeNoSub)
  - Open: InternVideo3-8B 73.8. Closed: Gemini 3 Pro 88.6, GPT-5 83.3. — [search summary of 2026 guides](https://www.bentoml.com/blog/multimodal-ai-a-guide-to-open-source-vision-language-models)
- **Older open baselines (superseded):**
  - InternVL3-78B 72.7 / 75.7. — [InternVL3 report (snippet)](https://arxiv.org/pdf/2504.10479)
  - InternVL2-40B 61.2 (16 frames) and 64.4 (32 frames), 2024. — [InternVL README](https://github.com/OpenGVLab/InternVL)
  - PLM-8B 58.3. — [perception_models](https://github.com/facebookresearch/perception_models)
- **Video-MME-v2:**
  - Launched 2026-04-07 with 800 videos and 3,200 QA pairs in groups of 4, built from 3,300 human-hours of annotation.
  - Uses "grouped non-linear scoring" (consistency and coherence groups). It aims to fix saturation and the gap "between leaderboard performance and" real capability.
  - Supported in VLMEvalKit and lmms-eval.
  - [MME-Benchmarks/Video-MME-v2](https://github.com/MME-Benchmarks/Video-MME-v2)
- **Video-MME-v2 results:**
  - Average accuracy vs non-linear score: Gemini-3-Pro 66.1% → 49.4; Gemini-3-Flash 61.1% → 42.5.
  - Robustness ratio (non-linear score divided by accuracy): Gemini-3-Pro about 75%, Doubao-Seed-2.0-Pro about 72%, InternVL3.5-241B-A28B about 56%, LLaVA-Video-7B about 40%.
  - Thinking mode: Qwen3.5-122B-A10B gains +3.8 without subs and +5.8 with subs. Qwen3-VL-8B loses 0.6 without subs. KimiVL-16B loses 3.3.
  - Gemini-3-Pro leads on Frames & Audio, Order and Video-Based Knowledge Acquisition. "Models that rely more on visual frames (e.g. GPT-5 and the Qwen family) are relatively weaker". Even Gemini scores below 30 on Action & Motion and Physical World Reasoning.
  - [Video-MME-v2 README](https://github.com/MME-Benchmarks/Video-MME-v2)
- An aggregator lists Video-MME-v2 scores of Gemini-3-Pro 49.4 (with subs) / 38.2 (without), Qwen3.5-397B-Instruct 24.5 / 16.9, and human 90.7. The Qwen figure looks surprisingly low and could not be checked against the official leaderboard, which is an image or on a blocked site. — [benchmarklist.com (aggregator, search snippet)](https://benchmarklist.com/benchmarks/video_mme_v2/)
- **Temporal grounding (Charades-STA mIoU):**
  - Qwen3-VL-235B-A22B: 64.8. — [llm-stats (aggregator)](https://llm-stats.com/models/compare/qwen2.5-vl-7b-vs-qwen3-vl-235b-a22b-thinking)
  - PLM-8B: 58.6. — [perception_models](https://github.com/facebookresearch/perception_models)
  - TRACE zero-shot: 38.7–41.5. — [TRACE](https://github.com/gyxxyg/TRACE)
- **MVBench:** PLM-8B 77.1 and PLM-3B 74.7. — [perception_models](https://github.com/facebookresearch/perception_models)
- **MLVU:** Qwen3.5-27B 85.9 and Qwen3.5-9B 84.4. — [HF model cards (search snippets)](https://huggingface.co/Qwen/Qwen3.5-9B)
- **VideoMMMU, proprietary:**
  - Search results conflict: Gemini 3 Pro 87.6, GPT-5.1 75.2, and "Claude 4.5" 68.4 in one source, but Claude Opus 4.5 84.4 in another. — [macmyths comparison](https://macmyths.com/gemini-3-pro-vs-gpt-5-1-vs-claude-benchmarks-and-results/); conflicting snippet via [benchlm VideoMMMU](https://benchlm.ai/benchmarks/videommmu)
- **Claude video input:** one 2026 article says native video of up to about 2 hours is "a capability no current OpenAI or Anthropic model offers natively". This is a secondary source. — [dev.to](https://dev.to/akaranjkar08/qwen-35-alibabas-open-weight-ai-is-quietly-challenging-gpt-54-and-gemini-31-2026-guide-39bl)

### Inferences
- For "describe what is visible in each scene", the relevant skills are frame-level perception, OCR and short-clip action recognition. On these, 2026 open models (Qwen3.5-9B/27B, InternVideo3-8B) are roughly at GPT-5 level on Video-MME-style tests.
- Gemini 3 Pro's lead lies mainly in long-horizon ordering, audio-visual fusion and robustness (Video-MME-v2). A per-scene pipeline mostly avoids needing these.
- Expect open models to be less *consistent* across related questions (the Video-MME-v2 ratios), so they hallucinate more on fine motion or physical details. Spot-check output, or use a second-pass verifier.
- Leaderboard numbers for the same open model vary a lot with frame count, resolution, subtitle use and inference stack. One example is the Qwen3.5-9B case: 78.4 official vs 69.8 reproduced through HF transformers. Treat vendor numbers as upper bounds.

### Gaps
- Not obtained (blocked sites):
  - Official Video-MME v1 leaderboard (video-mme.github.io)
  - Video-MME-v2 leaderboard (netlify)
  - OpenCompass video leaderboard
- Missing benchmark numbers:
  - LongVideoBench for the 2026 open models.
  - MVBench for Qwen3.5 and InternVideo3.
  - Charades-STA for Qwen3.5.
  - Any benchmark for Claude's frame-based video handling.
- The GPT-5 (83.3) and Gemini 3 Pro (88.6) Video-MME figures come from search summaries, not the vendors' own pages.
