from __future__ import annotations

from pathlib import Path
import gradio as gr

from core.runner import (
    load_settings,
    ensure_config,
    run_contract_review,
    run_legal_research,
    run_client_intake,
    run_compliance_alert,
    run_case_summary,
)

SETTINGS = load_settings()
ensure_config(SETTINGS)


def _paths_from_file_list(files):
    if not files:
        return []
    paths = []
    for f in files:
        if f is None:
            continue
        if hasattr(f, "name") and f.name:
            paths.append(Path(f.name))
        elif isinstance(f, str):
            paths.append(Path(f))
        elif hasattr(f, "path") and f.path:
            paths.append(Path(f.path))
    return paths


def _to_path(upload):
    if not upload:
        return None
    if hasattr(upload, "name") and upload.name:
        return Path(upload.name)
    if isinstance(upload, str):
        return Path(upload)
    if hasattr(upload, "path") and upload.path:
        return Path(upload.path)
    return None


def contract_review_ui(contract_file, client_name, agreement_type, client_role, concerns, governing_law):
    try:
        res = run_contract_review(
            contract_file=_to_path(contract_file),
            client_name=client_name,
            agreement_type=agreement_type,
            client_role=client_role,
            concerns=concerns,
            governing_law=governing_law,
            settings=SETTINGS,
        )
        return res["text"], res["markdown_path"], res["json_path"]
    except Exception as exc:
        return f"Error: {exc}", None, None


def legal_research_ui(question, facts, jurisdiction, purpose, urgency, attachment_files):
    try:
        paths = _paths_from_file_list(attachment_files)
        res = run_legal_research(
            question=question,
            facts=facts,
            jurisdiction=jurisdiction,
            purpose=purpose,
            urgency=urgency,
            uploaded_files=paths,
            settings=SETTINGS,
        )
        return res["text"], res["markdown_path"], res["json_path"]
    except Exception as exc:
        return f"Error: {exc}", None, None


def client_intake_ui(enquiry_text, practice_area, attachment_files):
    try:
        paths = _paths_from_file_list(attachment_files)
        res = run_client_intake(
            enquiry_text=enquiry_text,
            practice_area=practice_area,
            uploaded_files=paths,
            settings=SETTINGS,
        )
        return res["text"], res["markdown_path"], res["json_path"]
    except Exception as exc:
        return f"Error: {exc}", None, None


def compliance_alert_ui(source_name, update_text, practice_areas, urgency, attachment_files):
    try:
        paths = _paths_from_file_list(attachment_files)
        res = run_compliance_alert(
            source_name=source_name,
            update_text=update_text,
            practice_areas=practice_areas,
            urgency=urgency,
            uploaded_files=paths,
            settings=SETTINGS,
        )
        return res["text"], res["markdown_path"], res["json_path"]
    except Exception as exc:
        return f"Error: {exc}", None, None


def case_summary_ui(judgment_file, focus_area):
    try:
        res = run_case_summary(
            judgment_file=_to_path(judgment_file),
            focus_area=focus_area,
            settings=SETTINGS,
        )
        return res["text"], res["markdown_path"], res["json_path"]
    except Exception as exc:
        return f"Error: {exc}", None, None


CSS = r"""
.gradio-container {
    background: radial-gradient(circle at top, #f7f8fc 0%, #f2f4f9 45%, #eef1f7 100%);
}
#hero {
    padding: 1.25rem 1.25rem 0.5rem 1.25rem;
    border-radius: 24px;
    background: linear-gradient(135deg, rgba(20, 33, 61, 0.98), rgba(44, 62, 80, 0.94));
    color: white;
    box-shadow: 0 20px 50px rgba(0,0,0,0.12);
}
#hero h1 {
    margin: 0;
    font-size: 2rem;
    line-height: 1.1;
    color: white !important;
}
#hero p {
    margin: 0.4rem 0 0 0;
    opacity: 0.9;
    color: white !important;
}
.agent-card {
    border-radius: 22px;
    padding: 1rem;
    background: white;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
    border: 1px solid rgba(148, 163, 184, 0.18);
}
.small-note {
    font-size: 0.92rem;
    color: #475569;
}

/* Clean, readable tables in result panels */
.result-output {
    overflow-x: hidden;
}

.result-output table {
    width: 100%;
    table-layout: fixed;
    border-collapse: collapse;
    font-size: 0.95rem;
}

.result-output th,
.result-output td {
    border: 1px solid #d1d5db;
    padding: 0.7rem 0.8rem;
    vertical-align: top;
    white-space: normal;
    overflow-wrap: anywhere;
    word-break: normal;
    line-height: 1.5;
}

.result-output th {
    background: #f8fafc;
    font-weight: 700;
    text-align: left;
}

.result-output tr:nth-child(even) td {
    background: #fcfcfd;
}
"""


def build_app():
    title = SETTINGS["app_title"]

    with gr.Blocks(title=title) as demo:
        gr.HTML(
            f"""
            <div id="hero">
                <h1>{title}</h1>
                <p>Five production-style legal agents built with Python, smolagents, and Groq, ready to run locally.</p>
            </div>
            """
        )

        with gr.Row():
            with gr.Column(scale=1, min_width=280):
                gr.Markdown(
                    """
                    <div class="agent-card">
                    <h3>Workspace</h3>
                    <p class="small-note">Set your Groq key in <code>.env</code>. Keep statutes, playbooks, case notes, and sample judgments in <code>knowledge/</code>.</p>
                    <p class="small-note">Each run saves a Markdown file and a JSON file into <code>outputs/</code>.</p>
                    </div>
                    """
                )
            with gr.Column(scale=2):
                gr.Markdown(
                    """
                    <div class="agent-card">
                    <h3>Design principle</h3>
                    <p class="small-note">Each agent is isolated, testable, and tuned to the exact output structure from the module.</p>
                    </div>
                    """
                )

        with gr.Tabs():
            with gr.Tab("Contract Review"):
                with gr.Row():
                    with gr.Column():
                        contract_file = gr.File(label="Upload contract", file_types=[".pdf", ".docx", ".txt", ".md"], type="filepath")
                        client_name = gr.Textbox(label="Client name", placeholder="e.g. ABC Pvt Ltd")
                        agreement_type = gr.Textbox(label="Agreement type", placeholder="e.g. Master Services Agreement")
                        client_role = gr.Textbox(label="Client role", placeholder="e.g. Service provider / buyer / licensor")
                        governing_law = gr.Textbox(label="Governing law", value="Indian law")
                        concerns = gr.Textbox(label="Specific concerns", lines=4, placeholder="e.g. liability cap, termination, IP ownership")
                        run_btn = gr.Button("Run Contract Review", variant="primary")
                    with gr.Column():
                        contract_output = gr.Markdown(label="Result", elem_classes=["result-output"])
                        contract_md = gr.File(label="Download Markdown")
                        contract_json = gr.File(label="Download JSON")
                run_btn.click(
                    contract_review_ui,
                    inputs=[contract_file, client_name, agreement_type, client_role, concerns, governing_law],
                    outputs=[contract_output, contract_md, contract_json],
                )

            with gr.Tab("Legal Research"):
                with gr.Row():
                    with gr.Column():
                        question = gr.Textbox(label="Research question", lines=3, placeholder="State the precise legal issue")
                        facts = gr.Textbox(label="Facts", lines=6, placeholder="Give the relevant facts and assumptions")
                        jurisdiction = gr.Textbox(label="Jurisdiction", placeholder="e.g. India / Delhi High Court / Supreme Court")
                        purpose = gr.Dropdown(
                            ["opinion", "advice", "litigation support", "academic"],
                            label="Purpose",
                            value="advice",
                        )
                        urgency = gr.Dropdown(["None", "Medium", "High", "Critical"], label="Urgency", value="Medium")
                        research_files = gr.File(label="Upload authorities / notes", file_types=[".pdf", ".docx", ".txt", ".md"], file_count="multiple", type="filepath")
                        run_btn2 = gr.Button("Run Legal Research", variant="primary")
                    with gr.Column():
                        research_output = gr.Markdown(label="Result", elem_classes=["result-output"])
                        research_md = gr.File(label="Download Markdown")
                        research_json = gr.File(label="Download JSON")
                run_btn2.click(
                    legal_research_ui,
                    inputs=[question, facts, jurisdiction, purpose, urgency, research_files],
                    outputs=[research_output, research_md, research_json],
                )

            with gr.Tab("Client Intake"):
                with gr.Row():
                    with gr.Column():
                        enquiry_text = gr.Textbox(label="Enquiry", lines=8, placeholder="Paste the form submission or message here")
                        practice_area = gr.Textbox(label="Practice area", placeholder="e.g. contracts, labour, regulatory, disputes")
                        intake_files = gr.File(label="Attachments", file_types=[".pdf", ".docx", ".txt", ".md"], file_count="multiple", type="filepath")
                        run_btn3 = gr.Button("Run Intake Triage", variant="primary")
                    with gr.Column():
                        intake_output = gr.Markdown(label="Result", elem_classes=["result-output"])
                        intake_md = gr.File(label="Download Markdown")
                        intake_json = gr.File(label="Download JSON")
                run_btn3.click(
                    client_intake_ui,
                    inputs=[enquiry_text, practice_area, intake_files],
                    outputs=[intake_output, intake_md, intake_json],
                )

            with gr.Tab("Compliance Alert"):
                with gr.Row():
                    with gr.Column():
                        source_name = gr.Textbox(label="Source name", placeholder="e.g. SEBI / MCA / RBI / MeitY")
                        urgency = gr.Dropdown(["None", "Medium", "High", "Critical"], label="Urgency", value="Medium")
                        practice_areas = gr.Textbox(label="Affected practice areas", placeholder="e.g. privacy, securities, banking, companies")
                        update_text = gr.Textbox(label="Update text", lines=8, placeholder="Paste the regulatory update or notification here")
                        compliance_files = gr.File(label="Attachments", file_types=[".pdf", ".docx", ".txt", ".md"], file_count="multiple", type="filepath")
                        run_btn4 = gr.Button("Run Compliance Alert", variant="primary")
                    with gr.Column():
                        compliance_output = gr.Markdown(label="Result", elem_classes=["result-output"])
                        compliance_md = gr.File(label="Download Markdown")
                        compliance_json = gr.File(label="Download JSON")
                run_btn4.click(
                    compliance_alert_ui,
                    inputs=[source_name, update_text, practice_areas, urgency, compliance_files],
                    outputs=[compliance_output, compliance_md, compliance_json],
                )

            with gr.Tab("Case Summary"):
                with gr.Row():
                    with gr.Column():
                        judgment_file = gr.File(label="Upload judgment", file_types=[".pdf", ".docx", ".txt", ".md"], type="filepath")
                        focus_area = gr.Textbox(label="Area of law", placeholder="e.g. Arbitration / Contract law / Competition law")
                        run_btn5 = gr.Button("Run Case Summary", variant="primary")
                    with gr.Column():
                        summary_output = gr.Markdown(label="Result", elem_classes=["result-output"])
                        summary_md = gr.File(label="Download Markdown")
                        summary_json = gr.File(label="Download JSON")
                run_btn5.click(
                    case_summary_ui,
                    inputs=[judgment_file, focus_area],
                    outputs=[summary_output, summary_md, summary_json],
                )

        gr.Markdown(
            """
            <div class="small-note">
            Tip: Place your internal playbooks, statutes, precedent notes, and sample judgments in the knowledge folder to enrich outputs.
            </div>
            """
        )

    return demo


if __name__ == "__main__":
    app = build_app()
    app.launch(css=CSS, theme=gr.themes.Soft(), share=False)