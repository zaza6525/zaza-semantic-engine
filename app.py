"""Gradio Web UI for Zaza Semantic Engine on Hugging Face Spaces.

Wraps the SemanticEngine to allow visitors to:
  - upload a document (PDF/DOCX/TXT/MD/HTML/CSV/JSON/EPUB/...)
  - run semantic search across what they've ingested
"""

import sys
from pathlib import Path

# Make `src/zaza` importable even if the package isn't pip-installed yet
sys.path.insert(0, str(Path(__file__).parent / "src"))

import gradio as gr  # noqa: E402
from zaza.engine import SemanticEngine  # noqa: E402

engine = SemanticEngine()


def ingest(file):
    if file is None:
        return "❌ Aucun fichier sélectionné."
    try:
        result = engine.ingest_file(file.name)
        chunks = ""
        if engine.embed_store:
            chunks = f" — indexé dans {engine.embed_store.count()} embedding(s)"
        return (
            f"✅ **{result['filename']}** ingéré — {result['word_count']} mots{chunks}.\n\n"
            f"Mots-clés principaux : {', '.join(w['word'] for w in result['top_words'])}"
        )
    except Exception as e:
        return f"❌ Erreur d'ingestion : `{e}`"


def search(query, top_k):
    if not query or not query.strip():
        return "_Entre une requête d'abord._"
    if not engine.embed_store:
        return "⚠️ Embeddings sémantiques désactivés sur ce Space."
    try:
        results = engine.search_semantic(query, n_results=int(top_k))
        if not results:
            return "_Aucun résultat — as-tu ingéré au moins un document ?_"

        lines = [f"### {len(results)} résultat(s) pour : *{query}*\n"]
        for i, r in enumerate(results, 1):
            meta = r.get("metadata") or {}
            distance = r.get("distance", 1.0)
            score = round(max(0.0, 1.0 - distance), 3)
            filename = meta.get("filename", "?")
            preview = (r.get("document") or "")[:280].replace("\n", " ")
            lines.append(f"**{i}. {filename}** — score {score}\n\n> {preview}…\n")
        return "\n".join(lines)
    except Exception as e:
        return f"❌ Erreur de recherche : `{e}`"


def status():
    try:
        n_docs = engine.embed_store.count() if engine.embed_store else 0
        model = engine.embed_store.model_name if engine.embed_store else "n/a"
        return f"**État du moteur**\n\n- Embeddings : {'✅ activés' if engine.embed_store else '❌ désactivés'}\n- Modèle : `{model}`\n- Documents indexés : {n_docs}"
    except Exception as e:
        return f"❌ {e}"


with gr.Blocks(title="Zaza Semantic Engine", theme=gr.themes.Soft()) as app:
    gr.Markdown(
        """
        # 🧠 Zaza Semantic Engine

        Indexation et **recherche sémantique multilingue** locale — 50+ langues,
        sans cloud, sans clé API.

        [💻 Code source GitHub](https://github.com/zaza6525/zaza-semantic-engine)
        """
    )

    with gr.Tab("📥 Ingérer"):
        file_in = gr.File(
            label="Document (PDF, DOCX, TXT, MD, HTML, XML, CSV, JSON, YAML, EPUB)",
            file_types=[".pdf", ".docx", ".txt", ".md", ".html", ".htm", ".xml", ".csv", ".json", ".yaml", ".yml", ".epub"],
        )
        ingest_btn = gr.Button("Ingérer", variant="primary")
        ingest_out = gr.Markdown()
        ingest_btn.click(ingest, inputs=file_in, outputs=ingest_out)

    with gr.Tab("🔍 Recherche sémantique"):
        query = gr.Textbox(
            label="Recherche",
            placeholder="Ex : « idées de vacances », « notes sur le projet X », « budget Q3 »",
        )
        top_k = gr.Slider(1, 20, value=5, step=1, label="Nombre de résultats")
        search_btn = gr.Button("Chercher", variant="primary")
        search_out = gr.Markdown()
        search_btn.click(search, inputs=[query, top_k], outputs=search_out)

    with gr.Tab("ℹ️ Statut"):
        status_btn = gr.Button("Rafraîchir")
        status_out = gr.Markdown(status())
        status_btn.click(status, outputs=status_out)


if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)
