import streamlit as st
import pandas as pd
from typing import List

from pipeline import get_set_go
from helpers import list_to_html_ol, my_logger
from models import ProcessedFile, filetypes
from generate_ppt import create_presentation

st.set_page_config(page_title="File Analyser", layout="wide")
st.title("PII remover and analyser")
st.page_link(
    "https://github.com/pii-remover-analyser",
    label="GitHub Repo",
)

uploaded_files = st.file_uploader(
    "Upload files (.png, .jpg, .pdf, .xlsx, .pptx)",
    type=["png", "jpg", "jpeg", "pdf", "xlsx", "pptx"],
    accept_multiple_files=True,
)

generate_ppt = st.button(label="Generate PPT from analysis")
download_button = st.download_button

if "results" not in st.session_state:
    st.session_state["results"] = []
if "ppt_rows" not in st.session_state:
    st.session_state["ppt_rows"] = []
if "files_key" not in st.session_state:
    st.session_state["files_key"] = None
if "results_map" not in st.session_state:
    st.session_state["results_map"] = {}


def create_results_table(results: List[ProcessedFile]) -> str:
    if not results:
        return ""

    table_rows = []
    for r in results:
        table_rows.append(
            {
                "File Name": r.file_name,
                "File Type": r.file_type,
                "Classification": f"<b>{r.doc_class}</b> ({r.doc_confidence})<br>{r.doc_reasoning}",
                "PII Risk": r.pii_risk,
                "Regulatory": r.regulatory_exposure,
                "Residual Risk": r.residual_risk,
                "Actions": r.recommended_actions,
            }
        )
        st.session_state["ppt_rows"].append(
            [
                r.file_name,
                r.file_type,
                f"{r.doc_class} ({r.doc_confidence})",
                r.doc_reasoning,
                r.regulatory_exposure + r.residual_risk + r.recommended_actions,
            ]
        )

    df = pd.DataFrame(table_rows)
    for col in ["PII Risk", "Regulatory", "Residual Risk", "Actions"]:
        if col in df.columns:
            df[col] = df[col].apply(list_to_html_ol)

    return df.to_html(escape=False)


results: List[ProcessedFile] = st.session_state["results"]

if uploaded_files:
    new_processed = False

    def _key(f):
        return (f.name, getattr(f, "size", None), f.type)

    current_keys = [_key(f) for f in uploaded_files]
    results_map = st.session_state["results_map"]

    new_files = [f for f in uploaded_files if _key(f) not in results_map]

    if new_files:
        new_processed = True
        progress_container = st.container()
        results_container = st.empty()

        with progress_container:
            st.subheader("Processing Files")
            progress_bar = st.progress(0)
            status_text = st.empty()

        total_new = len(new_files)

        for i, file in enumerate(new_files):
            progress_bar.progress((i + 1) / max(total_new, 1))
            status_text.text(f"Processing {file.name}... ({i+1}/{total_new})")

            with st.spinner(f"Processing {file.name}..."):
                try:
                    data_from_pipeline = get_set_go(file)
                    if data_from_pipeline:
                        if "error" in data_from_pipeline:
                            st.error(
                                f"Error processing {file.name}: {data_from_pipeline['error']}"
                            )
                            my_logger.error(
                                f"Pipeline error for {file.name}: {data_from_pipeline['error']}"
                            )
                        else:
                            processed = ProcessedFile(
                                file_name=file.name,
                                file_type=filetypes.get(file.type, ""),
                                doc_class=data_from_pipeline.get("document_classification", {}).get("type", "Unknown"),
                                doc_confidence=data_from_pipeline.get("document_classification", {}).get("confidence", "Unknown"),
                                doc_reasoning=data_from_pipeline.get("document_classification", {}).get("reasoning", ""),
                                pii_risk=data_from_pipeline.get("pii_risk_assessment", []),
                                regulatory_exposure=data_from_pipeline.get("regulatory_exposure", []),
                                residual_risk=data_from_pipeline.get("residual_risk", []),
                                recommended_actions=data_from_pipeline.get("recommended_actions", []),
                                detection_report=data_from_pipeline.get("detection_report", []),
                            )
                            results_map[_key(file)] = processed

                            if processed.detection_report:
                                st.sidebar.subheader(f"🔍 PII Confidence: {file.name}")
                                st.sidebar.dataframe(pd.DataFrame(processed.detection_report), hide_index=True)

                            with results_container.container():
                                st.subheader("File Analysis Output")
                                current_results = [
                                    results_map[k]
                                    for k in current_keys
                                    if k in results_map
                                ]
                                table_rows = [
                                    {
                                        "File Name": r.file_name,
                                        "File Type": r.file_type,
                                        "Classification": f"<b>{r.doc_class}</b> ({r.doc_confidence})<br>{r.doc_reasoning}",
                                        "PII Risk": r.pii_risk,
                                        "Regulatory": r.regulatory_exposure,
                                        "Residual Risk": r.residual_risk,
                                        "Actions": r.recommended_actions,
                                    }
                                    for r in current_results
                                ]
                                if table_rows:
                                    df = pd.DataFrame(table_rows)
                                    for col in ["PII Risk", "Regulatory", "Residual Risk", "Actions"]:
                                        if col in df.columns:
                                            df[col] = df[col].apply(list_to_html_ol)
                                    st.markdown(
                                        df.to_html(escape=False),
                                        unsafe_allow_html=True,
                                    )
                except Exception as e:
                    st.error(f"Error processing {file.name}: {e}")
                    my_logger.error(f"Error processing {file.name}: {e}")

        progress_bar.progress(1.0)
        status_text.text(f"Completed processing {total_new} new file(s)!")

    current_results = [results_map[k] for k in current_keys if k in results_map]
    st.session_state["results"] = current_results

    st.session_state["ppt_rows"] = [
        [
            r.file_name,
            r.file_type,
            f"{r.doc_class} ({r.doc_confidence})",
            r.doc_reasoning,
            r.regulatory_exposure + r.residual_risk + r.recommended_actions,
        ]
        for r in current_results
    ]

    if not new_processed:
        if current_results:
            df = pd.DataFrame(
                [
                    {
                        "File Name": r.file_name,
                        "File Type": r.file_type,
                        "Classification": f"<b>{r.doc_class}</b> ({r.doc_confidence})<br>{r.doc_reasoning}",
                        "PII Risk": r.pii_risk,
                        "Regulatory": r.regulatory_exposure,
                        "Residual Risk": r.residual_risk,
                        "Actions": r.recommended_actions,
                    }
                    for r in current_results
                ]
            )
            for col in ["PII Risk", "Regulatory", "Residual Risk", "Actions"]:
                if col in df.columns:
                    df[col] = df[col].apply(list_to_html_ol)
            st.subheader("File Analysis Output")
            st.markdown(df.to_html(escape=False), unsafe_allow_html=True)
        else:
            st.info("Upload files to see analysis results.")

if generate_ppt:
    try:
        if not st.session_state["results"]:
            st.warning("Please upload files before generating PPT.")
            st.stop()

        report_dict = create_presentation(
            st.session_state["ppt_rows"],
        )
        download_button(
            label="Download PPT",
            data=report_dict,
            file_name="analysis_output.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )

    except Exception as e:
        st.error(f"Error generating PPT: {e}")
        my_logger.error(f"Error generating PPT: {e}")
