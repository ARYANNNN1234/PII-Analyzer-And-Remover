import streamlit as st
import pandas as pd
from typing import List

from pipeline import get_set_go
from helpers import list_to_html_ol, my_logger
from models import ProcessedFile, filetypes
from generate_ppt import create_presentation

st.set_page_config(page_title="File Analysis", layout="wide")
st.title("PII Remover and Analyser")
st.page_link(
    "https://github.com/pii-remover-analyser",
    label="GitHub Repo",
)

uploaded_files = st.file_uploader(
    "Upload files (.png, .jpg, .pdf, .xlsx, .pptx)",
    type=["png", "jpg", "jpeg", "pdf", "xlsx", "pptx"],
    accept_multiple_files=True,
)

results: List[ProcessedFile] = []

generate_ppt = st.button(label="Generate PPT from analysis")
download_button = st.download_button
table_rows_for_ppt = []

if uploaded_files:
    for file in uploaded_files:
        with st.spinner(f"Processing {file.name}..."):

            try:
                data_from_pipeline = get_set_go(file)

                if data_from_pipeline:

                    results.append(
                        ProcessedFile(
                            file_name=file.name,
                            file_type=filetypes[file.type],
                            file_heading=data_from_pipeline["file_description"][
                                "heading"
                            ],
                            file_description=data_from_pipeline["file_description"][
                                "description"
                            ],
                            key_findings=data_from_pipeline["key_findings"],
                        )
                    )

            except Exception as e:
                st.error(f"Error processing {file.name}: {e}")
                my_logger.error(f"Error processing {file.name}: {e}")

if results:
    table_rows_for_ui_display = []

    for r in results:
        table_rows_for_ui_display.append(
            {
                "File Name": r.file_name,
                "File Type": r.file_type,
                "File Description": f"<b>{r.file_heading}</b>"
                + "<br>"
                + r.file_description,
                "Key Findings": r.key_findings,
            }
        )

        table_rows_for_ppt.append(
            [
                r.file_name,
                r.file_type,
                r.file_heading,
                r.file_description,
                r.key_findings,
            ]
        )

    df = pd.DataFrame(table_rows_for_ui_display)

    st.subheader("File Analysis Output")

    df["Key Findings"] = df["Key Findings"].apply(list_to_html_ol)

    st.markdown(df.to_html(escape=False), unsafe_allow_html=True)


if generate_ppt:
    try:
        if not results:
            st.warning("Please upload files before generating PPT.")
            st.stop()

        report_dict = create_presentation(table_rows_for_ppt)
        ppt_bytes = report_dict
        download_button(
            label="Download PPT",
            data=ppt_bytes,
            file_name="analysis_output.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )

    except Exception as e:
        st.error(f"Error generating PPT: {e}")
        my_logger.error(f"Error generating PPT: {e}")
