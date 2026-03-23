import io
import streamlit as st
from PIL import Image

import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_image_redactor import ImageRedactorEngine

from helpers import my_logger
from presidio_nlp_engine_config import create_nlp_engine_with_spacy
from compliance.gdpr_mapping import get_gdpr_reference


@st.cache_resource(show_spinner=False)
def image_redactor_engine():
    return ImageRedactorEngine()


@st.cache_resource(show_spinner=False)
def analyzer_engine():
    nlp_engine, registry = create_nlp_engine_with_spacy()
    return AnalyzerEngine(nlp_engine=nlp_engine, registry=registry)


@st.cache_resource(show_spinner=False)
def anonymizer_engine():
    return AnonymizerEngine()


def remove_pii_from_text(input_text):
    try:
        results = analyzer_engine().analyze(
            text=input_text,
            language="en",
            score_threshold=0.3,
        )

        anonymized_text = anonymizer_engine().anonymize(
            text=input_text, analyzer_results=results  # type: ignore
        )

        # Debug: Display original and anonymized text

        # col1, col2 = st.columns(2)
        # col1.write(input_text)
        # col2.write(anonymized_text.text)

        report = [
            {
                "Entity": r.entity_type,
                "Score": round(r.score, 3),
                "GDPR Reference": get_gdpr_reference(r.entity_type),
                "Snippet": input_text[r.start:r.end][:30] + "..." if len(input_text[r.start:r.end]) > 30 else input_text[r.start:r.end]
            }
            for r in results
        ]

        return anonymized_text.text, report
    except Exception as e:
        my_logger.error(f"Error removing pii from text: {e}")
        raise


def remove_pii_from_image(input_file):
    try:

        image_redactor = image_redactor_engine()

        if type(input_file) == bytes:
            image = Image.open(io.BytesIO(input_file))

        elif hasattr(input_file, "mode") and hasattr(input_file, "size"):
            image = input_file

        else:
            image = Image.open(input_file)

        pii_removed_image = image_redactor.redact(image=image, fill=(255, 0, 0))  # type: ignore

        # Debug: Display original and redacted images

        # col1, col2 = st.columns(2)
        # col1.image(input_file, caption="Original Image", width="content")
        # col2.image(
        #     pii_removed_image,  # type: ignore
        #     caption="PII Redacted Image",
        #     width="content",
        # )

        return pii_removed_image

    except Exception as e:
        my_logger.error(f"Error removing pii from file {input_file}: {e}")
        raise


def remove_pii_from_df(df):
    try:
        anonymized_df = df.copy()
        report = []
        for column in anonymized_df.select_dtypes(include=["object"]).columns:
            for index, value in anonymized_df[column].items():
                if isinstance(value, str):
                    results = analyzer_engine().analyze(
                        text=value,
                        language="en",
                        score_threshold=0,
                    )
                    if results:
                        anonymized_value = anonymizer_engine().anonymize(
                            text=value,
                            analyzer_results=results,  # type: ignore
                        )
                        anonymized_df.at[index, column] = anonymized_value.text
                        for r in results:
                            report.append({
                                "Entity": r.entity_type,
                                "Score": round(r.score, 3),
                                "GDPR Reference": get_gdpr_reference(r.entity_type),
                                "Snippet": value[r.start:r.end][:30] + "..." if len(value[r.start:r.end]) > 30 else value[r.start:r.end]
                            })

        # Debug: Display original DataFrame and anonymized DataFrame

        # col1, col2 = st.columns(2)
        # col1.dataframe(df)
        # col2.dataframe(anonymized_df)

        return anonymized_df, report
    except Exception as e:
        my_logger.error(f"Error removing pii from dataframe: {e}")
        raise
