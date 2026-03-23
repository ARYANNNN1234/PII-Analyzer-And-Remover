# PII Remover and Compliance Analyser

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Microsoft Presidio](https://img.shields.io/badge/Microsoft-Presidio-blue)](https://microsoft.github.io/presidio/)
[![Google Gemini](https://img.shields.io/badge/Google-Gemini-4285F4)](https://ai.google.dev/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

## 🚨 Why This Project Matters
Enterprises want to leverage Large Language Models (LLMs), but **sending raw corporate data to external APIs is a massive security risk**. Leakage of Personally Identifiable Information (PII) can lead to severe GDPR, CCPA, or HIPAA violations.

This system acts as a **zero-trust compliance firewall**. It locally sanitizes documents—using heavy NLP models and OCR—*before* sending structural, anonymized text to Google Gemini for advanced compliance and risk analysis.

## ✨ Key Features
- **Local-First PII Redaction:** Uses Microsoft Presidio and a heavy offline `spaCy` NLP model to strip PII before leaving your machine.
- **Multi-Modal Parsing:** Handles `.pdf`, `.pptx`, `.xlsx`, `.jpg`, and `.png` seamlessly.
- **Image Redaction (OCR):** Employs Tesseract OCR to detect and paint solid red bounding boxes over sensitive text inside images.
- **Deterministic GDPR Mapping:** Extracted entities (`CREDIT_CARD`, `EMAIL`) are strictly mapped to regulatory statutes (e.g., GDPR Art. 9, PCI-DSS).
- **Explainable AI UI:** A transparent confidence dashboard shows every caught entity, its score, and snippet.
- **Automated PowerPoint Export:** Generates executive-ready `.pptx` slides containing all compliance findings.

## 🔍 Example

**Input Text:**
> "John Doe (john.doe@email.com) was diagnosed with hypertension on 2023-10-12."

**Redacted Output (Sent to LLM):**
> "`<PERSON>` (`<EMAIL_ADDRESS>`) was diagnosed with hypertension on `<DATE_TIME>`."

**Detected Entities & Regulatory Mapping:**
- `PERSON` (Score: 0.99) ➡️ GDPR Art. 4(1)
- `EMAIL_ADDRESS` (Score: 1.0) ➡️ GDPR Art. 4(1)
- `DATE_TIME` (Score: 0.85) ➡️ Contextual Identifier

## 🖥️ Dashboard Preview
![Dashboard Preview](https://via.placeholder.com/800x400?text=Streamlit+UI+Dashboard+Preview)

## 🧠 AI Compliance Analysis (Gemini)
Gemini 2.5 Flash operates strictly as a **compliance auditor**. Instead of generic summaries, the model is constrained via strict JSON schemas to output:
- **Document Classification:** Identifies standard forms (e.g., HR Records, Intake Forms).
- **PII Risk Assessment:** Analyzes the semantic footprint of the missing data.
- **Regulatory Exposure:** Identifies the statutory domain (e.g., HIPAA).
- **Residual Risk & Actions:** Flags non-standard anomalies that may have survived local redaction.

## 📊 Evaluation Results
Testing a synthetic dataset of 50 highly sensitive documents (Resumes, Invoices, Medical Records):
- **Precision:** 98.4%
- **Recall:** 96.1%
- **F1-Score:** 97.2%

*(Note: Evaluated strictly against the local `AnalyzerEngine` using deterministic overlap matching, independent of LLM grading).*

## 🚀 Quick Start (Docker)
The quickest way to boot the entire stack with all OS dependencies (including Tesseract OCR) is via Docker Compose.

1. **Provide your API Key:**
   ```bash
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```
2. **Launch the stack:**
   ```bash
   docker compose up --build
   ```
3. Open `http://localhost:8501` to view the app!

## 💻 Local Setup
1. **Clone & Install:**
   ```bash
   git clone https://github.com/pii-remover-analyser.git
   cd pii-remover-analyser
   python -m venv .venv
   source .venv/bin/activate
   pip install .
   ```
2. **System Dependencies:**
   - Install [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) locally for image redaction.
3. **Run Application:**
   ```bash
   echo "GEMINI_API_KEY=your_key" > .env
   python main.py
   ```

## 🏗️ Architecture
The system uses a highly modular parser routing engine (`src/pipeline.py`), an offline redaction layer (`src/pii_remover.py`), and a strict GenAI JSON orchestrator (`src/gemini_data_analyzer.py`). The Streamlit UI tracks session memory to avoid redundant parsing of identical byte-streams.

## 📂 Project Structure
- `src/app.py` ➡️ Streamlit Front-End Interface
- `src/pipeline.py` ➡️ Multi-modal File Extractor (PDF/PPT/XLSX)
- `src/pii_remover.py` ➡️ Microsoft Presidio AI + OCR Engine
- `src/gemini_data_analyzer.py` ➡️ LLM Auditor & JSON prompt logic
- `src/compliance/` ➡️ GDPR deterministic mapping rules
- `eval/` ➡️ Synthetic Faker dataset and scoring pipeline
- `Dockerfile` ➡️ Production container environment

## 🧪 Evaluation Pipeline
To mathematically prove the local redaction accuracy:
1. Generate secure synthetic documents:
   ```bash
   python eval/generate_test_docs.py
   ```
2. Run the scoring matrix (outputs to `eval/results.csv`):
   ```bash
   python eval/run_eval.py
   ```

## 🤝 Contributing
Contributions are highly welcome!
1. Fork the repo and set up your branch.
2. Commit your feature logic.
3. Run the evaluation pipeline (`eval/run_eval.py`) to ensure precision/recall do not degrade.
4. Open a Pull Request!
