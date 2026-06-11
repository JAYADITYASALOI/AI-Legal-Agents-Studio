# AI Legal Agent Studio (Groq) — Test Guide

Use these files to test the five tabs in the app.

Accepted upload types in the current UI:
- .pdf
- .docx
- .txt
- .md

Recommended quick test inputs:
- Contract Review: upload `01_contract_review_sample.txt`
- Legal Research: upload `02_legal_research_sample.txt` and paste the question/facts into the form
- Client Intake: paste `03_client_intake_sample.txt`
- Compliance Alert: upload `04_compliance_alert_sample.txt`
- Case Summary: upload `05_case_summary_sample.txt`

Notes:
- Legal Research, Client Intake, and Compliance Alert allow multiple attachments.
- Contract Review and Case Summary take a single uploaded file.
- The app creates Markdown and JSON outputs in `outputs/`.
