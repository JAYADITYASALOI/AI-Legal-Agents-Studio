---
title: AI Legal Agent Studio (Groq)
sdk: gradio
app_file: app.py
---

# AI Legal Agent Studio (Groq)

Five production-style legal AI agents built with Python, Gradio, smolagents, LiteLLM, and Groq.

Included agents:
- Contract Review Agent
- Legal Research Agent
- Client Intake Agent
- Compliance Alert Agent
- Case Summary Agent

## System Requirements

Minimum supported versions:

- Python 3.10+
- pip
- Windows, macOS, or Linux

Recommended versions:

- Python 3.12+
- Python 3.13+
- Python 3.14+

## Installation

1. Extract this repository.
2. Open a terminal in the project folder.
3. Create a virtual environment:

```bash
python -m venv .venv
```

4. Activate it:

### Command Prompt

```bash
.venv\Scripts\activate
```

### PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

5. Upgrade packaging tools:

```bash
python -m pip install --upgrade pip setuptools wheel
```

6. Install dependencies:

```bash
pip install -r requirements.txt
```

7. Create your environment file:

### Windows

```bash
copy .env.example .env
```

### macOS/Linux

```bash
cp .env.example .env
```

8. Add your Groq API key to `.env`:

```env
GROQ_API_KEY=your_api_key_here
```

9. Run the app:

```bash
python app.py
```

## Knowledge Base

The app uses the local `knowledge/` folder as its knowledge base. Put your playbooks, statutes, precedent notes, and guidance files there.

## Accepted Upload Types

- `.pdf`
- `.docx`
- `.txt`
- `.md`

## Output Files

Each run saves:
- a Markdown file
- a JSON file

into `outputs/`.

## Groq Model

The app is configured by default for:

```text
groq/llama-3.3-70b-versatile
```

Groq’s documentation lists `llama-3.3-70b-versatile` as a production model and shows Groq-compatible tool use and JSON mode support. smolagents’ `LiteLLMModel` supports provider-prefixed model IDs, and its docs show that `ToolCallingAgent` is the agent class for structured tool calls, while `CodeAgent` emits Python code snippets. citeturn636908view2turn679490view0turn636908view1turn551477search5

## Notes

- Keep confidential material out of public deployments.
- Verify legal citations before professional use.
- Review outputs before sharing them with clients or courts.
