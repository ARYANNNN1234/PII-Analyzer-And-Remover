FROM python:3.12-slim

# Install system dependencies required for OCR (Image Redaction)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency definitions
COPY pyproject.toml README.md ./

# We upgrade pip to ensure smooth installation, then install project packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Download the spaCy model required by Presidio
RUN python -m spacy download en_core_web_lg

# Copy application code
COPY src/ ./src/
COPY main.py .

EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]