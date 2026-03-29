import streamlit as st
import requests
import time
import json
import threading
import psutil
import platform
from datetime import datetime
from collections import defaultdict
import statistics

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LocalMind · SLM Benchmarking",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --bg: #0a0a0f;
    --surface: #111118;
    --surface2: #1a1a24;
    --border: #2a2a3a;
    --accent: #7c6af7;
    --accent2: #f7c56a;
    --accent3: #6af7c5;
    --text: #e8e8f0;
    --muted: #7878a0;
    --danger: #f76a6a;
}

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp { background-color: var(--bg) !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

/* Headers */
h1 { font-size: 2rem !important; font-weight: 800 !important; letter-spacing: -0.03em !important; }
h2 { font-size: 1.4rem !important; font-weight: 700 !important; letter-spacing: -0.02em !important; }
h3 { font-size: 1.1rem !important; font-weight: 600 !important; }

/* Metric cards */
.metric-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    font-family: 'Space Mono', monospace;
}
.metric-label { color: var(--muted); font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.3rem; }
.metric-value { font-size: 2rem; font-weight: 700; line-height: 1; }
.metric-unit  { font-size: 0.75rem; color: var(--muted); margin-top: 0.2rem; }

/* Status badge */
.badge {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 99px;
    font-size: 0.7rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.badge-green  { background: #1a3a2a; color: var(--accent3); border: 1px solid #2a5a3a; }
.badge-yellow { background: #3a3010; color: var(--accent2); border: 1px solid #5a4a10; }
.badge-red    { background: #3a1010; color: var(--danger);  border: 1px solid #5a1a1a; }
.badge-purple { background: #1e1a3a; color: var(--accent);  border: 1px solid #3a2a6a; }

/* Chat bubbles */
.chat-user {
    background: #1e1a3a;
    border: 1px solid #3a2a6a;
    border-radius: 12px 12px 2px 12px;
    padding: 0.8rem 1.1rem;
    margin: 0.5rem 0;
    max-width: 80%;
    margin-left: auto;
    font-size: 0.9rem;
}
.chat-bot {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 2px 12px 12px 12px;
    padding: 0.8rem 1.1rem;
    margin: 0.5rem 0;
    max-width: 85%;
    font-size: 0.9rem;
    font-family: 'Space Mono', monospace;
    line-height: 1.6;
    white-space: pre-wrap;
}
.chat-meta {
    font-size: 0.65rem;
    color: var(--muted);
    font-family: 'Space Mono', monospace;
    margin-top: 0.3rem;
}

/* Result rows */
.result-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.7rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.82rem;
}
.model-name { font-weight: 700; color: var(--accent); min-width: 140px; }
.bar-container { flex: 1; background: var(--border); border-radius: 4px; height: 8px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 4px; transition: width 0.5s; }

/* Tradeoff table */
.tradeoff-table { width: 100%; border-collapse: collapse; font-size: 0.83rem; font-family: 'Space Mono', monospace; }
.tradeoff-table th { 
    background: var(--surface2); color: var(--muted); 
    padding: 0.7rem 1rem; text-align: left; 
    border-bottom: 1px solid var(--border); 
    font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em;
}
.tradeoff-table td { 
    padding: 0.8rem 1rem; 
    border-bottom: 1px solid var(--border); 
    color: var(--text);
}
.tradeoff-table tr:hover td { background: var(--surface2); }

/* Constraint card */
.constraint-card {
    background: var(--surface2);
    border-left: 3px solid var(--accent);
    border-radius: 0 10px 10px 0;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
}
.constraint-card.privacy  { border-color: var(--accent3); }
.constraint-card.latency  { border-color: var(--accent2); }
.constraint-card.cost     { border-color: var(--danger); }
.constraint-title { font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.4rem; }
.constraint-body  { font-size: 0.82rem; color: var(--muted); line-height: 1.6; }

/* Ollama status banner */
.status-banner {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.8rem 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 1rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
}

/* Buttons */
.stButton > button {
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em !important;
    padding: 0.5rem 1.5rem !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* Input / Select */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'Space Mono', monospace !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"]  { gap: 0.5rem; border-bottom: 1px solid var(--border); }
.stTabs [data-baseweb="tab"]       { 
    background: transparent !important; 
    color: var(--muted) !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 0.5rem 1.2rem !important;
}
.stTabs [aria-selected="true"]     { color: var(--text) !important; border-bottom: 2px solid var(--accent) !important; }

/* Spinner */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* Scrollbar */
::-webkit-scrollbar       { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Ollama helpers ────────────────────────────────────────────────────────────
OLLAMA_URL = "http://localhost:11434"

def check_ollama():
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        return r.status_code == 200, r.json().get("models", [])
    except Exception:
        return False, []

def list_models():
    ok, models = check_ollama()
    if not ok:
        return []
    return [m["name"] for m in models]

def generate(model: str, prompt: str, system: str = ""):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }
    if system:
        payload["system"] = system
    _error_result = lambda msg: {
        "text": msg, "elapsed": 0, "tokens_per_sec": 0,
        "tokens_generated": 0, "prompt_tokens": 0,
        "total_duration_ms": 0, "load_duration_ms": 0,
    }
    try:
        t0 = time.time()
        r = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=120)
        elapsed = time.time() - t0
        if r.status_code == 200:
            data = r.json()
            text = data.get("response", "")
            eval_count = data.get("eval_count", 0)
            eval_duration_ns = data.get("eval_duration", 1)
            tokens_per_sec = eval_count / (eval_duration_ns / 1e9) if eval_duration_ns else 0
            prompt_tokens = data.get("prompt_eval_count", 0)
            return {
                "text": text,
                "elapsed": elapsed,
                "tokens_per_sec": round(tokens_per_sec, 1),
                "tokens_generated": eval_count,
                "prompt_tokens": prompt_tokens,
                "total_duration_ms": round(data.get("total_duration", 0) / 1e6, 1),
                "load_duration_ms":  round(data.get("load_duration",  0) / 1e6, 1),
            }
        else:
            return _error_result(f"[HTTP {r.status_code}: {r.text[:200]}]")
    except Exception as e:
        return _error_result(f"[Error: {e}]")

def get_sys_info():
    cpu_pct = psutil.cpu_percent(interval=0.3)
    mem = psutil.virtual_memory()
    return {
        "cpu_pct": cpu_pct,
        "ram_used_gb": round(mem.used / 1e9, 1),
        "ram_total_gb": round(mem.total / 1e9, 1),
        "ram_pct": mem.percent,
        "platform": platform.system(),
        "cpu_count": psutil.cpu_count(),
    }

# ── Benchmark prompts ─────────────────────────────────────────────────────────
BENCH_PROMPTS = {
    "Reasoning":    "If a train leaves at 9 AM traveling 60 mph and another leaves at 10 AM traveling 80 mph from the same station, when does the second catch the first?",
    "Code":         "Write a Python function that finds all prime numbers up to n using the Sieve of Eratosthenes. Include docstring and type hints.",
    "Summarization":"Summarize the following in 3 bullet points: Large language models are neural networks trained on vast text corpora. They predict next tokens via transformer architectures with attention mechanisms. Fine-tuning adapts base models to specific tasks. RLHF aligns outputs with human preferences.",
    "Creative":     "Write a haiku about running AI entirely offline, then explain its meaning in one sentence.",
    "Knowledge":    "What are the key differences between RAG (Retrieval-Augmented Generation) and fine-tuning as techniques to adapt LLMs to domain-specific knowledge?",
}

# ── Session state init ────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "bench_results" not in st.session_state:
    st.session_state.bench_results = {}
if "compare_results" not in st.session_state:
    st.session_state.compare_results = []

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🧠 LocalMind")
    st.markdown('<p style="color:var(--muted);font-size:0.8rem;font-family:\'Space Mono\',monospace;margin-top:-0.5rem;">Offline SLM Workbench</p>', unsafe_allow_html=True)
    st.divider()

    # Ollama status
    ollama_ok, raw_models = check_ollama()
    if ollama_ok:
        st.markdown('<span class="badge badge-green">● Ollama Online</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-red">✕ Ollama Offline</span>', unsafe_allow_html=True)
        st.markdown("""
<div style="font-family:'Space Mono',monospace;font-size:0.75rem;color:var(--muted);margin-top:0.5rem;line-height:1.8;">
Install Ollama:<br>
<code style="color:var(--accent3);">curl -fsSL https://ollama.com/install.sh | sh</code><br><br>
Pull models:<br>
<code style="color:var(--accent3);">ollama pull phi3</code><br>
<code style="color:var(--accent3);">ollama pull gemma:2b</code><br>
<code style="color:var(--accent3);">ollama pull tinyllama</code>
</div>
""", unsafe_allow_html=True)

    st.divider()

    # Model selector
    available = list_models()
    if available:
        selected_model = st.selectbox("Active Model", available)
    else:
        selected_model = st.text_input("Model name", value="phi3",
                                       help="Type the model name even if Ollama isn't running yet")

    # System prompt
    system_prompt = st.text_area("System Prompt", value="You are a helpful, concise AI assistant running entirely locally on the user's device. No data leaves this machine.", height=100)

    st.divider()

    # System info
    sys = get_sys_info()
    st.markdown("**System**")
    st.markdown(f"""
<div class="metric-card" style="padding:0.8rem 1rem;margin-bottom:0.5rem;">
<div class="metric-label">CPU Usage</div>
<div class="metric-value" style="font-size:1.4rem;">{sys['cpu_pct']}%</div>
</div>
<div class="metric-card" style="padding:0.8rem 1rem;margin-bottom:0.5rem;">
<div class="metric-label">RAM Used</div>
<div class="metric-value" style="font-size:1.4rem;">{sys['ram_used_gb']} <span style="font-size:0.85rem;color:var(--muted);">/ {sys['ram_total_gb']} GB</span></div>
</div>
<div style="font-family:'Space Mono',monospace;font-size:0.7rem;color:var(--muted);">
{sys['platform']} · {sys['cpu_count']} cores
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("# LocalMind · SLM Workbench")
st.markdown('<p style="color:var(--muted);font-family:\'Space Mono\',monospace;font-size:0.82rem;margin-top:-0.8rem;">100% offline inference · zero telemetry · your hardware, your data</p>', unsafe_allow_html=True)

tab_chat, tab_bench, tab_compare, tab_tradeoffs, tab_constraints = st.tabs([
    "💬 Chat", "⚡ Benchmark", "🔬 Compare Models", "📊 Tradeoffs", "🔒 Constraints"
])

# ──────────────────────────────────────────────────────────────────────────────
# TAB 1 · CHAT
# ──────────────────────────────────────────────────────────────────────────────
with tab_chat:
    col_header, col_badge = st.columns([3, 1])
    with col_header:
        st.markdown(f"### Chatting with `{selected_model}`")
    with col_badge:
        if ollama_ok:
            st.markdown('<span class="badge badge-green">● Live</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge badge-red">Offline</span>', unsafe_allow_html=True)

    # Chat history display
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(
                    f'<div class="chat-bot">{msg["content"]}</div>'
                    f'<div class="chat-meta">⚡ {msg.get("tps",0)} tok/s · '
                    f'{msg.get("tokens",0)} tokens · {msg.get("elapsed",0):.1f}s · '
                    f'model: {msg.get("model","?")}</div>',
                    unsafe_allow_html=True,
                )

    # Input
    st.divider()
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        user_input = st.text_input("Message", placeholder="Ask anything… runs entirely on your machine", label_visibility="collapsed")
    with col_btn:
        send = st.button("Send →", use_container_width=True)

    col_clear, col_export = st.columns(2)
    with col_clear:
        if st.button("Clear history", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    if send and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.spinner(f"Running {selected_model} locally…"):
            result = generate(selected_model, user_input, system_prompt)
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": result["text"],
            "tps": result["tokens_per_sec"],
            "tokens": result["tokens_generated"],
            "elapsed": result["elapsed"],
            "model": selected_model,
        })
        st.rerun()

# ──────────────────────────────────────────────────────────────────────────────
# TAB 2 · BENCHMARK
# ──────────────────────────────────────────────────────────────────────────────
with tab_bench:
    st.markdown(f"### Benchmark · `{selected_model}`")
    st.markdown('<p style="color:var(--muted);font-size:0.82rem;font-family:\'Space Mono\',monospace;">Run standardised prompts and measure inference performance metrics.</p>', unsafe_allow_html=True)

    col_sel, col_run = st.columns([3, 1])
    with col_sel:
        selected_prompts = st.multiselect(
            "Select benchmark tasks",
            list(BENCH_PROMPTS.keys()),
            default=list(BENCH_PROMPTS.keys()),
        )
    with col_run:
        run_bench = st.button("▶ Run Benchmark", use_container_width=True)

    if run_bench and selected_prompts:
        if not ollama_ok:
            st.error("Ollama is not running. Start it with `ollama serve`.")
        else:
            results = {}
            progress = st.progress(0)
            status_txt = st.empty()
            for i, task in enumerate(selected_prompts):
                status_txt.markdown(f'<span style="font-family:\'Space Mono\',monospace;font-size:0.8rem;color:var(--accent);">Running: {task}…</span>', unsafe_allow_html=True)
                r = generate(selected_model, BENCH_PROMPTS[task], system_prompt)
                results[task] = r
                progress.progress((i + 1) / len(selected_prompts))
            status_txt.empty()
            st.session_state.bench_results[selected_model] = results
            st.success(f"Benchmark complete for {selected_model}!")

    # Display results
    if selected_model in st.session_state.bench_results:
        res = st.session_state.bench_results[selected_model]
        st.divider()

        all_tps = [v["tokens_per_sec"] for v in res.values()]
        all_lat = [v["elapsed"] for v in res.values()]
        all_tok = [v["tokens_generated"] for v in res.values()]

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
<div class="metric-card">
<div class="metric-label">Avg Throughput</div>
<div class="metric-value" style="color:var(--accent3);">{statistics.mean(all_tps):.1f}</div>
<div class="metric-unit">tokens / second</div>
</div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
<div class="metric-card">
<div class="metric-label">Avg Latency</div>
<div class="metric-value" style="color:var(--accent2);">{statistics.mean(all_lat):.1f}</div>
<div class="metric-unit">seconds</div>
</div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
<div class="metric-card">
<div class="metric-label">Total Tokens</div>
<div class="metric-value" style="color:var(--accent);">{sum(all_tok)}</div>
<div class="metric-unit">generated</div>
</div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
<div class="metric-card">
<div class="metric-label">Tasks Run</div>
<div class="metric-value">{len(res)}</div>
<div class="metric-unit">completed</div>
</div>""", unsafe_allow_html=True)

        st.markdown("#### Per-Task Results")
        max_tps = max(all_tps) if all_tps else 1
        for task, r in res.items():
            pct = int(r["tokens_per_sec"] / max_tps * 100)
            bar_color = "var(--accent3)" if pct >= 70 else ("var(--accent2)" if pct >= 40 else "var(--danger)")
            st.markdown(f"""
<div class="result-row">
  <span style="min-width:120px;color:var(--muted);font-size:0.75rem;text-transform:uppercase;">{task}</span>
  <div class="bar-container"><div class="bar-fill" style="width:{pct}%;background:{bar_color};"></div></div>
  <span style="min-width:70px;color:{bar_color};">{r['tokens_per_sec']} tok/s</span>
  <span style="min-width:55px;color:var(--muted);">{r['elapsed']:.1f}s</span>
  <span style="min-width:60px;color:var(--muted);">{r['tokens_generated']} tok</span>
</div>""", unsafe_allow_html=True)

        # Responses
        with st.expander("View model responses"):
            for task, r in res.items():
                st.markdown(f"**{task}**")
                st.markdown(f'<div class="chat-bot">{r["text"][:800]}{"…" if len(r["text"])>800 else ""}</div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# TAB 3 · COMPARE MODELS
# ──────────────────────────────────────────────────────────────────────────────
with tab_compare:
    st.markdown("### Compare 3 Models Head-to-Head")
    st.markdown('<p style="color:var(--muted);font-size:0.82rem;font-family:\'Space Mono\',monospace;">Run the same prompt across multiple models simultaneously and compare quality + speed.</p>', unsafe_allow_html=True)

    all_avail = list_models() or ["phi3", "gemma:2b", "tinyllama"]

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        m1 = st.selectbox("Model 1", all_avail, index=0, key="cm1")
    with col_m2:
        m2 = st.selectbox("Model 2", all_avail, index=min(1, len(all_avail)-1), key="cm2")
    with col_m3:
        m3 = st.selectbox("Model 3", all_avail, index=min(2, len(all_avail)-1), key="cm3")

    compare_prompt = st.text_area(
        "Comparison prompt",
        value=BENCH_PROMPTS["Reasoning"],
        height=80,
    )

    run_compare = st.button("🔬 Run Comparison", use_container_width=False)

    if run_compare and compare_prompt.strip():
        if not ollama_ok:
            st.error("Ollama is not running.")
        else:
            models_to_run = [m for m in [m1, m2, m3] if m]
            compare_out = []
            prog2 = st.progress(0)
            for i, m in enumerate(models_to_run):
                with st.spinner(f"Running {m}…"):
                    r = generate(m, compare_prompt, system_prompt)
                    compare_out.append({"model": m, **r})
                prog2.progress((i+1)/len(models_to_run))
            st.session_state.compare_results = compare_out
            st.success("Comparison done!")

    if st.session_state.compare_results:
        st.divider()
        cres = st.session_state.compare_results

        # Speed leaderboard
        st.markdown("#### ⚡ Speed Leaderboard")
        sorted_by_speed = sorted(cres, key=lambda x: x["tokens_per_sec"], reverse=True)
        max_s = sorted_by_speed[0]["tokens_per_sec"] or 1
        medals = ["🥇", "🥈", "🥉"]
        for i, r in enumerate(sorted_by_speed):
            pct = int(r["tokens_per_sec"] / max_s * 100)
            st.markdown(f"""
<div class="result-row">
  <span style="font-size:1.2rem;">{medals[i]}</span>
  <span class="model-name">{r['model']}</span>
  <div class="bar-container"><div class="bar-fill" style="width:{pct}%;background:var(--accent3);"></div></div>
  <span style="color:var(--accent3);min-width:80px;">{r['tokens_per_sec']} tok/s</span>
  <span style="color:var(--muted);min-width:60px;">{r['elapsed']:.1f}s</span>
  <span style="color:var(--muted);min-width:70px;">{r['tokens_generated']} tokens</span>
</div>""", unsafe_allow_html=True)

        # Side-by-side responses
        st.markdown("#### 📝 Response Comparison")
        cols = st.columns(len(cres))
        for col, r in zip(cols, cres):
            with col:
                st.markdown(f"**`{r['model']}`**")
                st.markdown(f'<div class="chat-bot" style="min-height:200px;font-size:0.78rem;">{r["text"][:600]}{"…" if len(r["text"])>600 else ""}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="chat-meta">⚡ {r["tokens_per_sec"]} tok/s · {r["elapsed"]:.1f}s · {r["tokens_generated"]} tok</div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# TAB 4 · TRADEOFFS
# ──────────────────────────────────────────────────────────────────────────────
with tab_tradeoffs:
    st.markdown("### Quality vs Speed Tradeoffs")
    st.markdown('<p style="color:var(--muted);font-size:0.82rem;font-family:\'Space Mono\',monospace;">Documented tradeoffs for common small language models on consumer hardware.</p>', unsafe_allow_html=True)

    tradeoff_data = [
        {
            "model": "TinyLlama 1.1B",
            "params": "1.1B",
            "ram": "~1 GB",
            "speed": "⚡⚡⚡⚡⚡",
            "quality": "⭐⭐",
            "ideal_for": "Edge devices, IoT, rapid prototyping",
            "weakness": "Shallow reasoning, limited context",
            "quantization": "Q4_K_M",
        },
        {
            "model": "Gemma 2B",
            "params": "2B",
            "ram": "~2.5 GB",
            "speed": "⚡⚡⚡⚡",
            "quality": "⭐⭐⭐",
            "ideal_for": "Q&A, summarization, light coding",
            "weakness": "Struggles with multi-step math",
            "quantization": "Q4_K_M",
        },
        {
            "model": "Phi-3 Mini 3.8B",
            "params": "3.8B",
            "ram": "~3 GB",
            "speed": "⚡⚡⚡",
            "quality": "⭐⭐⭐⭐",
            "ideal_for": "Reasoning, code gen, analysis",
            "weakness": "Slower on CPU-only systems",
            "quantization": "Q4_K_M",
        },
        {
            "model": "Mistral 7B",
            "params": "7B",
            "ram": "~5 GB",
            "speed": "⚡⚡",
            "quality": "⭐⭐⭐⭐⭐",
            "ideal_for": "Complex tasks, nuanced writing",
            "weakness": "Needs 8+ GB RAM, slow on weak HW",
            "quantization": "Q4_K_M",
        },
        {
            "model": "LLaMA 3.2 3B",
            "params": "3B",
            "ram": "~2.8 GB",
            "speed": "⚡⚡⚡⚡",
            "quality": "⭐⭐⭐⭐",
            "ideal_for": "General assistant, instruction following",
            "weakness": "Less specialized than Phi-3",
            "quantization": "Q4_K_M",
        },
    ]

    st.markdown("""
<table class="tradeoff-table">
<thead>
<tr>
<th>Model</th><th>Params</th><th>RAM</th><th>Speed</th><th>Quality</th><th>Ideal For</th><th>Weakness</th><th>Quant</th>
</tr>
</thead>
<tbody>
""" + "".join(f"""
<tr>
<td style="color:var(--accent);font-weight:700;">{d['model']}</td>
<td>{d['params']}</td>
<td>{d['ram']}</td>
<td>{d['speed']}</td>
<td>{d['quality']}</td>
<td style="color:var(--muted);">{d['ideal_for']}</td>
<td style="color:var(--muted);">{d['weakness']}</td>
<td><span class="badge badge-purple">{d['quantization']}</span></td>
</tr>
""" for d in tradeoff_data) + "</tbody></table>", unsafe_allow_html=True)

    st.divider()
    st.markdown("#### Key Tradeoff Axes")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
<div class="constraint-card" style="border-color:var(--accent3);">
<div class="constraint-title" style="color:var(--accent3);">📐 Model Size vs RAM</div>
<div class="constraint-body">
Every billion parameters ≈ ~0.5–1 GB RAM at 4-bit quantization. 
A 7B model needs ~5 GB; a 1B model needs ~1 GB. 
Running beyond available RAM causes swapping → 10–100× slowdown.
Match the model to your RAM budget first.
</div>
</div>

<div class="constraint-card" style="border-color:var(--accent2);">
<div class="constraint-title" style="color:var(--accent2);">⚡ Quantization Levels</div>
<div class="constraint-body">
Q8 = highest quality, most RAM.<br>
Q4_K_M = sweet spot (95% quality, 50% size).<br>
Q2 = smallest, noticeable degradation.<br>
Use Q4_K_M for production; Q2 only on severely constrained devices.
</div>
</div>
""", unsafe_allow_html=True)

    with col_b:
        st.markdown("""
<div class="constraint-card" style="border-color:var(--accent);">
<div class="constraint-title" style="color:var(--accent);">🖥️ CPU vs GPU Inference</div>
<div class="constraint-body">
GPU (even integrated) gives 4–20× speedup via llama.cpp Metal/CUDA layers.
CPU-only: expect 5–20 tok/s for 3B models.
GPU-offloaded: 30–100 tok/s for same model.
Ollama auto-detects and uses available GPU layers.
</div>
</div>

<div class="constraint-card" style="border-color:var(--danger);">
<div class="constraint-title" style="color:var(--danger);">🔀 Context Window vs Speed</div>
<div class="constraint-body">
Longer context = quadratic attention cost.
At 4K tokens: baseline speed.<br>
At 8K tokens: ~30% slower.<br>
At 32K tokens: 2–4× slower.<br>
Use context limits for latency-critical applications.
</div>
</div>
""", unsafe_allow_html=True)

    # If we have real benchmark data, show it
    if st.session_state.bench_results:
        st.divider()
        st.markdown("#### 📈 Your Measured Results")
        for model_name, res in st.session_state.bench_results.items():
            tps_vals = [v["tokens_per_sec"] for v in res.values()]
            lat_vals = [v["elapsed"] for v in res.values()]
            st.markdown(f"""
<div class="result-row">
  <span class="model-name">{model_name}</span>
  <span style="color:var(--accent3);">⚡ avg {statistics.mean(tps_vals):.1f} tok/s</span>
  <span style="color:var(--accent2);">⏱ avg {statistics.mean(lat_vals):.1f}s latency</span>
  <span style="color:var(--muted);">{len(res)} tasks</span>
</div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# TAB 5 · CONSTRAINTS
# ──────────────────────────────────────────────────────────────────────────────
with tab_constraints:
    st.markdown("### Real-World Constraints")
    st.markdown('<p style="color:var(--muted);font-size:0.82rem;font-family:\'Space Mono\',monospace;">Privacy, latency, and cost are first-class concerns in local SLM deployments — not afterthoughts.</p>', unsafe_allow_html=True)

    st.markdown("""
<div class="constraint-card privacy">
<div class="constraint-title" style="color:var(--accent3);">🔒 Privacy</div>
<div class="constraint-body">
<b style="color:var(--text);">The core guarantee:</b> every token stays on your hardware. Zero API calls, zero logging, zero vendor telemetry.<br><br>
<b style="color:var(--text);">Use cases that demand this:</b><br>
• Medical / patient records (HIPAA jurisdictions)<br>
• Legal documents and attorney-client comms<br>
• Financial data, source code, trade secrets<br>
• Air-gapped environments (defense, critical infrastructure)<br>
• Regions with data-residency laws (GDPR, India DPDP Act)<br><br>
<b style="color:var(--text);">What Ollama does:</b> all inference via local Unix socket / 127.0.0.1 — packets never leave the NIC.
</div>
</div>

<div class="constraint-card latency">
<div class="constraint-title" style="color:var(--accent2);">⏱️ Latency</div>
<div class="constraint-body">
<b style="color:var(--text);">Cloud LLM round-trip:</b> 300–2000 ms network + queue + inference.<br>
<b style="color:var(--text);">Local SLM (3B, GPU):</b> 50–200 ms time-to-first-token.<br>
<b style="color:var(--text);">Local SLM (3B, CPU):</b> 500 ms–2 s time-to-first-token.<br><br>
<b style="color:var(--text);">Latency budget rules:</b><br>
• Interactive chat: need &lt;500ms first-token → use ≤3B on GPU or ≤1.1B on CPU<br>
• Batch processing: throughput matters more → use largest fitting model<br>
• Streaming mitigates perceived latency — always use stream=True in production<br><br>
<b style="color:var(--text);">This app measures:</b> total_duration, load_duration, eval_duration separately so you know where time is spent.
</div>
</div>

<div class="constraint-card cost">
<div class="constraint-title" style="color:var(--danger);">💰 Cost</div>
<div class="constraint-body">
<b style="color:var(--text);">Cloud API cost example (GPT-4o):</b> ~$5–15 per million output tokens.<br>
<b style="color:var(--text);">Local SLM cost:</b> electricity only — ~0.01–0.05 kWh per million tokens on a laptop.<br>
At $0.12/kWh → <b style="color:var(--accent3);">~$0.001–0.006 per million tokens.</b><br><br>
<b style="color:var(--text);">Break-even analysis:</b><br>
• If you run &gt;100K tokens/day → local pays off in weeks<br>
• One-time hardware cost (e.g. MacBook M3) amortised over 3 years ≈ negligible per-token<br>
• No rate limits, no subscription, no per-seat pricing<br><br>
<b style="color:var(--text);">Hidden cloud costs:</b> egress fees, data processing agreements, compliance audits, vendor lock-in.
</div>
</div>
""", unsafe_allow_html=True)

    st.divider()
    st.markdown("#### 🗺️ Decision Guide: Local vs Cloud")
    st.markdown("""
<table class="tradeoff-table">
<thead><tr><th>Criterion</th><th>Choose Local SLM</th><th>Choose Cloud LLM</th></tr></thead>
<tbody>
<tr><td>Data sensitivity</td><td style="color:var(--accent3);">PII / regulated / confidential</td><td style="color:var(--muted);">Public / non-sensitive</td></tr>
<tr><td>Latency requirement</td><td style="color:var(--accent3);">Offline / real-time edge</td><td style="color:var(--muted);">Async / batch OK</td></tr>
<tr><td>Volume</td><td style="color:var(--accent3);">High volume → low marginal cost</td><td style="color:var(--muted);">Low / sporadic volume</td></tr>
<tr><td>Hardware</td><td style="color:var(--accent3);">GPU or modern CPU available</td><td style="color:var(--muted);">No local compute</td></tr>
<tr><td>Task complexity</td><td style="color:var(--accent3);">Structured / repeatable tasks</td><td style="color:var(--muted);">Open-ended complex reasoning</td></tr>
<tr><td>Connectivity</td><td style="color:var(--accent3);">Air-gapped / intermittent</td><td style="color:var(--muted);">Always-on broadband</td></tr>
</tbody>
</table>
""", unsafe_allow_html=True)

    st.divider()
    # Live system snapshot
    st.markdown("#### 🖥️ Live System Snapshot")
    sys2 = get_sys_info()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
<div class="metric-card">
<div class="metric-label">CPU Load</div>
<div class="metric-value" style="color:{'var(--danger)' if sys2['cpu_pct']>85 else 'var(--accent3)'};">{sys2['cpu_pct']}%</div>
<div class="metric-unit">{sys2['cpu_count']} logical cores</div>
</div>""", unsafe_allow_html=True)
    with c2:
        ram_color = "var(--danger)" if sys2["ram_pct"] > 85 else "var(--accent2)"
        st.markdown(f"""
<div class="metric-card">
<div class="metric-label">RAM Pressure</div>
<div class="metric-value" style="color:{ram_color};">{sys2['ram_pct']}%</div>
<div class="metric-unit">{sys2['ram_used_gb']} / {sys2['ram_total_gb']} GB used</div>
</div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
<div class="metric-card">
<div class="metric-label">Platform</div>
<div class="metric-value" style="font-size:1.2rem;">{sys2['platform']}</div>
<div class="metric-unit">inference host</div>
</div>""", unsafe_allow_html=True)