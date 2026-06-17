import streamlit as st
from theme import (COLORS, STRATEGY_COLORS, GLOBAL_CSS,
                   page_header_html, chunk_card_html, scroll_div,
                   progress_bar_css, icon)
from chunkers import SemanticChunker, HierarchicalChunker, LateChunker
from utils import make_page, init_embedder, merge_small_chunks

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

if not st.session_state.get("process_text", "").strip():
    st.warning("📄 Please load a document on the main page first.")
    st.page_link("app.py", label="← Go to Main Page", use_container_width=True)
    st.stop()

COMPARE_ACCENT = STRATEGY_COLORS["compare"]
st.markdown(progress_bar_css(COMPARE_ACCENT), unsafe_allow_html=True)

st.markdown(
    page_header_html(
        "Strategy Comparison",
        "Run multiple chunking strategies side-by-side on the same document",
        icon_name="split",
        accent=COMPARE_ACCENT,
    ),
    unsafe_allow_html=True,
)

text = st.session_state.get("process_text", "")
page = make_page(text)

embedder = st.session_state.get("embedder")
if embedder is None:
    embedder = init_embedder("local")
    st.session_state.embedder = embedder

min_tok = st.session_state.get("min_chunk_tokens", 0)

all_strategies = {
    "semantic": {"label": "Semantic", "color": STRATEGY_COLORS["semantic"], "icon": "layers"},
    "hierarchical": {"label": "Hierarchical", "color": STRATEGY_COLORS["hierarchical"], "icon": "git-branch"},
    "late": {"label": "Late", "color": STRATEGY_COLORS["late"], "icon": "brain"},
}

st.markdown("### Choose strategies to compare")
sel = {}
pars = {}
sc1, sc2, sc3 = st.columns(3)
cols_map = {"semantic": sc1, "hierarchical": sc2, "late": sc3}

for name, cfg in all_strategies.items():
    with cols_map[name]:
        sel[name] = st.checkbox(
            cfg['label'],
            value=True,
            key=f"comp_enable_{name}",
        )

st.markdown("---")

selected = [n for n in all_strategies if sel.get(n)]
if selected:
    st.markdown("### Configure Parameters")
    pcols = st.columns(len(selected))
    for ci, name in enumerate(selected):
        cfg = all_strategies[name]
        with pcols[ci]:
            st.markdown(
                f'<div style="background:{COLORS["surface"]};border-radius:8px;'
                f'border-top:3px solid {cfg["color"]};padding:12px;">'
                f'<span style="color:{cfg["color"]};font-size:0.9rem;font-weight:600;">'
                f'{icon(cfg["icon"], 16)} {cfg["label"]}</span>',
                unsafe_allow_html=True,
            )
            if name == "semantic":
                pars["s_cs"] = st.slider("Chunk size", 64, 1024, 256, 16, key="comp_sem_cs")
                pars["s_th"] = st.slider("Threshold", 0.1, 1.0, 0.5, 0.05, key="comp_sem_th")
            elif name == "hierarchical":
                pars["h_cs"] = st.slider("Parent size", 64, 2048, 1024, 16, key="comp_hier_cs")
                pars["h_cc"] = st.slider("Child size", 32, 512, 128, 16, key="comp_hier_cc")
                pars["h_co"] = st.slider("Child overlap", 0, 128, 32, 8, key="comp_hier_co")
            elif name == "late":
                pars["l_cs"] = st.slider("Chunk size", 64, 1024, 256, 16, key="comp_late_cs")
            st.markdown("</div>", unsafe_allow_html=True)

available_strategies = {}
if "semantic" in selected:
    available_strategies["semantic"] = {
        "chunker": SemanticChunker(embedder=embedder, chunk_size=pars.get("s_cs", 256), similarity_threshold=pars.get("s_th", 0.5)),
        "label": "Semantic",
        "color": STRATEGY_COLORS["semantic"],
    }
if "hierarchical" in selected:
    available_strategies["hierarchical"] = {
        "chunker": HierarchicalChunker(chunk_size=pars.get("h_cs", 1024), child_chunk_size=pars.get("h_cc", 128), child_overlap=pars.get("h_co", 32)),
        "label": "Hierarchical",
        "color": STRATEGY_COLORS["hierarchical"],
    }
if "late" in selected:
    available_strategies["late"] = {
        "chunker": LateChunker(embedder=embedder, chunk_size=pars.get("l_cs", 256)),
        "label": "Late",
        "color": STRATEGY_COLORS["late"],
    }

if selected and st.button("Run Comparison", type="primary", use_container_width=True, key="comp_run"):
    results = {}
    with st.status("Running strategies…", expanded=True) as status:
        for name in selected:
            cfg = available_strategies[name]
            st.write(f"**{cfg['label']}**…")
            chunks = cfg["chunker"].chunk([page])
            results[name] = list(chunks)
        status.update(label="✅ Comparison complete!", state="complete")
    st.session_state["comp_results"] = results

if "comp_results" in st.session_state:
    results = st.session_state["comp_results"]
    active = [n for n in selected if n in results]
    if active:
        cols = st.columns(len(active))
        for col_idx, name in enumerate(active):
            with cols[col_idx]:
                cfg = available_strategies[name]
                chunks = list(results[name])

                if min_tok > 0:
                    if name in ("semantic", "late"):
                        if name == "late":
                            chunks = merge_small_chunks(
                                [{"chunk_text": r.chunk_text, "token_count": r.token_count,
                                  "chunk_embedding": getattr(r, "chunk_embedding", None),
                                  "full_page_embedding": getattr(r, "full_page_embedding", None)}
                                 for r in chunks], min_tok) if chunks else []
                        else:
                            chunks = list(merge_small_chunks(
                                [{"chunk_text": r.chunk_text, "token_count": r.token_count,
                                  "reason": getattr(r, "reason", None)}
                                 for r in chunks], min_tok)) if chunks else []
                    elif name == "hierarchical":
                        i = 0
                        while i < len(chunks) - 1:
                            if chunks[i].token_count < min_tok:
                                chunks[i].chunk_text += " " + chunks[i + 1].chunk_text
                                chunks[i].token_count += chunks[i + 1].token_count
                                del chunks[i + 1]
                            else:
                                i += 1

                tc = sum(c.token_count if hasattr(c, "token_count") else c.get("token_count", 0) for c in chunks)
                num = len(chunks)
                avg_tc = tc // num if num else 0

                st.markdown(
                    f"<h3 style='color:{cfg['color']};text-align:center;'>{cfg['label']}</h3>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div style="text-align:center;color:{cfg["color"]};font-size:0.85rem;'
                    f'margin:4px 0 8px;">'
                    f'<b>{num}</b> Chunks · <b>{tc}</b> Tokens · <b>{avg_tc}</b> Avg/Chunk'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                st.markdown("---")

                show_all_key = f"comp_show_all_{name}"
                show_all = st.session_state.get(show_all_key, False)
                display = chunks if show_all else chunks[:10]

                cards = []

                if name == "hierarchical":
                    # Build parent/child tree
                    parents_in = [c for c in display if c.parent_chunk_id is None]
                    children_map = {}
                    for c in display:
                        if c.parent_chunk_id is not None:
                            children_map.setdefault(c.parent_chunk_id, []).append(c)

                    for p in parents_in:
                        cards.append(chunk_card_html(
                            idx=p.chunk_index, chunk_text=p.chunk_text,
                            token_count=p.token_count, strategy="hierarchical",
                            extra_fields={
                                "chunk_index": p.chunk_index,
                                "token_count": p.token_count,
                                "chunk_strategy": "hierarchical",
                                "page_number": 0, "source_uri": None,
                                "parent_chunk_id": None,
                            },
                            badge="Parent",
                        ))
                        pid = f"parent_{p.chunk_index}"
                        kids = children_map.get(pid, [])
                        for ki, kid in enumerate(kids):
                            is_last = ki == len(kids) - 1
                            cards.append(chunk_card_html(
                                idx=kid.chunk_index, chunk_text=kid.chunk_text,
                                token_count=kid.token_count, strategy="hierarchical",
                                extra_fields={
                                    "chunk_index": kid.chunk_index,
                                    "token_count": kid.token_count,
                                    "chunk_strategy": "hierarchical",
                                    "page_number": 0, "source_uri": None,
                                    "parent_chunk_id": kid.parent_chunk_id,
                                },
                                badge="Child",
                                tree="end" if is_last else "mid",
                            ))
                else:
                    for idx, c in enumerate(display):
                        if hasattr(c, "chunk_text"):
                            extra = {"chunk_index": idx, "token_count": c.token_count, "chunk_strategy": name,
                                     "page_number": 0, "source_uri": None}
                            extra["reason"] = getattr(c, "reason", None)
                            cards.append(chunk_card_html(
                                idx=idx, chunk_text=c.chunk_text, token_count=c.token_count,
                                strategy=name, extra_fields=extra,
                            ))
                        else:
                            extra = {"chunk_index": idx, "token_count": c["token_count"], "chunk_strategy": name,
                                     "page_number": 0, "source_uri": None}
                            extra["chunk_embedding"] = c.get("chunk_embedding", "N/A")
                            extra["full_page_embedding"] = c.get("full_page_embedding", "N/A")
                            extra["reason"] = c.get("reason", None)
                            cards.append(chunk_card_html(
                                idx=idx, chunk_text=c["chunk_text"], token_count=c["token_count"],
                                strategy=name, extra_fields=extra,
                            ))
                st.markdown(scroll_div("".join(cards)), unsafe_allow_html=True)
                if len(chunks) > 10:
                    if st.button(f"Show {len(chunks)}" if not show_all else "Show fewer",
                                  key=show_all_key + "_btn", use_container_width=True):
                        st.session_state[show_all_key] = not show_all
                        st.rerun()
