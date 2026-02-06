PROHIBITION_PATTERNS = [
    "shall not",
    "must not",
    "is prohibited from",
    "may not"
]

OBLIGATION_PATTERNS = [
    "shall",
    "must",
    "is required to",
    "agrees to"
]

RIGHT_PATTERNS = [
    "may",
    "is entitled to",
    "has the right to",
    "can"
]

def classify_obligation_right_prohibition(text):
    text_lower = text.lower()

    # 1. Prohibition
    for p in PROHIBITION_PATTERNS:
        if p in text_lower:
            return {
                "classification": "Prohibition",
                "signal": p
            }

    # 2. Obligation
    for p in OBLIGATION_PATTERNS:
        if p in text_lower:
            return {
                "classification": "Obligation",
                "signal": p
            }

    # 3. Right
    for p in RIGHT_PATTERNS:
        if p in text_lower:
            return {
                "classification": "Right",
                "signal": p
            }

    return {
        "classification": "Other",
        "signal": None
    }

def infer_party(entities):
    if entities.get("parties"):
        return entities["parties"][0]
    return "Unspecified"

def classify_clause_role(clause):
    text = clause.get("text_original", "")
    entities = clause.get("entities", {})

    result = classify_obligation_right_prohibition(text)

    clause["legal_role"] = {
        "type": result["classification"],
        "trigger_phrase": result["signal"],
        "affected_party": infer_party(entities)
    }

    return clause

def apply_role_classification(storage):
    for clause in storage.get("clauses", []):
        classify_clause_role(clause)

    return storage
