FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libgl1 \
    libglib2.0-0 \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./

RUN pip3 install --no-cache-dir spacy

RUN pip3 install --no-cache-dir .

COPY src/ ./src/

ENV PYTHONPATH=/app/src

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "src/better_ui.py", "--server.port=8501", "--server.address=0.0.0.0"]