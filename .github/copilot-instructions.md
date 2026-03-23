# PII Remover and Analyser - AI Coding Instructions

## Architecture Overview

This is a **Streamlit-based security analysis tool** that processes multiple file formats, removes PII using Microsoft Presidio, and generates security insights using Google Gemini AI. The core workflow follows a **pipeline pattern**: Upload → PII Removal → AI Analysis → Report Generation.

### Key Components
- **Entry Point**: `main.py` launches Streamlit via `src/streamlit_app.py`
- **Processing Pipeline**: `src/pipeline.py` orchestrates the entire flow based on file type
- **PII Removal**: `src/pii_remover.py` handles text, image, and DataFrame anonymization using Presidio
- **AI Analysis**: `src/gemini_data_analyzer.py` interfaces with Google Gemini for security insights
- **Content Extraction**: `src/helpers.py` extracts text/images from PPTX/PDF files
- **Output Generation**: `src/generate_ppt.py` creates presentation reports

## Development Patterns

### File Processing Strategy
The pipeline handles 5 file types with different processing paths:
```python
# Images: PIL → Presidio redaction → Gemini analysis
# Excel: pandas → DataFrame anonymization → Gemini analysis  
# PPTX: Extract text/tables/images → Individual PII removal → Combined analysis
# PDF: Extract text/images → PII removal → Combined analysis
```

### Streamlit Caching Strategy
**Critical**: Use `@st.cache_resource` for expensive engine initialization:
- `analyzer_engine()` - Presidio analyzer with custom NLP config
- `anonymizer_engine()` - Presidio anonymizer
- `image_redactor_engine()` - Presidio image redactor

### Custom PII Recognition
Add new PII patterns in `src/patterns/` using YAML format:
```yaml
recognizers:
  - name: "Employee ID Recognizer"
    supported_entity: "EMPID"
    patterns:
      - regex: "^EMP....."
        score: 0.8
```

## Environment Setup

### Required Environment Variables
Create `.env` file with:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

### Dependencies Management
- Uses `uv` for dependency management (see `uv.lock`)
- Requires spaCy model: `en_core_web_lg-3.8.0-py3-none-any.whl` (included in repo)
- Install: `uv sync` or traditional `pip install -r pyproject.toml`

### Running the Application
```bash
# Method 1: Via main script
python main.py

# Method 2: Direct Streamlit
streamlit run src/streamlit_app.py
```

## Key Integration Points

### Presidio Configuration
Custom NLP engine configuration in `src/presidio_nlp_engine_config.py`:
- Loads spaCy model `en_core_web_lg`
- Configures entity mappings for consistent PII detection
- Automatically loads custom recognizers from `patterns/` directory

### Gemini AI Interface
All AI analysis functions return structured JSON with:
```json
{
  "file_description": {
    "heading": "...",
    "description": "..."
  },
  "key_findings": ["finding1", "finding2", ...]
}
```

### Error Handling Pattern
All processing functions use try-catch with structured error returns:
```python
return {"error": str(e)}  # On failure
```

## Testing & Debugging

### Debug Mode
Uncomment debug sections in `pii_remover.py` to see before/after comparisons in Streamlit UI.

### Common Issues
- **Missing .env**: Gemini API calls will fail silently
- **spaCy model**: Download `en_core_web_lg` if import errors occur
- **File size limits**: Streamlit has default upload limits for large files

## File Organization
- `src/` - All source code
- `src/patterns/` - Custom PII recognition patterns
- `.env` - Environment variables (gitignored)
- Generated `.pptx` files are excluded from git

When modifying this codebase, maintain the pipeline pattern and ensure proper Streamlit caching for performance.