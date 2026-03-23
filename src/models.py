from dataclasses import dataclass

filetypes = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",  # add this
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
}


@dataclass
class ProcessedFile:
    file_name: str
    file_type: str
    doc_class: str
    doc_confidence: str
    doc_reasoning: str
    pii_risk: list
    regulatory_exposure: list
    residual_risk: list
    recommended_actions: list
    detection_report: list
