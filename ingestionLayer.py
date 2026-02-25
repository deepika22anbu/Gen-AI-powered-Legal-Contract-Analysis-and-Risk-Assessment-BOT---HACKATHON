import json
import uuid
import datetime
import spacy
import re

nlp = spacy.load("en_core_web_sm")

def extract_clauses(text):
    """
    Extracts clauses using numbering patterns like:
    1., 1.1, 2., 3.2 etc.
    """
    clause_pattern = re.split(r'\n(?=\d+[\.\)])', text)
    clauses = []

    for chunk in clause_pattern:
        chunk = chunk.strip()
        if not chunk:
            continue

        match = re.match(r'(\d+(\.\d+)*)[\.\)]?\s*(.*)', chunk, re.DOTALL)
        if not match:
            clause_id = "Preamble"
            clause_text = chunk
        if match:
            clause_id = match.group(1)
            clause_text = match.group(3).strip()
        else:
            clause_id = str(len(clauses) + 1)
            clause_text = chunk

        clauses.append({
            "clause_id": clause_id,
            "text_original": clause_text
        })

    return clauses

def build_storage_json(raw_text, filename):
    document_id = str(uuid.uuid4())

    clauses = extract_clauses(raw_text)

    storage = {
        "document_id": document_id,
        "document_type": "contract",
        "source_language": "en",
        "normalized_language": "en",
        "contract_type_hint": None,  # filled later
        "metadata": {
            "file_name": filename,
            "uploaded_at": datetime.datetime.utcnow().isoformat(),
            "page_count": None
        },
        "raw_text": raw_text,
        "clauses": [],
        "audit": {
            "ingestion_method": "streamlit_file_upload",
            "confidence": 0.95
        }
    }

    for clause in clauses:
        storage["clauses"].append({
            "clause_id": clause["clause_id"],
            "title": None,
            "text_original": clause["text_original"]
        })

    return storage


