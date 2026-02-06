RISK_TYPE_PATTERNS = {
    "Termination": [
        "terminate", "termination", "cancel", "end this agreement"
    ],
    "Indemnity": [
        "indemnify", "hold harmless", "indemnification"
    ],
    "Intellectual Property": [
        "intellectual property", "ip", "copyright",
        "patent", "trademark"
    ],
    "Penalty": [
        "penalty", "liquidated damages", "fine", "interest", "late fee"
    ],
    "Confidentiality": [
        "confidential", "non-disclosure", "nda"
    ],
    "Jurisdiction": [
        "governing law", "jurisdiction", "courts of", "arbitration"
    ],
    "Non-Compete": [
        "non-compete", "shall not engage", "competing business"
    ],
    "Auto-Renewal": [
        "auto-renew", "automatically renew", "renewal unless terminated"
    ]
}
def detect_risk_types(text):
    text_lower = text.lower()
    detected = []

    for risk_type, patterns in RISK_TYPE_PATTERNS.items():
        for p in patterns:
            if p in text_lower:
                detected.append(risk_type)
                break

    return detected

def enrich_clause_with_risk_types(clause):
    text = clause.get("text_original", "")
    clause["risk_types"] = detect_risk_types(text)
    return clause

def apply_risk_type_detection(storage):
    for clause in storage.get("clauses", []):
        enrich_clause_with_risk_types(clause)
    return storage

BASE_RISK_SCORE = {
    "Termination": 70,
    "Indemnity": 75,
    "Intellectual Property": 65,
    "Penalty": 60,
    "Non-Compete": 80,
    "Auto-Renewal": 55,
    "Jurisdiction": 50,
    "Confidentiality": 40
}

ROLE_MULTIPLIER = {
    "Obligation": 1.2,
    "Prohibition": 1.3,
    "Right": 1.1,
    "Other": 1.0
}


def score_clause_risk(clause):
    risk_types = clause.get("risk_types", [])
    role = clause.get("legal_role", {}).get("type", "Other")
    ambiguity = clause.get("ambiguity_flag", False)

    score = 0

    for r in risk_types:
        score = max(score, BASE_RISK_SCORE.get(r, 30))

    score *= ROLE_MULTIPLIER.get(role, 1.0)

    if ambiguity:
        score += 10

    score = min(int(score), 100)

    if score >= 75:
        level = "High"
    elif score >= 45:
        level = "Medium"
    else:
        level = "Low"

    clause["risk_score"] = {
        "score": score,
        "level": level
    }

    return clause

def compute_contract_risk(storage):
    scores = [c["risk_score"]["score"] for c in storage["clauses"]]
    avg = sum(scores) / len(scores)

    if avg >= 75:
        level = "High"
    elif avg >= 45:
        level = "Medium"
    else:
        level = "Low"

    storage["contract_risk_summary"] = {
        "average_score": round(avg, 2),
        "risk_level": level
    }
    return storage

def apply_risk_scoring(storage):
    for clause in storage.get("clauses", []):
        score_clause_risk(clause)
    return storage
