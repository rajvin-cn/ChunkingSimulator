import streamlit as st
from theme import (COLORS, TYP, STRATEGY_COLORS, GLOBAL_CSS,
                   page_header_html, step_header_html, chunk_card_html,
                   scroll_div, breadcrumb_html, how_it_works_html,
                   metric_summary_html, completion_arrow_html,
                   progress_bar_css, processing_overlay_html, loading_placeholder_html, icon)
from chunkers import LateChunker
from utils import make_page, vector_preview, init_embedder, merge_small_chunks

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

if not st.session_state.get("process_text", "").strip():
    st.warning("📄 Please load a document on the main page first.")
    st.page_link("app.py", label="← Go to Main Page", use_container_width=True)
    st.stop()

STRATEGY = "late"
ACCENT = STRATEGY_COLORS[STRATEGY]

st.markdown(progress_bar_css(ACCENT), unsafe_allow_html=True)

st.markdown(
    page_header_html(
        "Late Chunker",
        "Embed full page first, then chunk with dual context-aware vectors",
        icon_name="brain",
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
         "content": "<code>chunk_size</code> + Embedder + text"},
        {"title": "⚙️ How it works",
         "content": "<ol>"
                    "<li>Embed the entire page as a full-page vector</li>"
                    "<li>Split into chunks (~chunk_size tokens)</li>"
                    "<li>Embed each chunk separately</li>"
                    "<li>Each chunk gets two vectors: chunk_embedding + full_page_embedding</li>"
                    "</ol>"},
        {"title": "📤 Output",
         "content": "<code>list[ChunkResult]</code> — flat, each with pre-computed chunk_embedding + full_page_embedding."},
    ], STRATEGY), unsafe_allow_html=True)

with st.expander("Parameters", expanded=True):
    chunk_size = st.slider("Chunk size (tokens)", 64, 1024,
                            st.session_state.get("chunk_size", 256), 16, key="late_chunk_size")

input_text = st.session_state.get("process_text", "")
page = make_page(input_text)
chunker = LateChunker(embedder=embedder, chunk_size=chunk_size)

sample_placeholder = st.empty()
sample_placeholder.markdown(
    loading_placeholder_html("Computing sample embedding...", ACCENT,
                             "Initializing the embedding model"),
    unsafe_allow_html=True,
)
with st.spinner():
    sample_vec = embedder.embed(["test"])[0]
sample_placeholder.empty()
dim_display = f"{len(sample_vec)}-dim"

STEP_LABELS = ["Load Document", "Split Sentences", "Embed Full Page", "Split Chunks", "Embed Chunks", "Final Output"]
P = "late_"

_input_hash = hash(input_text)
if st.session_state.get(f"{P}_input_hash") != _input_hash:
    sentences = chunker._split_sentences(input_text)
    st.session_state[f"{P}_sentences"] = sentences
    st.session_state[f"{P}_input_hash"] = _input_hash
    for k in [f"{P}_full_vec", f"{P}_chunks_data", f"{P}_results"]:
        st.session_state.pop(k, None)

sentences = st.session_state.get(f"{P}_sentences", [])
total_sentences = len(sentences)

full_vec_done = st.session_state.get(f"{P}_full_vec") is not None
chunks_done = st.session_state.get(f"{P}_chunks_data") is not None
results_done = st.session_state.get(f"{P}_results") is not None
done_mask = [True, True, full_vec_done, chunks_done, results_done, results_done]

st.markdown(breadcrumb_html(STEP_LABELS, done_mask, STRATEGY), unsafe_allow_html=True)
st.markdown("---")

# ── STEP 1: Load Document ──────────────────────────────────────────
st.markdown(step_header_html(1, "Load Document", "completed", ACCENT, "file-text"), unsafe_allow_html=True)
st.info(f"📄 Loaded {len(input_text)} characters")
st.markdown("---")

# ── STEP 2: Split Sentences ─────────────────────────────────────────
st.markdown(step_header_html(2, "Split into Sentences", "completed", ACCENT, "scissors"), unsafe_allow_html=True)
with st.expander("View sentences", expanded=False):
    sents_html = scroll_div("".join(
        f'<div style="{TYP["small"]};padding:3px 0;border-bottom:1px solid {COLORS["border"]};">'
        f'<b style="color:{ACCENT};">s{i+1}</b> '
        f'<code style="color:{COLORS["text_secondary"]};">{s}</code></div>'
        for i, s in enumerate(sentences)
    ) + f'<div style="color:{COLORS["text_secondary"]};{TYP["small"]};padding-top:6px;">Total: {len(sentences)} sentences</div>')
    st.markdown(sents_html, unsafe_allow_html=True)
st.markdown("---")

if len(sentences) < 1:
    st.warning("No sentences to process.")
    st.stop()


def run_all():
    p1 = st.empty()
    p1.markdown(loading_placeholder_html("Embedding full page...", ACCENT,
                                         "Encoding the complete document as a single vector"),
                unsafe_allow_html=True)
    with st.spinner():
        full_vector = chunker._embed_full_page(input_text)
    p1.empty()
    st.session_state[f"{P}_full_vec"] = full_vector
    buffers = split_chunks()
    p2 = st.empty()
    p2.markdown(loading_placeholder_html("Embedding each chunk...", ACCENT,
                                         f"Encoding {len(buffers)} chunks individually"),
                unsafe_allow_html=True)
    with st.spinner():
        chunk_vecs = embedder.embed(buffers)
    p2.empty()
    results = []
    for i, (ct, cv) in enumerate(zip(buffers, chunk_vecs)):
        results.append({
            "chunk_text": ct,
            "chunk_embedding": cv,
            "full_page_embedding": full_vector,
            "token_count": chunker.count_tokens(ct),
        })
    st.session_state[f"{P}_results"] = results


def split_chunks():
    buffers = []
    buf = []
    buf_tok = 0
    for s in sentences:
        tk = chunker.count_tokens(s)
        if buf and buf_tok + tk > chunker.chunk_size:
            buffers.append(" ".join(buf))
            buf, buf_tok = [s], tk
        else:
            buf.append(s)
            buf_tok += tk
    if buf:
        buffers.append(" ".join(buf))
    st.session_state[f"{P}_chunks_data"] = buffers
    return buffers


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
        f'<div style="font-size:0.72rem;color:{COLORS["text_muted"]};">Step by step · inspect each stage</div>'
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

if mode == "Auto" and not results_done:
    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
    if st.button("Run Strategy to Completion", type="primary", use_container_width=True, key="late_auto_run"):
        run_all()
        st.rerun()

st.markdown("---")

# ── STEP 3: Embed Full Page ────────────────────────────────────────
st.markdown(step_header_html(3, "Embed Full Page Once",
                              "completed" if full_vec_done else "active", ACCENT, "globe"), unsafe_allow_html=True)

if mode == "Developer":
    if not full_vec_done:
        if st.button("Embed Full Page", type="primary", use_container_width=True, key="late_embed_full"):
            p = st.empty()
            p.markdown(loading_placeholder_html("Embedding full page...", ACCENT,
                                                "Encoding the complete document as a single vector"),
                       unsafe_allow_html=True)
            with st.spinner():
                full_vector = chunker._embed_full_page(input_text)
            st.session_state[f"{P}_full_vec"] = full_vector
            p.empty()
            st.rerun()

full_vec = st.session_state.get(f"{P}_full_vec")
if full_vec:
    st.code(f"full_page_embedding = {vector_preview(full_vec)}", language="text")
    st.caption("This single vector captures the **entire page** meaning.")

if full_vec_done:
    st.markdown(completion_arrow_html(), unsafe_allow_html=True)
st.markdown("---")

# ── STEP 4: Split into Chunks ──────────────────────────────────────
st.markdown(step_header_html(4, "Split into Chunks",
                              "completed" if chunks_done else "active" if full_vec_done else "upcoming",
                              ACCENT, "scissors"), unsafe_allow_html=True)

if mode == "Developer":
    if full_vec_done and not chunks_done:
        if st.button("Split Text into Chunks", type="primary", use_container_width=True, key="late_split"):
            split_chunks()
            st.rerun()

chunks_data = st.session_state.get(f"{P}_chunks_data", [])
if chunks_data:
    chunks_html = scroll_div("".join(
        f'<div class="card-hover" style="border:1px solid {COLORS["border"]};border-radius:8px;padding:10px;margin:4px 0;'
        f'border-left:3px solid {ACCENT};">'
        f'<b>Chunk {i}</b> <span style="color:{COLORS["text_muted"]};">({chunker.count_tokens(c)} tokens)</span><br>'
        f'<code style="color:{COLORS["text_secondary"]};">{c[:200]}{"..." if len(c) > 200 else ""}</code></div>'
        for i, c in enumerate(chunks_data)
    ))
    st.markdown(chunks_html, unsafe_allow_html=True)

if chunks_done:
    st.markdown(completion_arrow_html(), unsafe_allow_html=True)
st.markdown("---")

# ── STEP 5: Embed Each Chunk ───────────────────────────────────────
st.markdown(step_header_html(5, "Embed Each Chunk Separately",
                              "completed" if results_done else "active" if chunks_done else "upcoming",
                              ACCENT, "target"), unsafe_allow_html=True)

if mode == "Developer":
    if chunks_done and not results_done:
        if st.button("Embed Each Chunk", type="primary", use_container_width=True, key="late_embed_chunks"):
            p = st.empty()
            p.markdown(loading_placeholder_html("Embedding each chunk...", ACCENT,
                                                f"Encoding {len(chunks_data)} chunks individually"),
                       unsafe_allow_html=True)
            with st.spinner():
                chunk_vecs = embedder.embed(chunks_data)
                results = []
                for i, (ct, cv) in enumerate(zip(chunks_data, chunk_vecs)):
                    results.append({
                        "chunk_text": ct,
                        "chunk_embedding": cv,
                        "full_page_embedding": full_vec,
                        "token_count": chunker.count_tokens(ct),
                    })
                st.session_state[f"{P}_results"] = results
            p.empty()
            st.rerun()

results = st.session_state.get(f"{P}_results")
if results:
    min_tok = st.session_state.get("min_chunk_tokens", 0)
    if min_tok > 0:
        results = merge_small_chunks(results, min_tok)

if results_done and results:
    st.success(f"✅ Embedded all {len(results)} chunks!")
    st.markdown(completion_arrow_html(), unsafe_allow_html=True)
st.markdown("---")

# ── STEP 6: Final Output ───────────────────────────────────────────
st.markdown(step_header_html(6, "Final Output",
                              "completed" if results_done else "upcoming", ACCENT, "package"), unsafe_allow_html=True)

if results:
    total_tokens = sum(r["token_count"] for r in results)
    st.markdown(metric_summary_html([
        (str(len(results)), "Total Chunks", "Number of chunks produced"),
        (str(total_tokens), "Total Tokens", "Sum of tokens across all chunks"),
    ], STRATEGY), unsafe_allow_html=True)

    show_all = st.session_state.get(f"{P}_show_all", False)
    display = results if show_all else results[:15]
    cards_html = scroll_div("".join(
        chunk_card_html(
            idx=i,
            chunk_text=r["chunk_text"],
            token_count=r["token_count"],
            strategy=STRATEGY,
            extra_fields={
                "chunk_index": i,
                "token_count": r["token_count"],
                "chunk_strategy": "late",
                "page_number": 0,
                "source_uri": None,
                "chunk_embedding": vector_preview(r["chunk_embedding"]),
                "full_page_embedding": vector_preview(r["full_page_embedding"]),
            }
        ) for i, r in enumerate(display)
    ))
    st.markdown(cards_html, unsafe_allow_html=True)
    if len(results) > 15:
        btn_label = f"Show all {len(results)} chunks" if not show_all else "Show fewer"
        if st.button(btn_label, use_container_width=True, key="late_toggle"):
            st.session_state[f"{P}_show_all"] = not show_all
            st.rerun()
else:
    st.info("Run through Steps ①—⑤ first.")

st.markdown("---")
if st.button("Reset & Run Again", use_container_width=True, key="late_reset"):
    keep = {f"{P}_sentences", f"{P}_input_hash"}
    for k in [f"{P}_full_vec", f"{P}_chunks_data", f"{P}_results"]:
        st.session_state.pop(k, None)
    st.rerun()
