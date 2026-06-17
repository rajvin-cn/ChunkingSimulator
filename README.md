---
title: Chunking Visualizer
emoji: 🧩
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
app_port: 8501
---

# Chunking Visualizer

Interactive visualizer for 3 text chunking strategies: Semantic, Hierarchical, and Late. Built with Streamlit.

## Features
- **Semantic** — topic-boundary detection via embedding centroid comparison
- **Hierarchical** — rule-based parent/child two-level chunking
- **Late** — full-page embedding first, then split with dual-context vectors
- **Compare** — run 2–3 strategies side by side
- **Local** (sentence-transformers) or **Remote** (EURI API) embedder

## Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy
Push to [Hugging Face Spaces](https://huggingface.co/spaces) with Docker — uses the included `Dockerfile`.

## License
MIT
