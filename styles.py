# ---------- Custom styling ----------
CUSTOM_CSS = """
:root {
    --bg: #0f1117;
    --surface: #171a23;
    --border: #262b3a;
    --text: #e7e9ee;
    --text-dim: #9aa0ac;
    --accent: #7c9eff;
}

.gradio-container {
    background: var(--bg) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

#header {
    text-align: center;
    padding: 2rem 0 1rem 0;
}

#header h1 {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 0.25rem;
}

#header p {
    color: var(--text-dim);
    font-size: 0.95rem;
}

#query-box textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-size: 1rem !important;
    padding: 14px !important;
}

#query-box textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(124, 158, 255, 0.15) !important;
}

#submit-btn {
    background: var(--accent) !important;
    border: none !important;
    border-radius: 10px !important;
    color: #0f1117 !important;
    font-weight: 600 !important;
    padding: 12px 20px !important;
}

#submit-btn:hover {
    opacity: 0.9;
}

.card {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 20px !important;
}

.card h3 {
    color: var(--accent) !important;
    font-size: 0.85rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 10px !important;
}

#report-card {
    max-height: 600px;
    overflow-y: auto;
}

footer {
    display: none !important;
}
"""

THEME = gr.themes.Base(
    primary_hue="indigo",
    neutral_hue="slate",
).set(
    body_background_fill="#0f1117",
    block_background_fill="#171a23",
    block_border_color="#262b3a",
    block_label_text_color="#9aa0ac",
    body_text_color="#e7e9ee",
)
