import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from utils import init_embedder, ENGINE_DEFAULTS
from theme import (GLOBAL_CSS, COLORS, TYP, STRATEGY_COLORS,
                   page_header_html, step_header_html, stepper_html,
                   badge_html, icon, loading_placeholder_html)

load_dotenv(Path(__file__).parent / ".env")

st.set_page_config(
    page_title="Chunking Visualizer",
    page_icon="🧩",
    layout="wide",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

SAMPLE_DIR = Path(__file__).parent / "sample_texts"
DEMO_PATH = SAMPLE_DIR / "demo.txt"


def load_demo_text() -> str:
    return DEMO_PATH.read_text()


# ── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;padding:4px 0;">'
        f'<span style="font-size:1.5rem;">🧩</span>'
        f'<span style="{TYP["h3"]}color:{COLORS["text"]};">Chunking Visualizer</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

# ── Page Header ──────────────────────────────────────────────────────
st.markdown(
    page_header_html(
        "Chunking Visualizer",
        "Explore how different chunking strategies split text — "
        "Semantic, Hierarchical, and Late.",
        icon_name="cpu",
        accent=COLORS["primary"],
    ),
    unsafe_allow_html=True,
)

# ── Setup Stepper ────────────────────────────────────────────────────
guide_labels = ["Choose Engine", "Load Document", "Set Max Characters", "Explore Strategy"]
guide_done = [
    st.session_state.get("embedder") is not None,
    st.session_state.get("input_text") is not None and len(st.session_state.get("input_text", "")) > 0,
    st.session_state.get("max_chars", 0) > 0,
    False,
]
st.markdown(stepper_html(guide_labels, guide_done, COLORS["primary"]), unsafe_allow_html=True)
st.markdown("---")

# ── ① Engine ────────────────────────────────────────────────────────
st.markdown(
    step_header_html(1, "Embedding Engine",
                     "active" if not guide_done[0] else "completed",
                     COLORS["primary"], "cpu"),
    unsafe_allow_html=True,
)

engine = st.radio(
    "Select engine",
    options=["local", "euri"],
    format_func=lambda x: ENGINE_DEFAULTS[x]["label"],
    index=0,
    horizontal=True,
    label_visibility="visible",
)
st.session_state.engine = engine
engine_cfg = ENGINE_DEFAULTS[engine]

prev_engine = st.session_state.get("_prev_engine")
euri_key = ""
euri_url = "https://api.euron.one/api/v1/euri"
euri_model = "gemini-embedding-2"

if engine == "euri":
    st.markdown("### EURI API Credentials")
    col_k, col_u, col_m = st.columns(3)
    with col_k:
        euri_key = st.text_input("API Key", type="password", value="",
                                  help="Enter your EURI API key")
        if not euri_key:
            st.info("No key entered — falling back to local embedding engine")
    with col_u:
        euri_url = st.text_input("Base URL", value="https://api.euron.one/api/v1/euri")
    with col_m:
        euri_model = st.text_input("Model", value="gemini-embedding-2")

st.markdown("---")

# ── Build / update embedder ─────────────────────────────────────────
embedder_key = f"embedder_{engine}"

if prev_engine != engine or embedder_key not in st.session_state:
    if engine == "euri" and not euri_key:
        st.session_state[embedder_key] = init_embedder("local")
    else:
        placeholder = st.empty()
        placeholder.markdown(
            loading_placeholder_html("Loading embedding model...", COLORS["primary"],
                                     "Downloading and caching — this may take a moment on first run"),
            unsafe_allow_html=True,
        )
        with st.spinner():
            st.session_state[embedder_key] = init_embedder(
                engine,
                api_key=euri_key,
                base_url=euri_url,
                model=euri_model,
            )
        placeholder.empty()
    st.session_state.similarity_threshold = engine_cfg["similarity_threshold"]
    st.session_state.chunk_size = engine_cfg["chunk_size"]
    st.session_state._prev_engine = engine

st.session_state.embedder = st.session_state.get(embedder_key)

# ── ② Document ──────────────────────────────────────────────────────
st.markdown(
    step_header_html(2, "Load Document",
                     "active" if guide_done[0] and not guide_done[1]
                     else "completed" if guide_done[1] else "upcoming",
                     COLORS["primary"], "file-text"),
    unsafe_allow_html=True,
)

doc_col, _ = st.columns([3, 2])
with doc_col:
    load_option = st.radio("Load text from:", ["📄 Demo text", "📁 Upload .txt"], horizontal=True)

    if load_option == "📄 Demo text":
        st.success("✅ Loaded demo text")
    else:
        uploaded = st.file_uploader("Upload a .txt file", type=["txt"],
                                    help="Upload a plain text file to chunk",
                                    label_visibility="collapsed")
        if uploaded:
            new_text = uploaded.read().decode("utf-8")
            if st.session_state.get("input_text") != new_text:
                st.session_state.input_text = new_text

    if "input_text" not in st.session_state:
        st.session_state.input_text = load_demo_text()

    raw_text = st.session_state.get("input_text", "")

    # ── ③ Max chars + min tokens ────────────────────────────────────────
    st.markdown(
        step_header_html(3, "Set Maximum Characters to Process",
                         "active" if guide_done[1] and not guide_done[2]
                         else "completed" if guide_done[2] else "upcoming",
                         COLORS["primary"], "scissors"),
        unsafe_allow_html=True,
    )

    doc_len = len(raw_text)
    max_val = max(doc_len, 1000)
    current = st.session_state.get("max_chars", 300)
    if current > max_val:
        current = max_val

    slider_col, _ = st.columns([2, 3])
    with slider_col:
        max_chars = st.slider(
            "Max characters to process",
            0, max_val, current, 500,
            help=f"0 = full document ({doc_len} chars)",
        )
    st.session_state.max_chars = max_chars

    min_chunk_tokens = st.slider(
        "Min tokens per chunk",
        64, 200, st.session_state.get("min_chunk_tokens", 64), 16,
        help="Merges smaller chunks into the previous chunk.",
    )
    st.session_state.min_chunk_tokens = min_chunk_tokens

    if max_chars > 0 and len(raw_text) > max_chars:
        process_text = raw_text[:max_chars]
    else:
        process_text = raw_text
    st.session_state.process_text = process_text

    if max_chars > 0 and len(raw_text) > max_chars:
        st.caption(f"⚠️ Truncated to {max_chars} chars (original: {doc_len})")
    else:
        st.caption(f"📄 {doc_len} chars loaded")

st.markdown("---")

# ── ④ Explore Strategy ──────────────────────────────────────────────
st.markdown(
    step_header_html(4, "Explore a Strategy",
                     "active" if guide_done[2] else "upcoming",
                     COLORS["primary"], "zap"),
    unsafe_allow_html=True,
)

cards = [
    ("layers",     "Semantic",      "Topic-boundary detection via embedding centroid comparison", "pages/1_Semantic.py"),
    ("git-branch", "Hierarchical",  "Rule-based parent/child two-level chunking — no ML required", "pages/2_Hierarchical.py"),
    ("brain",      "Late",          "Embed full page first, then chunk with dual context-aware vectors", "pages/3_Late.py"),
    ("split",      "Compare All",   "Run 2–3 strategies side by side on the same text", "pages/4_Compare.py"),
]

col_n1, col_n2, col_n3, col_n4 = st.columns(4)

for col, (icon_name, title, desc, page) in zip([col_n1, col_n2, col_n3, col_n4], cards):
    with col:
        with st.container(border=True):
            st.markdown(
                f'<div style="text-align:center;padding:8px 0 4px 0;color:{COLORS["text_secondary"]};">'
                f'{icon(icon_name, 32)}</div>',
                unsafe_allow_html=True,
            )
            st.page_link(page, label=title, use_container_width=True)
            st.caption(desc)
