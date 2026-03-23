# Rule-based mapping of detected PII entity types to GDPR / Compliance references.
# Note: Financial data like Credit Cards is strictly speaking Art. 4(1) / Art. 32 under GDPR
# but triggers major PCI-DSS requirements. Health data maps to Art. 9.

GDPR_MAPPING = {
    "PERSON": "Art. 4(1) — Personal Data (Identified or Identifiable Natural Person)",
    "EMAIL_ADDRESS": "Art. 4(1) — Personal Data (Contact Identifier)",
    "PHONE_NUMBER": "Art. 4(1) — Personal Data (Contact Identifier)",
    "CREDIT_CARD": "Art. 32 — High Risk / PCI-DSS Financial Data",
    "MEDICAL_LICENSE": "Art. 9(1) — Special Category (Health Data)",
    "US_SSN": "Art. 87 — National Identification Number",
    "US_PASSPORT": "Art. 87 — National Identification Number",
    "IBAN_CODE": "Art. 32 — High Risk Financial Data",
    "DATE_TIME": "Contextual — May contribute to identifiability",
    "IP_ADDRESS": "Recital 30 — Online Identifier (Considered Personal Data)",
    "LOCATION": "Art. 4(1) — Personal Data (Location Data)",
    "ORGANIZATION": "Contextual — Usually Non-PII unless linking to sole trader",
}

def get_gdpr_reference(entity_type: str) -> str:
    """
    Returns legal/compliance context for a given entity type.
    """
    return GDPR_MAPPING.get(entity_type, "Unclassified — Requires Manual Review")
