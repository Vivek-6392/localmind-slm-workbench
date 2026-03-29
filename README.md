# 🧠 LocalMind · SLM Workbench

> **100% offline AI inference · zero telemetry · your hardware, your data**

LocalMind is a production-grade Streamlit application that lets you run, benchmark, and compare Small Language Models (SLMs) **entirely on your own machine** — no internet connection required after setup, no API keys, no subscription, no data leaving your device. It uses [Ollama](https://ollama.com) as the local inference engine and exposes a clean, dark-themed UI for interactive chat, performance benchmarking, multi-model comparison, tradeoff analysis, and real-world constraint documentation.

---

## 📌 Table of Contents

- [Why Local SLMs?](#-why-local-slms)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Recommended Models](#-recommended-models)
- [App Features — All 5 Tabs](#-app-features--all-5-tabs)
- [Benchmark Prompts Explained](#-benchmark-prompts-explained)
- [Metrics Explained](#-metrics-explained)
- [Quality vs Speed Tradeoffs](#-quality-vs-speed-tradeoffs)
- [Quantization Guide](#-quantization-guide)
- [Privacy Architecture](#-privacy-architecture)
- [Latency Guide](#-latency-guide)
- [Cost Analysis](#-cost-analysis)
- [Hardware Recommendations](#-hardware-recommendations)
- [Troubleshooting](#-troubleshooting)
- [Project Structure](#-project-structure)

---

## 🤔 Why Local SLMs?

Most people interact with AI through cloud APIs — you send text to a remote server, it processes it, and sends back a response. This works great, but it comes with real problems:

| Problem | Cloud LLM | Local SLM |
|---------|-----------|-----------|
| **Privacy** | Your data leaves your machine | Data never leaves your device |
| **Cost** | Pay per token (adds up fast) | One-time hardware, near-zero running cost |
| **Latency** | 300ms–2s network round-trip | 50–500ms locally |
| **Availability** | Needs internet, subject to outages | Works offline, always available |
| **Rate limits** | Hard caps, throttling | Unlimited — you control it |
| **Compliance** | Data residency issues (GDPR, HIPAA) | Fully on-premise, audit-ready |

Local SLMs are not always the right answer — a 3B model is not as capable as GPT-4o. But for a huge class of tasks (summarization, Q&A, code generation, classification, data extraction), they are **good enough** and the privacy + cost benefits are enormous.

This project proves you understand that tradeoff and know how to measure it.

---

## 🛠 Tech Stack

| Component | Tool | Role |
|-----------|------|------|
| **Frontend** | [Streamlit](https://streamlit.io) | Python-native web UI framework |
| **Inference Engine** | [Ollama](https://ollama.com) | Runs LLMs locally via llama.cpp |
| **HTTP Client** | `requests` | Communicates with Ollama's REST API |
| **System Monitoring** | `psutil` | CPU %, RAM usage, core count |
| **Statistics** | `statistics` (stdlib) | Mean, aggregation of benchmark results |
| **Styling** | Custom CSS + Google Fonts | Dark terminal aesthetic (Syne + Space Mono) |

**No cloud services. No OpenAI. No Anthropic. No Hugging Face Inference API.** Everything runs on `localhost`.

---

## ✅ Prerequisites

Before running the app, make sure you have:

1. **Python 3.9 or higher** — check with `python --version`
2. **Ollama installed** — the local LLM runtime (free, open source)
3. **At least one model pulled** — model weights live on your disk
4. **4 GB RAM minimum** — 8 GB strongly recommended
5. A modern CPU (2019+) or any GPU (NVIDIA / AMD / Apple Silicon)

---

## 📦 Installation

### Step 1 — Install Ollama

Ollama is the engine that actually runs the AI models locally. Think of it as a lightweight local server for LLMs.

```bash
# macOS and Linux (one command):
curl -fsSL https://ollama.com/install.sh | sh

# Windows:
# Download the installer from: https://ollama.com/download/windows
```

Verify it installed correctly:
```bash
ollama --version
```

### Step 2 — Pull Models

Download the AI model weights to your disk. These are large files (600 MB – 5 GB), so choose based on your available RAM:

```bash
# Fastest — good for weak hardware (1.1B parameters, ~637 MB)
ollama pull tinyllama

# Balanced — best starting point (2B parameters, ~1.7 GB)
ollama pull gemma:2b

# Smartest small model — recommended default (3.8B parameters, ~2.3 GB)
ollama pull phi3

# Highest quality — needs 8+ GB RAM (7B parameters, ~4.1 GB)
ollama pull mistral
```

Check what you have downloaded:
```bash
ollama list
```

### Step 3 — Start the Ollama Server

```bash
ollama serve
```

This starts Ollama listening on `http://localhost:11434`. Keep this terminal open while using the app.

> **Note for macOS:** If you installed Ollama as a desktop app, it starts automatically. Look for the llama icon in your menu bar.  
> **Note for Windows:** Check the system tray after installation.

### Step 4 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

The `requirements.txt` only has three packages:
```
streamlit>=1.32.0
requests>=2.31.0
psutil>=5.9.0
```

### Step 5 — Run the App

```bash
streamlit run app.py
```

Open your browser at: **http://localhost:8501**

The sidebar will show a green **● Ollama Online** badge if everything is connected correctly.

---

## 🤖 Recommended Models

Here are the three models we recommend for a meaningful side-by-side comparison:

### TinyLlama 1.1B — The Speed Demon
```bash
ollama pull tinyllama
```
- **Disk size:** ~637 MB
- **RAM needed:** ~1 GB
- **Speed:** 40–80 tok/s on a modern CPU
- **Quality:** Basic — handles simple Q&A, struggles with multi-step reasoning
- **Best for:** Devices with very limited RAM, latency-critical edge deployments, rapid prototyping

### Gemma 2B (Google) — The Balanced Pick
```bash
ollama pull gemma:2b
```
- **Disk size:** ~1.7 GB
- **RAM needed:** ~2.5 GB
- **Speed:** 25–50 tok/s on a modern CPU
- **Quality:** Good for its size — solid at Q&A and summarization
- **Best for:** General-purpose tasks on constrained hardware, the "works everywhere" choice

### Phi-3 Mini 3.8B (Microsoft) — The Overachiever
```bash
ollama pull phi3
```
- **Disk size:** ~2.3 GB
- **RAM needed:** ~3 GB
- **Speed:** 15–35 tok/s on a modern CPU
- **Quality:** Surprisingly strong — outperforms many 7B models on reasoning and code tasks
- **Best for:** Code generation, multi-step reasoning, the sweet spot of quality vs speed
- **Why it punches above its weight:** Trained on high-quality "textbook" data, not just raw web crawl

---

## 🖥 App Features — All 5 Tabs

### 💬 Tab 1 — Chat

A full interactive chat interface with any locally available model.

**What it shows per reply:**
- `tok/s` — how fast the model generated tokens
- Total tokens generated in that response
- Wall-clock time in seconds
- Which model produced the answer

**How it works internally:** Your message is sent via HTTP POST to `http://localhost:11434/api/generate`. Ollama runs inference and returns JSON with the response text plus timing metadata. The full conversation history is stored in Streamlit's `session_state` dictionary so it persists across rerenders within the same session.

**System prompt:** You can customize the model's behaviour via the system prompt in the sidebar. The default instructs it to be concise and reminds it (and you) that no data leaves the machine.

---

### ⚡ Tab 2 — Benchmark

Run 5 standardised prompts against your selected model and measure performance on each task independently.

**The 5 benchmark tasks and what they test:**

| Task | What the prompt asks | What it measures |
|------|---------------------|-----------------|
| Reasoning | Train speed math problem | Logical deduction, arithmetic |
| Code | Python prime sieve with type hints | Structured output, syntax correctness |
| Summarization | Compress AI concepts to 3 bullets | Faithfulness, compression quality |
| Creative | Write a haiku about offline AI | Instruction-following, format adherence |
| Knowledge | Explain RAG vs fine-tuning | Technical accuracy, conceptual clarity |

**Results displayed as:**
- 4 summary metrics cards (avg throughput, avg latency, total tokens, tasks completed)
- Horizontal bar charts per task, normalised against the fastest task
- Colour coding: green (fast) → amber (moderate) → red (slow)
- Expandable section showing the full model responses for qualitative review

---

### 🔬 Tab 3 — Compare Models

The most visually compelling tab. Pick up to 3 models, enter any prompt, and run them all.

**Output:**
1. **Speed Leaderboard** — ranked bar chart with 🥇🥈🥉 medals, showing tok/s for each model
2. **Side-by-side responses** — all three answers displayed in columns so you can judge quality directly
3. **Per-model stats** — tok/s, elapsed time, token count beneath each response

**Why side-by-side matters:** Speed benchmarks alone are misleading. A model that's twice as fast but gives wrong answers is worse. This tab forces you to evaluate both speed and quality simultaneously, which is the honest way to measure tradeoffs.

You can use any of the 5 built-in benchmark prompts or type your own.

---

### 📊 Tab 4 — Tradeoffs

A curated reference documentation tab with structured analysis:

**Model comparison table** covers 5 popular SLMs with: parameter count, RAM requirement at Q4 quantization, speed rating, quality rating, ideal use cases, and known weaknesses.

**Four key tradeoff axes:**
- **Model size vs RAM** — every billion params ≈ 0.5–1 GB at Q4; exceeding RAM causes swap → 10–100× slowdown
- **Quantization levels** — Q4_K_M is the sweet spot (95% quality at 28% of full size)
- **CPU vs GPU** — even integrated GPU gives 4–20× speedup via llama.cpp Metal/CUDA layers
- **Context window vs speed** — quadratic attention cost; 32K context is 2–4× slower than 4K

**Your measured results** also appear here if you've run the benchmark tab — so static reference data and your actual hardware measurements sit together.

---

### 🔒 Tab 5 — Constraints

A deep-dive into the three real-world constraints that drive local SLM adoption. This tab shows you understand the *why* behind running models offline, not just the *how*.

**Privacy section:**
- Explains which compliance regimes mandate on-premise AI (HIPAA, GDPR, India DPDP Act, air-gapped defense environments)
- Shows the complete network architecture — proves with a diagram that no packets leave the machine

**Latency section:**
- Numerical comparison: cloud round-trip (300ms–2s) vs local GPU (50–200ms) vs local CPU (300ms–2s)
- Explains time-to-first-token vs throughput and when each matters
- Guidance on picking a model size for a given latency budget

**Cost section:**
- Cloud API pricing table (GPT-4o, Claude, Gemini)
- Local electricity cost math (~$0.032 per million output tokens on a laptop)
- Break-even analysis: at what daily token volume does local hardware pay for itself

**Decision guide:** A 6-criterion table that helps you decide Local vs Cloud for any given use case.

**Live system snapshot:** Real-time CPU %, RAM %, and platform info at the bottom.

---

## 📐 Benchmark Prompts Explained

### Why these 5 tasks?

They're deliberately chosen to stress **different capabilities** so no single model dominates unfairly:

**Reasoning** is hard for small models — they often get the arithmetic right but fail the multi-step logic setup. A model that gets this wrong is unreliable for anything requiring deduction.

**Code** is measurable right/wrong. The Sieve of Eratosthenes is a well-known algorithm, so any model that knows it should produce correct, runnable code. Type hints and docstrings test instruction-following precision.

**Summarization** tests faithfulness — the model must compress without hallucinating. A bad model will invent facts not in the original text.

**Creative** tests constrained generation. Haiku has strict syllable rules (5-7-5). Models that can't follow format constraints are unreliable for structured output tasks.

**Knowledge** tests whether the model has accurate, nuanced understanding of a technical topic (RAG vs fine-tuning) vs confabulating plausible-sounding but wrong information.

Together, they produce a **rounded capability profile**, not just a raw speed number.

---

## 📊 Metrics Explained

When inference completes, Ollama returns these timing fields (in nanoseconds). The app converts them to human-readable units:

| Metric | What It Measures | Why It Matters |
|--------|-----------------|----------------|
| `tokens_per_sec` | Output tokens generated per second | Primary throughput — higher is better |
| `elapsed` | Total wall-clock time (seconds) | What the user actually waits for |
| `load_duration_ms` | Time to load model from disk into RAM | Cold-start penalty — happens only once per model |
| `total_duration_ms` | Full pipeline: prompt processing + generation | True end-to-end benchmark |
| `prompt_tokens` | Token count of your input | Affects prefill phase duration |
| `tokens_generated` | Token count of the response | Normalises speed comparisons across responses |

**Important nuance — cold start vs warm inference:**

`load_duration` is paid only on the **first** request after a model is loaded. Ollama keeps models in RAM between requests. So:
- First request: slow (includes disk → RAM load time)
- All subsequent requests: fast (model already in RAM)

Our benchmarks run tasks sequentially so the first task pays the cold-start cost. This is realistic — it reflects what a user would experience when switching to a model.

---

## ⚖️ Quality vs Speed Tradeoffs

This is the central tension of local SLMs:

```
Larger model  →  Better quality  →  More RAM  →  Slower inference
Smaller model →  Faster inference →  Less RAM  →  Lower quality
```

### Reference Table (Q4_K_M quantization, approximate)

| Model | Parameters | RAM | CPU Speed | Apple M2 Speed | Quality |
|-------|-----------|-----|-----------|----------------|---------|
| TinyLlama 1.1B | 1.1B | ~1 GB | 40–80 tok/s | 100–160 tok/s | ⭐⭐ |
| Gemma 2B | 2B | ~2.5 GB | 25–50 tok/s | 60–120 tok/s | ⭐⭐⭐ |
| Phi-3 Mini 3.8B | 3.8B | ~3 GB | 15–35 tok/s | 40–90 tok/s | ⭐⭐⭐⭐ |
| LLaMA 3.2 3B | 3B | ~2.8 GB | 18–40 tok/s | 50–100 tok/s | ⭐⭐⭐⭐ |
| Mistral 7B | 7B | ~5 GB | 8–20 tok/s | 25–60 tok/s | ⭐⭐⭐⭐⭐ |

### The Phi-3 Anomaly — Why Parameter Count Isn't Everything

Phi-3 Mini at 3.8B parameters scores 4/5 quality — the same as LLaMA at 3B and significantly better than Gemma at 2B. This is because Microsoft trained it primarily on high-quality synthetic "textbook" data rather than the typical noisy web crawl. Training data quality and methodology matter as much as scale. This is a critical insight for anyone building with SLMs: **don't evaluate models purely by parameter count**.

---

## 🗜️ Quantization Guide

AI models are compressed using quantization — reducing the numerical precision of weights to save memory and increase speed. The format name encodes the precision:

| Format | Bits/Weight | Size vs Full | Quality vs Full | Recommendation |
|--------|------------|-------------|-----------------|----------------|
| `Q2_K` | ~2.6 bits | 16% of full | ~85% | Only for extreme RAM constraints |
| `Q4_K_M` | ~4.5 bits | 28% of full | ~95% | ✅ **Default — use this** |
| `Q5_K_M` | ~5.7 bits | 35% of full | ~97% | If you have extra RAM headroom |
| `Q8_0` | 8 bits | 50% of full | ~99% | Near-lossless, accuracy-critical tasks |
| `F16` | 16 bits | 100% | 100% | Reference only — rarely run locally |

**The `_K_M` suffix** means the quantization uses a mixed scheme — some layers are kept at higher precision (typically the attention layers that matter most for quality) while others are compressed more aggressively. This is smarter than uniform quantization and is why Q4_K_M is the recommended sweet spot.

When you run `ollama pull phi3`, Ollama downloads Q4_K_M by default unless you specify otherwise.

---

## 🔒 Privacy Architecture

Here is the complete data flow when you use this app:

```
┌──────────────────────────────────────────────────────────────┐
│                       YOUR MACHINE                           │
│                                                              │
│   Browser → localhost:8501                                   │
│       │                                                      │
│       ▼                                                      │
│   Streamlit Python Process (app.py)                         │
│       │                                                      │
│       │   HTTP POST to localhost:11434/api/generate          │
│       ▼                                                      │
│   Ollama Server (localhost:11434)                            │
│       │                                                      │
│       ▼                                                      │
│   llama.cpp (C++ inference engine)                           │
│       │                                                      │
│       ▼                                                      │
│   Model Weights (your local disk, GGUF format)              │
│                                                              │
│   ❌  NO packets leave this machine during inference        │
│   ❌  NO DNS lookups to external servers                    │
│   ❌  NO telemetry sent to Ollama's servers                 │
│   ❌  NO logging to any external service                    │
└──────────────────────────────────────────────────────────────┘
```

**Compliance use cases this architecture satisfies:**
- **HIPAA** (US) — patient records, clinical notes can be processed locally
- **GDPR** (EU) — data residency requirement satisfied by definition
- **India DPDP Act** — personal data stays within your infrastructure
- **SOC 2 Type II** — data never leaves controlled, audited infrastructure
- **Air-gapped environments** — works with network cable physically unplugged
- **Attorney-client privilege** — legal documents never touch third-party servers

---

## ⏱️ Latency Guide

Two metrics are commonly confused. Both matter, but for different reasons:

**Time-to-First-Token (TTFT):** How long before the user sees ANY text in the response. This is what determines *perceived* responsiveness. For interactive chat, you need this under ~500ms.

**Throughput (tokens/second):** How fast the full response streams in once it starts. For long responses, this dominates the total experience time.

### Typical Real-World Numbers

| Setup | TTFT | Throughput | Best For |
|-------|------|-----------|---------|
| Cloud GPT-4o (good connection) | 300–800ms | 80–120 tok/s | Complex reasoning |
| Cloud GPT-4o (congested) | 1–3s | 40–80 tok/s | — |
| Local Phi-3, Apple M2 (GPU) | 80–150ms | 50–90 tok/s | Interactive chat |
| Local Phi-3, NVIDIA RTX 3060 | 100–200ms | 60–100 tok/s | Batch processing |
| Local Phi-3, CPU only (modern) | 400–800ms | 15–35 tok/s | Background tasks |
| Local TinyLlama, CPU only (old) | 200–400ms | 20–50 tok/s | Edge / IoT |

**Decision rules:**
- Interactive chat → prioritise TTFT → use ≤3B model with GPU, or ≤1.1B on CPU
- Batch document processing → prioritise throughput → use largest model that fits in RAM
- Always enable streaming (`stream: true`) in production — even if throughput is low, the user sees tokens arriving immediately which feels faster

---

## 💰 Cost Analysis

### Cloud API Pricing Reference

| Service | Input (per 1M tokens) | Output (per 1M tokens) |
|---------|-----------------------|------------------------|
| GPT-4o | $2.50 | $10.00 |
| Claude Sonnet 3.5 | $3.00 | $15.00 |
| Gemini 1.5 Pro | $1.25 | $5.00 |
| GPT-3.5 Turbo | $0.50 | $1.50 |

### Local Running Cost Calculation

A laptop running inference draws roughly 15–45 watts depending on load.

At 30 tokens/second throughput and 30W average draw:
- 1 million tokens ≈ 33,000 seconds of inference time
- Energy consumed: 33,000s × 30W = 990,000 Wh → ~0.27 kWh
- At $0.12/kWh (India average): **~$0.032 per million output tokens**
- That's roughly **300× cheaper than GPT-4o output pricing**

### Break-Even Analysis

If you process 100,000 tokens per day:
- **Cloud cost:** $1.00/day = $365/year (at GPT-4o pricing)
- **Local cost (existing hardware):** ~$1.17/year in electricity
- **Local cost (new RTX 4070 + PC, ~$1,500):** Pays for itself in ~4 years vs GPT-4o

If you process 500,000 tokens per day:
- **Cloud cost:** ~$5/day = $1,825/year
- **New GPU PC break-even:** under 10 months

**Hidden cloud costs not reflected in per-token pricing:**
- Data egress fees if processing large documents
- Data Processing Agreements (legal cost to sign)
- Compliance audits for regulated industries
- Vendor lock-in risk if the API changes pricing or terms
- Outage risk if the API is unavailable

---

## 🖥️ Hardware Recommendations

### Minimum Viable Setup (CPU Only)
- **RAM:** 8 GB
- **CPU:** Intel Core i5 10th gen / AMD Ryzen 5 3000 / Apple M1
- **Models that run well:** TinyLlama 1.1B, Gemma 2B
- **Expected speed:** 10–30 tok/s

### Recommended Setup (Integrated GPU)
- **RAM:** 16 GB
- **Chip:** Apple M2 / M3 (unified memory) or AMD Ryzen 7 with Radeon integrated
- **Models that run well:** All models up to 7B
- **Expected speed:** 30–90 tok/s on Apple Silicon (Metal acceleration)

### Ideal Setup (Dedicated NVIDIA GPU)
- **System RAM:** 16–32 GB
- **VRAM:** 8 GB minimum (RTX 3060 12GB recommended), 16–24 GB for 13B+ models
- **GPU examples:** RTX 3060 12GB, RTX 4070, RTX 4090
- **Models that run well:** Everything — even 13B and 30B with enough VRAM
- **Expected speed:** 60–200 tok/s depending on model

### How Ollama Uses Your Hardware

Ollama auto-detects available hardware and routes accordingly:
- **NVIDIA GPU detected** → uses CUDA via llama.cpp
- **AMD GPU detected** → uses ROCm (Linux) or CPU fallback (Windows)
- **Apple Silicon** → uses Metal GPU layers automatically
- **No GPU** → uses CPU with AVX2/AVX512 BLAS acceleration

You don't need to configure anything. Run `ollama serve` and it handles the rest.

---

## 🐛 Troubleshooting

### "Ollama Offline" badge in sidebar
```bash
# Start the Ollama server:
ollama serve

# Test it directly:
curl http://localhost:11434/api/tags
# Should return JSON with your model list
```

### No models appear in the dropdown
```bash
# Pull at least one model:
ollama pull phi3

# Verify it downloaded:
ollama list
```

### Response shows `[HTTP 404: ...]`
The model name selected in the dropdown doesn't exist locally. This can happen if you deleted a model between sessions:
```bash
ollama pull <model-name>
```

### Very slow inference (under 5 tok/s)
1. Check the RAM meter in the sidebar — if it's over 85%, the system is swapping the model to disk (10–100× slowdown)
2. Switch to a smaller model (TinyLlama or Gemma 2B)
3. Close memory-heavy applications (browsers, IDEs) before running inference
4. On Windows, check Task Manager → Performance → Memory for available RAM

### `TypeError: 'NoneType' object is not subscriptable` at line 465
This was a bug in early versions where `generate()` returned `None` on non-200 HTTP responses instead of an error dict. **Fixed in the current version** — `generate()` now always returns a properly structured dict. If you still see this error, make sure you have the latest `app.py`.

### Port 8501 already in use
```bash
streamlit run app.py --server.port 8502
```

### Model is slow on first request, fast after
This is expected and correct. The first request pays the `load_duration` cost — loading the model from disk into RAM. All subsequent requests use the already-loaded model and are significantly faster. Ollama keeps models in RAM until you explicitly unload them or RAM pressure forces eviction.

---

## 📁 Project Structure

```
localmind-slm-workbench/
│
├── app.py                    # Main Streamlit application (single file, ~830 lines)
├── requirements.txt          # Python dependencies (3 packages only)
├── README.md                 # This file — comprehensive documentation
└── PROJECT_EXPLAINER.md      # Plain-English explanation of every part of the code
```

### Why a single app.py?

For a Streamlit app of this scope, a single `app.py` is idiomatic and simpler to run. The file is organized into clearly labelled sections:

1. **Imports** — standard library + three third-party packages
2. **Page config** — Streamlit layout and title settings
3. **Custom CSS** — injected as HTML to override Streamlit's default theme
4. **Ollama helpers** — `check_ollama()`, `generate()`, `list_models()`
5. **System info** — `get_sys_info()` reads CPU/RAM via psutil
6. **Benchmark prompts** — dictionary of 5 standardised test prompts
7. **Session state init** — initializes persistent state for chat history and results
8. **Sidebar** — Ollama status, model selector, system resource meters
9. **Tabs 1–5** — each tab's complete UI and logic

---

## 📄 License

MIT — use it, fork it, learn from it, build on it.

---

## 🙏 Acknowledgements

- [Ollama](https://ollama.com) — making local LLM inference as simple as `ollama pull`
- [llama.cpp](https://github.com/ggerganov/llama.cpp) — the C++ inference engine powering it all under the hood
- [Streamlit](https://streamlit.io) — Python-native web UI that requires zero frontend knowledge
- **Meta** (LLaMA family), **Google** (Gemma), **Microsoft** (Phi-3) — for open-sourcing capable small models