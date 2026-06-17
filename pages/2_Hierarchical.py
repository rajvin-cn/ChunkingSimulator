import streamlit as st
from theme import (COLORS, TYP, STRATEGY_COLORS, GLOBAL_CSS,
                   page_header_html, step_header_html, chunk_card_html,
                   scroll_div, breadcrumb_html, how_it_works_html,
                   metric_summary_html, completion_arrow_html,
                   progress_bar_css, processing_overlay_html, icon)
from chunkers import HierarchicalChunker
from utils import make_page, merge_small_chunks

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

if not st.session_state.get("process_text", "").strip():
    st.warning("📄 Please load a document on the main page first.")
    st.page_link("app.py", label="← Go to Main Page", use_container_width=True)
    st.stop()

STRATEGY = "hierarchical"
ACCENT = STRATEGY_COLORS[STRATEGY]

st.markdown(progress_bar_css(ACCENT), unsafe_allow_html=True)

st.markdown(
    page_header_html(
        "Hierarchical Chunker",
        "Rule-based two-level parent/child chunking — no ML required",
        icon_name="git-branch",
        accent=ACCENT,
    ),
    unsafe_allow_html=True,
)

with st.expander("How it works", expanded=True):
    st.markdown(how_it_works_html([
        {"title": "📥 Input",
         "content": "<code>chunk_size</code> (parent), <code>child_chunk_size</code>, <code>child_overlap</code> + text"},
        {"title": "⚙️ How it works",
         "content": "Two-pass — accumulates sentences into parent chunks (~1024 tokens), then splits each parent into overlapping child chunks. Sentence-aware, deterministic, <b>no ML</b>."},
        {"title": "📤 Output",
         "content": "<code>list[ChunkResult]</code> — parents have <code>parent_chunk_id=None</code>, children have <code>parent_chunk_id=\"parent_{index}\"</code>. No embeddings."},
    ], STRATEGY), unsafe_allow_html=True)

with st.expander("Parameters", expanded=True):
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        parent_size = st.slider("Parent chunk size (tokens)", 64, 2048,
                                 st.session_state.get("chunk_size", 1024), 16, key="hier_parent_cs")
    with col_p2:
        child_cs = st.slider("Child chunk size (tokens)", 32, 512, 128, 16, key="hier_child_cs")
    with col_p3:
        child_ov = st.slider("Child overlap (tokens)", 0, 128, 32, 8, key="hier_child_ov")

input_text = st.session_state.get("process_text", "")
page = make_page(input_text)
chunker = HierarchicalChunker(chunk_size=parent_size, child_chunk_size=child_cs, child_overlap=child_ov)

STEP_LABELS = ["Load Document", "Split Sentences", "Build Parents", "Create Children", "Final Output"]
P = "hier_"

_input_hash = hash(input_text)
if st.session_state.get(f"{P}_input_hash") != _input_hash:
    sentences = chunker._split_sentences(input_text)
    st.session_state[f"{P}_sentences"] = sentences
    st.session_state[f"{P}_input_hash"] = _input_hash
    for k in [f"{P}_parents", f"{P}_children_map", f"{P}_results"]:
        st.session_state.pop(k, None)

sentences = st.session_state.get(f"{P}_sentences", [])
total_sentences = len(sentences)

parents_done = st.session_state.get(f"{P}_parents") is not None
children_done = st.session_state.get(f"{P}_children_map") is not None
results_done = st.session_state.get(f"{P}_results") is not None
done_mask = [True, True, parents_done, children_done, results_done]

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
        f'<code style="color:{COLORS["text_secondary"]};">{s}</code> '
        f'<span style="color:{COLORS["text_muted"]};font-size:0.75rem;">({chunker.count_tokens(s)} tok)</span></div>'
        for i, s in enumerate(sentences)
    ) + f'<div style="color:{COLORS["text_secondary"]};{TYP["small"]};padding-top:6px;">Total: {len(sentences)} sentences</div>')
    st.markdown(sents_html, unsafe_allow_html=True)
st.markdown("---")

if len(sentences) == 0:
    st.warning("No sentences to process.")
    st.stop()


def run_all():
    results = chunker.chunk([page])
    parent_list = [r for r in results if r.parent_chunk_id is None]
    child_list = [r for r in results if r.parent_chunk_id is not None]
    children_map = {}
    for c in child_list:
        children_map.setdefault(c.parent_chunk_id, []).append(c)
    st.session_state[f"{P}_parents"] = [r.chunk_text for r in parent_list]
    st.session_state[f"{P}_children_map"] = children_map
    st.session_state[f"{P}_results"] = results


def build_parents():
    parents = []
    buf = []
    buf_tok = 0
    for s in sentences:
        tk = chunker.count_tokens(s)
        if buf and buf_tok + tk > chunker.chunk_size:
            parents.append(" ".join(buf))
            buf, buf_tok = [s], tk
        else:
            buf.append(s)
            buf_tok += tk
    if buf:
        parents.append(" ".join(buf))
    st.session_state[f"{P}_parents"] = parents
    return parents


def carve_children():
    results = chunker.chunk([page])
    parent_list = [r for r in results if r.parent_chunk_id is None]
    child_list = [r for r in results if r.parent_chunk_id is not None]
    children_map = {}
    for c in child_list:
        pid = c.parent_chunk_id
        children_map.setdefault(pid, []).append(c)
    st.session_state[f"{P}_children_map"] = children_map
    st.session_state[f"{P}_results"] = results
    return children_map, results


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
        f'<div style="font-size:0.72rem;color:{COLORS["text_muted"]};">Step by step · build & inspect each level</div>'
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
    if st.button("Run Strategy to Completion", type="primary", use_container_width=True, key="hier_auto_run"):
        run_all()
        st.rerun()

st.markdown("---")

# ── STEP 3: Build Parents ──────────────────────────────────────────
st.markdown(step_header_html(3, "Build Parent Chunks",
                              "completed" if parents_done else "active", ACCENT, "folder"), unsafe_allow_html=True)

if mode == "Developer":
    if not parents_done:
        if st.button("Build Parents", type="primary", use_container_width=True, key="hier_build_par"):
            build_parents()
            st.rerun()
parents = st.session_state.get(f"{P}_parents", [])
if parents:
    parents_html = scroll_div("".join(
        f'<div class="card-hover" style="border:1px solid {COLORS["border"]};border-radius:8px;padding:10px;margin:4px 0;'
        f'border-left:3px solid {ACCENT};">'
        f'<b>Parent {i}</b> <span style="color:{COLORS["text_muted"]};">({chunker.count_tokens(p)} tokens)</span><br>'
        f'<code style="color:{COLORS["text_secondary"]};">{p[:200]}{"..." if len(p) > 200 else ""}</code></div>'
        for i, p in enumerate(parents)
    ))
    st.markdown(parents_html, unsafe_allow_html=True)

if parents_done:
    st.markdown(completion_arrow_html(), unsafe_allow_html=True)
st.markdown("---")

# ── STEP 4: Create Children ────────────────────────────────────────
st.markdown(step_header_html(4, "Create Child Chunks",
                              "completed" if children_done else "active" if parents_done else "upcoming",
                              ACCENT, "file-text"), unsafe_allow_html=True)

if mode == "Developer":
    if parents_done and not children_done:
        if st.button("Create Children", type="primary", use_container_width=True, key="hier_carve"):
            carve_children()
            st.rerun()

children_map = st.session_state.get(f"{P}_children_map", {})
if children_map:
    tree_html = scroll_div("".join(
        f'<div style="border:1px solid {COLORS["border"]};border-radius:8px;padding:10px;margin:4px 0;'
        f'border-left:3px solid {STRATEGY_COLORS["late"]};">'
        f'<div style="font-weight:600;color:{ACCENT};margin-bottom:6px;">📂 {pid} → {len(children)} children</div>'
        + "".join(
            f'<div style="padding:2px 0 2px 16px;{TYP["small"]};">'
            f'📄 Child {c.chunk_index} '
            f'<span style="color:{COLORS["text_muted"]};">({c.token_count} tok)</span> '
            f'<code style="color:{COLORS["text_secondary"]};">{c.chunk_text[:80]}...</code></div>'
            for c in children
        )
        + "</div>"
        for pid, children in children_map.items()
    ))
    st.markdown(tree_html, unsafe_allow_html=True)

if children_done:
    st.markdown(completion_arrow_html(), unsafe_allow_html=True)
st.markdown("---")

# ── STEP 5: Final Output ───────────────────────────────────────────
st.markdown(step_header_html(5, "Final Output",
                              "completed" if results_done else "upcoming", ACCENT, "package"), unsafe_allow_html=True)

results = st.session_state.get(f"{P}_results")
if results:
    min_tok = st.session_state.get("min_chunk_tokens", 0)
    if min_tok > 0:
        i = 0
        while i < len(results) - 1:
            if results[i].token_count < min_tok:
                results[i].chunk_text += " " + results[i + 1].chunk_text
                results[i].token_count += results[i + 1].token_count
                del results[i + 1]
            else:
                i += 1

    # ── Summary metrics ──
    parents = sum(1 for r in results if r.parent_chunk_id is None)
    children = sum(1 for r in results if r.parent_chunk_id is not None)
    avg_tokens = sum(r.token_count for r in results) // len(results) if results else 0
    st.markdown(metric_summary_html([
        (str(len(results)), "Total Chunks", "Total number of chunks"),
        (str(parents), "Parents", "Top-level parent chunks"),
        (str(children), "Children", "Child chunks carved from parents"),
        (str(avg_tokens), "Avg Tokens", "Average tokens per chunk"),
    ], STRATEGY), unsafe_allow_html=True)

    show_all = st.session_state.get(f"{P}_show_all", False)
    parents_in_results = [r for r in results if r.parent_chunk_id is None]
    children_map = st.session_state.get(f"{P}_children_map", {})
    tree_cards = []
    for p in parents_in_results:
        tree_cards.append(chunk_card_html(
            idx=p.chunk_index,
            chunk_text=p.chunk_text,
            token_count=p.token_count,
            strategy="hierarchical",
            extra_fields={
                "chunk_index": p.chunk_index,
                "token_count": p.token_count,
                "chunk_strategy": "hierarchical",
                "page_number": 0,
                "source_uri": None,
                "parent_chunk_id": None,
            },
            badge="Parent",
        ))
        pid = f"parent_{p.chunk_index}"
        kids = children_map.get(pid, [])
        visible_kids = kids if show_all else kids[:15]
        for ki, kid in enumerate(visible_kids):
            is_last = ki == len(visible_kids) - 1
            tree_cards.append(chunk_card_html(
                idx=kid.chunk_index,
                chunk_text=kid.chunk_text,
                token_count=kid.token_count,
                strategy="hierarchical",
                extra_fields={
                    "chunk_index": kid.chunk_index,
                    "token_count": kid.token_count,
                    "chunk_strategy": "hierarchical",
                    "page_number": 0,
                    "source_uri": None,
                    "parent_chunk_id": kid.parent_chunk_id,
                },
                badge="Child",
                tree="end" if is_last else "mid",
            ))
    cards_html = scroll_div("".join(tree_cards))
    st.markdown(cards_html, unsafe_allow_html=True)
    if len(results) > 15:
        if st.button(f"Show all {len(results)} chunks" if not show_all else "Show fewer",
                      use_container_width=True, key="hier_toggle"):
            st.session_state[f"{P}_show_all"] = not show_all
            st.rerun()
else:
    st.info("Run Steps ③ and ④ first.")

st.markdown("---")
if st.button("Reset & Run Again", use_container_width=True, key="hier_reset"):
    for k in [f"{P}_parents", f"{P}_children_map", f"{P}_results"]:
        st.session_state.pop(k, None)
    st.rerun()
