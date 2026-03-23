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
    file_heading: str
    file_description: str
    key_findings: str
