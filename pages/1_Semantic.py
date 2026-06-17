import streamlit as st
import numpy as np
from theme import (COLORS, TYP, STRATEGY_COLORS, GLOBAL_CSS,
                   page_header_html, step_header_html, chunk_card_html,
                   scroll_div, breadcrumb_html, colored_log_html,
                   how_it_works_html, metric_summary_html, completion_arrow_html,
                   progress_bar_css, processing_overlay_html, loading_placeholder_html, icon)
from chunkers import SemanticChunker
from utils import make_page, vector_preview, init_embedder, merge_small_chunks

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

if not st.session_state.get("process_text", "").strip():
    st.warning("📄 Please load a document on the main page first.")
    st.page_link("app.py", label="← Go to Main Page", use_container_width=True)
    st.stop()

STRATEGY = "semantic"
ACCENT = STRATEGY_COLORS[STRATEGY]

st.markdown(progress_bar_css(ACCENT), unsafe_allow_html=True)

st.markdown(
    page_header_html(
        "Semantic Chunker",
        "Topic-boundary detection via embedding centroid comparison",
        icon_name="layers",
        accent=ACCENT,
    ),
    unsafe_allow_html=True,
)

embedder = st.session_state.get("embedder")
if embedder is None:
    embedder = init_embedder("local")
    st.session_state.embedder = embedder
    st.session_state.engine = "local"
    st.info("ℹ️ No engine selected — defaulting to local embedding engine.")

with st.expander("How it works", expanded=True):
    st.markdown(how_it_works_html([
        {"title": "📥 Input",
         "content": "<code>chunk_size</code> + <code>similarity_threshold</code> + Embedder + text"},
        {"title": "⚙️ How it works",
         "content": "<ol>"
                    "<li>Split page into sentences, embed every sentence</li>"
                    "<li>Start a buffer with the first sentence, track its embedding as the centroid</li>"
                    "<li>For each next sentence, compute cosine similarity vs the running centroid</li>"
                    "<li>If similarity drops below threshold — topic shift → flush buffer as one chunk, start new buffer</li>"
                    "<li>Also flush if token budget (<code>chunk_size</code>) is exceeded</li>"
                    "</ol>"},
        {"title": "📤 Output",
         "content": "<code>list[ChunkResult]</code> — flat chunks, no embeddings in output."},
    ], STRATEGY), unsafe_allow_html=True)

with st.expander("Parameters", expanded=True):
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        chunk_size = st.slider("Chunk size (tokens)", 64, 1024,
                                st.session_state.get("chunk_size", 256), 16, key="sem_chunk_size")
    with col_p2:
        default_threshold = st.session_state.get("similarity_threshold", 0.25)
        threshold = st.slider("Similarity threshold", 0.05, 0.95, default_threshold, 0.05,
                              help="Lower = fewer splits. Higher = more splits.", key="sem_threshold")

input_text = st.session_state.get("process_text", "")
page = make_page(input_text)
chunker = SemanticChunker(embedder=embedder, chunk_size=chunk_size, similarity_threshold=threshold)

STEP_LABELS = ["Load Document", "Split & Embed", "Walkthrough", "Final Output"]
P = "sem_"

def _cosine_sim(a, b):
    a_arr = np.array(a, dtype=np.float64)
    b_arr = np.array(b, dtype=np.float64)
    dot = float(np.dot(a_arr, b_arr))
    na, nb = float(np.linalg.norm(a_arr)), float(np.linalg.norm(b_arr))
    return 0.0 if na == 0 or nb == 0 else dot / (na * nb)

def _compute_centroid(vecs):
    return list(np.mean(np.array(vecs, dtype=np.float64), axis=0))

def _categorize_reason(reason: str) -> str:
    if "Topic" in reason:
        return "Topic Shift"
    if "Token cap" in reason or "cap" in reason.lower():
        return "Token Cap"
    return "End of Text"

_input_hash = hash(input_text)
if st.session_state.get(f"{P}_input_hash") != _input_hash:
    embed_placeholder = st.empty()
    embed_placeholder.markdown(
        loading_placeholder_html("Splitting sentences & computing embeddings...", ACCENT,
                                 "Embedding each sentence — this may take a moment"),
        unsafe_allow_html=True,
    )
    with st.spinner():
        sentences = chunker._split_sentences(input_text)
        vecs = embedder.embed(sentences) if len(sentences) > 0 else []
    embed_placeholder.empty()
    st.session_state[f"{P}_sentences"] = sentences
    st.session_state[f"{P}_vecs"] = vecs
    st.session_state[f"{P}_input_hash"] = _input_hash
    for k in list(st.session_state.keys()):
        if k.startswith(P) and k not in (f"{P}_sentences", f"{P}_vecs", f"{P}_input_hash"):
            del st.session_state[k]

sentences = st.session_state.get(f"{P}_sentences", [])
vecs = st.session_state.get(f"{P}_vecs", [])
total_sentences = len(sentences)

walkthrough_done = st.session_state.get(f"{P}_step", 0) >= total_sentences and not st.session_state.get(f"{P}_buffer", [])
chunks_emitted = len(st.session_state.get(f"{P}_chunks", [])) > 0
done_mask = [True, True, walkthrough_done, chunks_emitted]

st.markdown(breadcrumb_html(STEP_LABELS, done_mask, STRATEGY), unsafe_allow_html=True)
st.markdown("---")

# ── STEP 1: Load Document ──────────────────────────────────────────
st.markdown(step_header_html(1, "Load Document", "completed", ACCENT, "file-text"), unsafe_allow_html=True)
st.info(f"📄 Loaded {len(input_text)} characters")
st.markdown("---")

# ── STEP 2: Split Sentences + Embed ─────────────────────────────────
st.markdown(step_header_html(2, "Split Sentences & Generate Embeddings", "completed", ACCENT, "scissors"), unsafe_allow_html=True)
with st.expander("View sentences & embeddings", expanded=False):
    st.markdown(scroll_div("".join(
        f'<div style="{TYP["small"]};padding:3px 0;border-bottom:1px solid {COLORS["border"]};">'
        f'<b style="color:{ACCENT};">s{i+1}</b> <code style="color:{COLORS["text_secondary"]};">{s}</code>'
        f'<br><span style="color:{COLORS["text_muted"]};font-size:0.75rem;">{vector_preview(vecs[i])}</span></div>'
        for i, (s, v) in enumerate(zip(sentences, vecs))
    ) + f'<div style="color:{COLORS["text_secondary"]};{TYP["small"]};padding-top:6px;">Total: {len(sentences)} sentences</div>'), unsafe_allow_html=True)
st.markdown("---")

if len(sentences) < 2:
    st.warning("Need at least 2 sentences for the semantic walkthrough.")
    st.stop()


def _merge_stored_chunks():
    min_tok = st.session_state.get("min_chunk_tokens", 0)
    if min_tok <= 0:
        return
    chunks = st.session_state.get(f"{P}_chunks", [])
    reasons = st.session_state.get(f"{P}_chunk_reasons", [])
    if not chunks:
        return
    items = [{"chunk_text": c, "token_count": chunker.count_tokens(c), "reason": r}
             for c, r in zip(chunks, reasons)]
    items = merge_small_chunks(items, min_tok)
    st.session_state[f"{P}_chunks"] = [it["chunk_text"] for it in items]
    st.session_state[f"{P}_chunk_reasons"] = [it["reason"] for it in items]


def process_one():
    step = st.session_state[f"{P}_step"]
    total = len(sentences)
    next_idx = step + 1
    if next_idx >= total:
        if st.session_state[f"{P}_buffer"]:
            chunk_text = " ".join(st.session_state[f"{P}_buffer"])
            st.session_state[f"{P}_chunks"].append(chunk_text)
            st.session_state[f"{P}_chunk_reasons"].append("End of text")
            st.session_state[f"{P}_log"].append("📦 FINAL CHUNK (end of text)")
            st.session_state[f"{P}_buffer"] = []
            st.session_state[f"{P}_buffer_vecs"] = []
        st.session_state[f"{P}_step"] = total
        return True, "end_of_text"
    next_sent = sentences[next_idx]
    next_vec = vecs[next_idx]
    centroid = st.session_state[f"{P}_centroid"]
    buffer = st.session_state[f"{P}_buffer"]
    buffer_vecs = st.session_state[f"{P}_buffer_vecs"]
    c = SemanticChunker(embedder=embedder, chunk_size=chunk_size, similarity_threshold=threshold)
    sim = _cosine_sim(next_vec, centroid)
    buffer_tokens_now = c.count_tokens(" ".join(buffer))
    sent_tokens = c.count_tokens(next_sent)
    token_cap_hit = buffer and (buffer_tokens_now + sent_tokens > chunk_size)
    if (sim < threshold) or token_cap_hit:
        chunk_text = " ".join(buffer)
        st.session_state[f"{P}_chunks"].append(chunk_text)
        if sim < threshold and token_cap_hit:
            reason = "Topic shift + token cap"
        elif sim < threshold:
            reason = f"Topic shift (cosine {sim:.2f} < {threshold})"
        else:
            reason = f"Token cap ({buffer_tokens_now + sent_tokens}/{chunk_size})"
        st.session_state[f"{P}_chunk_reasons"].append(reason)
        st.session_state[f"{P}_log"].append(f"❌ s{next_idx+1} FLUSHED → chunk {len(st.session_state[f'{P}_chunks'])}: {reason}")
        st.session_state[f"{P}_buffer"] = [next_sent]
        st.session_state[f"{P}_buffer_vecs"] = [next_vec]
        st.session_state[f"{P}_centroid"] = list(next_vec)
        st.session_state[f"{P}_step"] = next_idx
        return True, reason
    else:
        st.session_state[f"{P}_buffer"].append(next_sent)
        st.session_state[f"{P}_buffer_vecs"].append(next_vec)
        st.session_state[f"{P}_centroid"] = _compute_centroid(st.session_state[f"{P}_buffer_vecs"])
        st.session_state[f"{P}_step"] = next_idx
        st.session_state[f"{P}_log"].append(f"✅ s{next_idx+1} ADDED → {len(st.session_state[f'{P}_buffer'])} in buffer")
        st.session_state[f"{P}_cosine_last"] = sim
        return False, ""


# ── Execution Mode ─────────────────────────────────────────────────
st.markdown("### Execution Mode")

mode = st.radio(
    "Mode",
    ["Developer", "Auto"],
    index=0,
    horizontal=True,
    label_visibility="visible",
)

is_dev = mode == "Developer"
dev_border = ACCENT if is_dev else COLORS["border"]
dev_color = ACCENT if is_dev else COLORS["text_muted"]
dev_opacity = "1" if is_dev else "0.45"
auto_border = ACCENT if not is_dev else COLORS["border"]
auto_color = ACCENT if not is_dev else COLORS["text_muted"]
auto_opacity = "1" if not is_dev else "0.45"

col_dev, col_auto = st.columns(2)
with col_dev:
    st.markdown(
        f'<div style="text-align:center;padding:14px 12px;background:{COLORS["surface"]};'
        f'border-radius:10px;border:2px solid {dev_border};opacity:{dev_opacity};'
        f'transition:border-color 0.2s,opacity 0.2s;">'
        f'<div style="color:{dev_color};margin-bottom:6px;">{icon("wrench", 24)}</div>'
        f'<div style="font-size:0.72rem;color:{COLORS["text_muted"]};">Step by step · inspect each decision</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
with col_auto:
    st.markdown(
        f'<div style="text-align:center;padding:14px 12px;background:{COLORS["surface"]};'
        f'border-radius:10px;border:2px solid {auto_border};opacity:{auto_opacity};'
        f'transition:border-color 0.2s,opacity 0.2s;">'
        f'<div style="color:{auto_color};margin-bottom:6px;">{icon("zap", 24)}</div>'
        f'<div style="font-size:0.72rem;color:{COLORS["text_muted"]};">Run all at once · see final results</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

if mode == "Auto":
    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
    if st.button("Run Strategy to Completion", type="primary", use_container_width=True, key="sem_auto_run"):
        while st.session_state[f"{P}_step"] < total_sentences or st.session_state[f"{P}_buffer"]:
            process_one()
        _merge_stored_chunks()
        st.session_state[f"{P}_status"] = "✅ All done"
        st.rerun()

st.markdown("---")

# ── Init walkthrough state ─────────────────────────────────────────
if f"{P}_step" not in st.session_state:
    st.session_state[f"{P}_step"] = 0
    st.session_state[f"{P}_buffer"] = [sentences[0]]
    st.session_state[f"{P}_buffer_vecs"] = [vecs[0]]
    st.session_state[f"{P}_centroid"] = list(vecs[0])
    st.session_state[f"{P}_chunks"] = []
    st.session_state[f"{P}_chunk_reasons"] = []
    st.session_state[f"{P}_log"] = [f"✅ s1 ADDED → 1 in buffer (starting)"]
    st.session_state[f"{P}_cosine_last"] = None
    st.session_state[f"{P}_status"] = ""

prev_th = st.session_state.get(f"{P}_prev_threshold")
if prev_th is not None and threshold != prev_th:
    keep = {f"{P}_sentences", f"{P}_vecs", f"{P}_input_hash"}
    for k in list(st.session_state.keys()):
        if k.startswith(P) and k not in keep:
            del st.session_state[k]
    st.session_state[f"{P}_prev_threshold"] = threshold
    st.session_state.similarity_threshold = threshold
    st.rerun()
st.session_state[f"{P}_prev_threshold"] = threshold

# ── STEP 3: Walkthrough ────────────────────────────────────────────
st.markdown(step_header_html(3, "Cosine Similarity Walkthrough",
                              "completed" if walkthrough_done else "active", ACCENT, "refresh-cw"), unsafe_allow_html=True)

# ── Controls ──────────────────────────────────────────────────────
col_btn, col_stat = st.columns([2, 1])
with col_btn:
    b1, b2 = st.columns(2)
    with b1:
        btn_chunks = st.button("Build Next 3 Chunks", type="primary", use_container_width=True, key="sem_dev_3")
    with b2:
        btn_all = st.button("Run All Remaining", type="primary", use_container_width=True, key="sem_dev_all")
with col_stat:
    st.markdown(f"**Buffer:** {len(st.session_state[f'{P}_buffer'])} sentences")
    st.markdown(f"**Chunks:** {len(st.session_state[f'{P}_chunks'])}")
if btn_chunks:
    st.session_state[f"{P}_pending"] = 3
    st.rerun()
if btn_all:
    while st.session_state[f"{P}_step"] < total_sentences or st.session_state[f"{P}_buffer"]:
        process_one()
    _merge_stored_chunks()
    st.session_state[f"{P}_status"] = "✅ All done"
    st.rerun()
if st.session_state.get(f"{P}_pending", 0) > 0:
    prev_count = len(st.session_state[f"{P}_chunks"])
    process_one()
    if len(st.session_state[f"{P}_chunks"]) > prev_count:
        st.session_state[f"{P}_pending"] -= 1
    if st.session_state[f"{P}_pending"] > 0 and st.session_state[f"{P}_step"] < total_sentences:
        st.rerun()
    else:
        st.session_state[f"{P}_pending"] = 0
        st.rerun()

processed = st.session_state[f"{P}_step"] + 1
sentences_done = min(processed, total_sentences)
st.progress(sentences_done / total_sentences if total_sentences > 0 else 0,
            text=f"Sentence {sentences_done} of {total_sentences}")

# ── Walkthrough details (Developer) ──
if mode == "Developer":
    step = st.session_state[f"{P}_step"]
    buf = st.session_state[f"{P}_buffer"]
    centroid = st.session_state[f"{P}_centroid"]
    next_idx = step + 1

    col_state, col_next = st.columns(2)
    with col_state:
        with st.container(border=True):
            st.markdown(f"**📦 Current Buffer** — {len(buf)} sentence{'s' if len(buf)!=1 else ''}")
            st.caption(" ".join(buf)[:200] + ("..." if len(" ".join(buf)) > 200 else ""))
            st.markdown(f"**Centroid:** {vector_preview(centroid)}")

    if next_idx < total_sentences:
        next_sent = sentences[next_idx]
        next_vec = vecs[next_idx]
        sim = _cosine_sim(next_vec, centroid)
        with col_next:
            with st.container(border=True):
                st.markdown(f"**🔍 Trying s{next_idx+1}**")
                st.caption(next_sent[:150] + ("..." if len(next_sent) > 150 else ""))
                st.markdown(f"**Cosine similarity:** `{sim:.4f}` vs threshold `{threshold}`")
                if sim >= threshold:
                    st.success(f"✅ {sim:.4f} ≥ {threshold} → SAME TOPIC (add to buffer)")
                else:
                    st.error(f"❌ {sim:.4f} < {threshold} → TOPIC SHIFT (flush buffer)")

        buf_tokens = chunker.count_tokens(" ".join(buf))
        next_tokens = chunker.count_tokens(next_sent)
        if buf and buf_tokens + next_tokens > chunk_size:
            with st.container(border=True):
                st.warning(f"⚠️ Token cap: {buf_tokens + next_tokens}/{chunk_size} — will flush on next step")
    else:
        with col_next:
            with st.container(border=True):
                if not buf:
                    st.success("✅ All done! Chunks ready below.")
                else:
                    st.info("⏳ Processing final buffer...")
                    st.caption(" ".join(buf)[:200])

# ── Split log ──
log = st.session_state.get(f"{P}_log", [])
if log:
    with st.expander("Split Log", expanded=True):
        st.markdown(
            f'<div style="font-size:0.75rem;color:{COLORS["text_secondary"]};margin-bottom:8px;display:flex;gap:16px;flex-wrap:wrap;">'
            f'<span><span style="color:{COLORS["success"]};">●</span> ADDED → sentence joined buffer</span>'
            f'<span><span style="color:{COLORS["error"]};">●</span> FLUSHED → buffer emitted as chunk</span>'
            f'<span><span style="color:{COLORS["warning"]};">●</span> FINAL → last chunk (end of text)</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(colored_log_html(log), unsafe_allow_html=True)

if st.session_state.get(f"{P}_status"):
    st.info(st.session_state[f"{P}_status"])

if walkthrough_done:
    st.markdown(completion_arrow_html(), unsafe_allow_html=True)
st.markdown("---")

# ── STEP 4: Final Output ───────────────────────────────────────────
st.markdown(step_header_html(4, "Final Output",
                              "completed" if chunks_emitted else "upcoming", ACCENT, "package"), unsafe_allow_html=True)

chunks = st.session_state.get(f"{P}_chunks", [])
chunk_reasons = st.session_state.get(f"{P}_chunk_reasons", [])

if chunks:
    total_tokens = sum(chunker.count_tokens(c) for c in chunks)
    topic_shifts = sum(1 for r in chunk_reasons if "Topic" in r)
    token_caps = sum(1 for r in chunk_reasons if "Token cap" in r or "cap" in r.lower())
    st.markdown(metric_summary_html([
        (str(len(chunks)), "Total Chunks", "Number of chunks produced"),
        (str(total_tokens), "Total Tokens", "Sum of tokens across all chunks"),
        (str(topic_shifts), "Topic Shifts", "Chunks flushed due to topic boundary"),
        (str(token_caps), "Token Cap Hits", "Chunks flushed due to token limit"),
    ], STRATEGY), unsafe_allow_html=True)

    show_all = st.session_state.get(f"{P}_show_all", False)
    display = chunks if show_all else chunks[:15]
    cards_html = scroll_div("".join(
        chunk_card_html(
            idx=i,
            chunk_text=c,
            token_count=chunker.count_tokens(c),
            strategy=STRATEGY,
            extra_fields={
                "chunk_index": i,
                "token_count": chunker.count_tokens(c),
                "chunk_strategy": "semantic",
                "page_number": 0,
                "source_uri": None,
            },
            badge=_categorize_reason(chunk_reasons[i]) if i < len(chunk_reasons) else None,
        ) for i, c in enumerate(display)
    ))
    st.markdown(cards_html, unsafe_allow_html=True)
    if len(chunks) > 15:
        btn_label = f"Show all {len(chunks)} chunks" if not show_all else "Show fewer"
        if st.button(btn_label, use_container_width=True, key="sem_toggle"):
            st.session_state[f"{P}_show_all"] = not show_all
            st.rerun()
else:
    st.info("No chunks emitted yet — run the walkthrough above.")

st.markdown("---")
if st.button("Reset & Run Again", use_container_width=True, key="sem_reset"):
    keep = {f"{P}_sentences", f"{P}_vecs", f"{P}_input_hash"}
    for k in list(st.session_state.keys()):
        if k.startswith(P) and k not in keep:
            del st.session_state[k]
    st.rerun()
