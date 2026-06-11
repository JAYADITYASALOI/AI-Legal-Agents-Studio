from __future__ import annotations

from datetime import datetime
from pathlib import Path
import json
import os
import re
from typing import Any, Sequence

from dotenv import load_dotenv
from smolagents import LiteLLMModel, ToolCallingAgent

from .file_io import extract_text_from_file, load_documents
from .prompts import (
    CONTRACT_REVIEW_SYSTEM,
    LEGAL_RESEARCH_SYSTEM,
    CLIENT_INTAKE_SYSTEM,
    COMPLIANCE_ALERT_SYSTEM,
    CASE_SUMMARY_SYSTEM,
)
from .retrieval import gather_knowledge_base


def load_settings() -> dict[str, Any]:
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY", "").strip() or os.getenv("OPENAI_API_KEY", "").strip()
    return {
        "api_key": api_key,
        "model_id": os.getenv("GROQ_MODEL", "groq/llama-3.3-70b-versatile").strip(),
        "temperature": float(os.getenv("AGENT_TEMPERATURE", "0.2")),
        "knowledge_base_dir": os.getenv("KNOWLEDGE_BASE_DIR", "knowledge").strip(),
        "output_dir": os.getenv("OUTPUT_DIR", "outputs").strip(),
        "app_title": os.getenv("APP_TITLE", "AI Legal Agent Studio").strip(),
    }


def ensure_config(settings: dict[str, Any]) -> None:
    if not settings["api_key"]:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Put it in your environment or in a .env file before running the app."
        )


def _normalize_model_id(model_id: str) -> str:
    model_id = (model_id or "").strip()
    if not model_id:
        return "groq/llama-3.3-70b-versatile"
    if "/" not in model_id:
        return f"groq/{model_id}"
    return model_id


def _build_model(settings: dict[str, Any]) -> LiteLLMModel:
    return LiteLLMModel(
        model_id=_normalize_model_id(settings["model_id"]),
        api_base="https://api.groq.com/openai/v1",
        api_key=settings["api_key"],
        temperature=settings["temperature"],
        max_tokens=6000,
    )


def _normalize_output(result: Any) -> str:
    if result is None:
        return ""
    if isinstance(result, str):
        return result.strip()
    for attr in ("final_answer", "content", "message", "output"):
        if hasattr(result, attr):
            val = getattr(result, attr)
            if isinstance(val, str) and val.strip():
                return val.strip()
    return str(result).strip()


def _make_agent(settings: dict[str, Any]) -> ToolCallingAgent:
    model = _build_model(settings)
    return ToolCallingAgent(
        tools=[],
        model=model,
        max_steps=1,
        verbosity_level=0,
    )


def _run_task(system_prompt: str, task_prompt: str, settings: dict[str, Any]) -> str:
    agent = _make_agent(settings)
    full_prompt = f"""{system_prompt}

TASK:
{task_prompt}

IMPORTANT:
- Do not call any tools.
- Do not output Python code or JSON.
- Return the final answer directly in markdown.
- Follow the output format exactly.
- Use markdown tables where a table is required.
"""
    result = agent.run(full_prompt)
    return _normalize_output(result)


def _save_output(output_dir: str | Path, agent_key: str, title: str, text: str) -> tuple[Path, Path]:
    outdir = Path(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", title).strip("_").lower()[:60] or agent_key
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_path = outdir / f"{timestamp}_{agent_key}_{slug}.md"
    json_path = outdir / f"{timestamp}_{agent_key}_{slug}.json"
    md_path.write_text(text, encoding="utf-8")
    json_path.write_text(
        json.dumps({"agent": agent_key, "title": title, "output": text}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return md_path, json_path


def build_document_context(uploaded_files: Sequence[Path] | None) -> str:
    if not uploaded_files:
        return ""
    docs = load_documents([Path(p) for p in uploaded_files if p])
    if not docs:
        return ""
    blocks = []
    for doc in docs:
        blocks.append(f"[DOCUMENT] {doc.title}\n{doc.text}")
    return "\n\n".join(blocks)


def run_contract_review(
    *,
    contract_file: Path | None,
    client_name: str,
    agreement_type: str,
    client_role: str,
    concerns: str,
    governing_law: str,
    settings: dict[str, Any],
) -> dict[str, Any]:
    contract_text = extract_text_from_file(contract_file) if contract_file else ""
    kb = gather_knowledge_base(settings["knowledge_base_dir"], f"{agreement_type} {client_role} {concerns} contract review")
    prompt = f"""Client name: {client_name or 'Not provided'}
Agreement type: {agreement_type or 'Not provided'}
Client role: {client_role or 'Not provided'}
Governing law: {governing_law or 'Not provided'}
Specific concerns: {concerns or 'None provided'}

CONTRACT TEXT:
{contract_text or '[No file uploaded]'}

KNOWLEDGE BASE EXCERPTS:
{kb or '[No local knowledge base matches found]'}
"""
    output = _run_task(CONTRACT_REVIEW_SYSTEM, prompt, settings)
    md_path, json_path = _save_output(settings["output_dir"], "contract_review", client_name or "contract_review", output)
    return {"text": output, "markdown_path": str(md_path), "json_path": str(json_path)}


def run_legal_research(
    *,
    question: str,
    facts: str,
    jurisdiction: str,
    purpose: str,
    urgency: str,
    uploaded_files: Sequence[Path] | None,
    settings: dict[str, Any],
) -> dict[str, Any]:
    docs_context = build_document_context(uploaded_files)
    kb = gather_knowledge_base(settings["knowledge_base_dir"], f"{question} {facts} {jurisdiction}")
    prompt = f"""Research question: {question}
Facts:
{facts or 'Not provided'}
Jurisdiction:
{jurisdiction or 'Not provided'}
Purpose:
{purpose or 'Not provided'}
Urgency:
{urgency or 'Not provided'}

ATTACHMENT CONTEXT:
{docs_context or '[No uploaded research material]'}

KNOWLEDGE BASE EXCERPTS:
{kb or '[No local knowledge base matches found]'}
"""
    output = _run_task(LEGAL_RESEARCH_SYSTEM, prompt, settings)
    md_path, json_path = _save_output(settings["output_dir"], "legal_research", question[:48] or "research", output)
    return {"text": output, "markdown_path": str(md_path), "json_path": str(json_path)}


def run_client_intake(
    *,
    enquiry_text: str,
    practice_area: str,
    uploaded_files: Sequence[Path] | None,
    settings: dict[str, Any],
) -> dict[str, Any]:
    docs_context = build_document_context(uploaded_files)
    kb = gather_knowledge_base(settings["knowledge_base_dir"], f"{enquiry_text} {practice_area}")
    prompt = f"""Practice area:
{practice_area or 'Not provided'}

Enquiry:
{enquiry_text or '[No text provided]'}

ATTACHMENT CONTEXT:
{docs_context or '[No attachments]'}

KNOWLEDGE BASE EXCERPTS:
{kb or '[No local knowledge base matches found]'}
"""
    output = _run_task(CLIENT_INTAKE_SYSTEM, prompt, settings)
    md_path, json_path = _save_output(settings["output_dir"], "client_intake", practice_area or "intake", output)
    return {"text": output, "markdown_path": str(md_path), "json_path": str(json_path)}


def run_compliance_alert(
    *,
    source_name: str,
    update_text: str,
    practice_areas: str,
    urgency: str,
    uploaded_files: Sequence[Path] | None,
    settings: dict[str, Any],
) -> dict[str, Any]:
    docs_context = build_document_context(uploaded_files)
    kb = gather_knowledge_base(settings["knowledge_base_dir"], f"{source_name} {update_text} {practice_areas}")
    prompt = f"""Source name:
{source_name or 'Not provided'}

Urgency:
{urgency or 'Not provided'}

Practice areas:
{practice_areas or 'Not provided'}

Update text:
{update_text or '[No update text provided]'}

ATTACHMENT CONTEXT:
{docs_context or '[No attachments]'}

KNOWLEDGE BASE EXCERPTS:
{kb or '[No local knowledge base matches found]'}
"""
    output = _run_task(COMPLIANCE_ALERT_SYSTEM, prompt, settings)
    md_path, json_path = _save_output(settings["output_dir"], "compliance_alert", source_name or "compliance_alert", output)
    return {"text": output, "markdown_path": str(md_path), "json_path": str(json_path)}


def run_case_summary(
    *,
    judgment_file: Path | None,
    focus_area: str,
    settings: dict[str, Any],
) -> dict[str, Any]:
    judgment_text = extract_text_from_file(judgment_file) if judgment_file else ""
    kb = gather_knowledge_base(settings["knowledge_base_dir"], f"{focus_area} judgment summary")
    prompt = f"""Focus area:
{focus_area or 'Not provided'}

JUDGMENT TEXT:
{judgment_text or '[No judgment file uploaded]'}

KNOWLEDGE BASE EXCERPTS:
{kb or '[No local knowledge base matches found]'}
"""
    output = _run_task(CASE_SUMMARY_SYSTEM, prompt, settings)
    md_path, json_path = _save_output(settings["output_dir"], "case_summary", focus_area or "case_summary", output)
    return {"text": output, "markdown_path": str(md_path), "json_path": str(json_path)}
