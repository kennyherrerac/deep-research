from orchestrator import main
import gradio as gr
import asyncio
from writer_agent import ReportData
from styles import CUSTOM_CSS

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

# ---------- Pipeline call ----------
async def run_research_ui(query: str):
    if not query or not query.strip():
        return "Please enter a query.", "", ""

    report: ReportData = await main(query)

    summary_md = f"### Summary\n{report.short_summary}"

    if report.follow_up_questions:
        questions_md = "### Follow-up questions\n" + "\n".join(
            f"- {q}" for q in report.follow_up_questions
        )
    else:
        questions_md = "### Follow-up questions\n_None suggested._"

    return report.markdown_report, summary_md, questions_md


# ---------- Layout ----------
with gr.Blocks(css=CUSTOM_CSS, theme=THEME, title="Deep Research") as demo:
    with gr.Column(elem_id="header"):
        gr.Markdown("# Deep Research")
        gr.Markdown("Ask a question. Get a researched, sourced report.")

    with gr.Row():
        query_input = gr.Textbox(
            elem_id="query-box",
            placeholder="e.g. Most popular AI agent frameworks in 2026",
            label="",
            lines=2,
            scale=4,
        )
        submit_btn = gr.Button("Research", elem_id="submit-btn", scale=1)

    with gr.Row():
        with gr.Column(scale=2):
            report_output = gr.Markdown(elem_classes="card", elem_id="report-card")
        with gr.Column(scale=1):
            summary_output = gr.Markdown(elem_classes="card")
            questions_output = gr.Markdown(elem_classes="card")

    submit_btn.click(
        fn=run_research_ui,
        inputs=query_input,
        outputs=[report_output, summary_output, questions_output],
    )
    query_input.submit(
        fn=run_research_ui,
        inputs=query_input,
        outputs=[report_output, summary_output, questions_output],
    )


if __name__ == "__main__":
    demo.launch()
