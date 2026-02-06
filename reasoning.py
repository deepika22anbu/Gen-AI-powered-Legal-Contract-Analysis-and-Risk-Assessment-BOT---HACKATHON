import spacy
import re


try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import en_core_web_sm
    nlp = en_core_web_sm.load()

# nlp = spacy.load("en_core_web_sm")

def extract_amounts(text):
    pattern = r'(₹\s?\d+[,\d]*|\bINR\s?\d+[,\d]*|\d+%|\d+\s?percent)'
    return re.findall(pattern, text, re.IGNORECASE)

def extract_obligations(text):
    obligations = []
    keywords = ["shall", "must", "agrees to", "is required to"]

    for kw in keywords:
        if kw in text.lower():
            obligations.append(kw)

    return obligations

def ner_enrich_clause(text):
    doc = nlp(text)

    entities = {
        "parties": [],
        "amounts": extract_amounts(text),
        "dates": [],
        "durations": [],
        "jurisdiction": [],
        "obligations": extract_obligations(text)
    }
    entities["parties"] = clean_parties(entities["parties"])
    for ent in doc.ents:
        if ent.label_ == "ORG":
            entities["parties"].append(ent.text)

        elif ent.label_ in ["DATE"]:
            entities["dates"].append(ent.text)

        elif ent.label_ in ["GPE", "LOC"]:
            entities["jurisdiction"].append(ent.text)

        elif ent.label_ == "TIME":
            entities["durations"].append(ent.text)

    return entities

def enrich_storage_with_ner(storage):
    for clause in storage.get("clauses", []):
        clause_text = clause.get("text_original", "")
        clause["entities"] = ner_enrich_clause(clause_text)

    return storage

def clean_parties(parties):
    blacklist = ["INR", "Scope of Services", "Intellectual Property"]
    return [p for p in parties if p not in blacklist]


def save_enriched_storage(storage, path="enriched_storage.json"):
    import json
    with open(path, "w", encoding="utf-8") as f:
        json.dump(storage, f, indent=2, ensure_ascii=False)
    return storage