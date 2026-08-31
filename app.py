import gradio as gr
from orchestrator import get_clarifying_questions, build_enriched_query, main
from writer_agent import ReportData


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

textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-size: 1rem !important;
    padding: 14px !important;
}

textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(124, 158, 255, 0.15) !important;
}

#ask-btn, #research-btn {
    background: var(--accent) !important;
    border: none !important;
    border-radius: 10px !important;
    color: #0f1117 !important;
    font-weight: 600 !important;
    padding: 12px 20px !important;
}

#ask-btn:hover, #research-btn:hover {
    opacity: 0.9;
}

.card {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 20px !important;
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

# ---------- Phase 1: clarifying questions ----------
async def ask_questions(query: str):
    """Returns: questions_display, answers_input, stored_query, stored_questions"""
    if not query.strip():
        return "Please enter a query first.", "", "", []

    questions = await get_clarifying_questions(query)

    if not questions:
        return "No clarification needed — click **Research**.", "", query, []

    numbered = "\n".join(f"{i}. {q}" for i, q in enumerate(questions, 1))
    return f"### A few questions first\n{numbered}", "", query, questions


async def run_with_answers(query: str, questions: list[str], answers: str):
    """Returns: report_output, summary_output, followups_output"""
    if not query.strip():
        return "Start with a query above.", "", ""

    report = await main(build_enriched_query(query, questions, answers))

    followups = "\n".join(f"- {q}" for q in report.follow_up_questions)
    return (
        report.markdown_report,
        f"### Summary\n{report.short_summary}",
        f"### Follow-up questions\n{followups}",
    )


# ---------- Layout ----------
with gr.Blocks(css=CUSTOM_CSS, theme=THEME, title="Deep Research") as demo:
    stored_query = gr.State("")
    stored_questions = gr.State([])

    with gr.Column(elem_id="header"):
        gr.Markdown("# Deep Research")
        gr.Markdown("Ask a question. Get a researched, sourced report.")

    with gr.Row():
        query_input = gr.Textbox(
            placeholder="e.g. Most popular AI agent frameworks in 2026",
            label="Your query",
            lines=2,
            scale=4,
        )
        ask_btn = gr.Button("Start", elem_id="ask-btn", scale=1)

    questions_display = gr.Markdown(elem_classes="card")

    with gr.Row():
        answers_input = gr.Textbox(
            label="Your answers",
            placeholder="Answer the questions above in your own words.",
            lines=4,
            scale=4,
        )
        research_btn = gr.Button("Research", elem_id="research-btn", scale=1)

    with gr.Row():
        with gr.Column(scale=2):
            report_output = gr.Markdown(elem_classes="card", elem_id="report-card")
        with gr.Column(scale=1):
            summary_output = gr.Markdown(elem_classes="card")
            followups_output = gr.Markdown(elem_classes="card")

    ask_btn.click(
        fn=ask_questions,
        inputs=query_input,
        outputs=[questions_display, answers_input, stored_query, stored_questions],
    )
    query_input.submit(
        fn=ask_questions,
        inputs=query_input,
        outputs=[questions_display, answers_input, stored_query, stored_questions],
    )

    research_btn.click(
        fn=run_with_answers,
        inputs=[stored_query, stored_questions, answers_input],
        outputs=[report_output, summary_output, followups_output],
    )


if __name__ == "__main__":
    demo.launch()