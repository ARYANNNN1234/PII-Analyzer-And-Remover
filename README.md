# PII Remover and Analyser

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Microsoft Presidio](https://img.shields.io/badge/Microsoft-Presidio-blue)](https://microsoft.github.io/presidio/)
[![Google Gemini](https://img.shields.io/badge/Google-Gemini-4285F4)](https://ai.google.dev/)

A sophisticated **Streamlit-based security analysis tool** that automatically removes Personally Identifiable Information (PII) from various file formats and generates intelligent security insights using Google Gemini AI.

## Features

### Multi-Format Support
- **Images**: PNG, JPG, JPEG with visual PII redaction
- **Documents**: PDF text and image extraction with PII removal
- **Presentations**: PPTX content analysis including text, tables, and embedded images
- **Spreadsheets**: Excel files with DataFrame anonymization
- **Batch Processing**: Upload and process multiple files simultaneously

### Advanced PII Detection & Removal
- **Microsoft Presidio Integration**: Industry-standard PII detection and anonymization
- **Custom Recognition Patterns**: Extensible YAML-based pattern definitions
- **Multi-Modal Processing**: Text, image, and structured data PII removal
- **Entity Mapping**: Consistent PII detection across different content types

### AI-Powered Analysis
- **Google Gemini Integration**: Intelligent security insights and recommendations
- **Structured Reporting**: JSON-formatted analysis with key findings
- **Contextual Understanding**: AI analysis of anonymized content for security assessment

### Professional Reporting
- **PowerPoint Generation**: Automated presentation creation with findings
- **Interactive UI**: Real-time processing status and results visualization
- **Detailed Logging**: Comprehensive error handling and debugging information

## System Design

![Simple flow of file](./public/system_design.png "Flow")

## Quick Start

### Run locally via Docker in 2 commands (Recommended)

You can run the entire application—securely containerized with all system dependencies (like Tesseract OCR for image redaction)—using Docker Compose.

1. Ensure your `.env` file has your API key:
   ```bash
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```
2. Start the container:
   ```bash
   docker compose up --build
   ```
   Open `http://localhost:8501`.

---

### Local Installation (Without Docker)

#### Prerequisites
- Python 3.12 or higher
- Google Gemini API key
- **Tesseract OCR**: must be installed and in your system PATH for image redaction to work

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/pii-remover-analyser.git
   cd pii-remover-analyser
   ```

2. **Install dependencies** (using uv - recommended)
   ```bash
   uv sync
   ```
   
   Or using pip:
   ```bash
   python -m venv .venv
   source /.venv/bin/activate
   pip install .
   ```

3. **Set up environment variables (Optional)**
   ```bash
   # Edit .env and add your Gemini API key
   echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env
   ```

4. **Run the application**
   ```bash
   python main.py
   ```
   
   Or directly with Streamlit:
   ```bash
   streamlit run src/better_ui.py
   ```

## Usage

1. **Launch the Application**: Open your browser to the Streamlit interface (typically `http://localhost:8501`)

2. **Upload Files**: Use the file uploader to select one or more supported files
   - Supported formats: PNG, JPG, JPEG, PDF, XLSX, PPTX

3. **Automatic Processing**: The pipeline will:
   - Extract content from your files
   - Remove PII using Presidio
   - Analyze the anonymized content with Gemini AI
   - Generate security insights and recommendations

4. **View Results**: Review the analysis results and download generated reports

## Configuration

### Custom PII Patterns

Add custom recognition patterns in `src/patterns/` using YAML format:

```yaml
recognizers:
  - name: "Employee ID Recognizer"
    supported_entity: "EMPID"
    supported_language: "en"
    patterns:
      - name: "EMPID Pattern"
        regex: "^EMP....."
        score: 0.8
    context:
      - EMPID
```

### Environment Variables

| Variable         | Description                          | Required |
| ---------------- | ------------------------------------ | -------- |
| `GEMINI_API_KEY` | Google Gemini API authentication key | Yes      |

## Development

### Project Structure
```
pii-remover-analyser/
├── main.py                          # Application entry point
├── pyproject.toml                   # Dependencies and project configuration
├── requirements.txt                 # Requirements for installation without uv
├── uv.lock                          # Dependency lock file
├── src/
│   ├── streamlit_app.py             # Streamlit web interface
│   ├── better_ui.py                 # Improved interface with caching for better performance
│   ├── pipeline.py                  # Main processing pipeline
│   ├── pii_remover.py               # PII removal engine
│   ├── gemini_data_analyzer.py      # AI analysis integration
│   ├── helpers.py                   # Content extraction utilities
│   ├── generate_ppt.py              # Report generation
│   ├── models.py                    # Data models
│   ├── presidio_nlp_engine_config.py# Presidio configuration
│   └── patterns/                    # Custom PII patterns
│       ├── emp.yaml
│       └── token.yaml
|   └── assets
|       └── system_design.png        # System design image for ppt generation
└── en_core_web_lg-3.8.0-py3-none-any.whl # spaCy model 
```

## Dependencies

### Core Dependencies
- **Streamlit**: Web application framework
- **Microsoft Presidio**: PII detection and anonymization
- **Google GenAI**: AI analysis capabilities
- **spaCy**: Natural language processing (en_core_web_lg model)
- **pandas**: Data manipulation and analysis
- **PIL**: Image processing
- **python-pptx**: PowerPoint file handling
- **PyPDF2**: PDF processing
- **openpyxl**: Excel file handling

### Development Dependencies
- **black**: Code formatting
- **pipreqs**: Dependency management

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

##  Support

For support, issues, or feature requests, please open an issue on GitHub.

---
