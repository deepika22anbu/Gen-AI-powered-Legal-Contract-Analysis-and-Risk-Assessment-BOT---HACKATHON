import json

from llm_client import call_llm


def needs_llm(clause):
    return clause.get("risk_score", {}).get("level") in ["Medium", "High"]


def build_batch_prompt(clauses):
    clause_blocks = []

    for clause in clauses:
        clause_blocks.append(
            f"""
Clause ID: {clause['clause_id']}
Clause Text: "{clause['text_original']}"
Legal Role: {clause['legal_role']['type']}
Risk Types: {clause.get('risk_types', [])}
Risk Level: {clause.get('risk_score', {}).get('level')}
"""
        )

    return f"""
For EACH clause below, return a JSON object keyed by Clause ID.

For each clause:
1. Explain the clause in simple business language
2. Explain why it may be risky
3. Suggest a safer alternative clause wording
4. Provide confidence (0–1)

Rules:
- No legal advice
- No laws or cases
- Plain business English
- JSON ONLY

Expected format:
{{
  "1": {{
    "plain_language_explanation": "...",
    "risk_reasoning": "...",
    "suggested_alternative_clause": "...",
    "llm_confidence": 0.85
  }}
}}

Clauses:
{''.join(clause_blocks)}
"""


def apply_llm_explanations(storage):
    clauses = storage.get("clauses", [])

    risky_clauses = [c for c in clauses if needs_llm(c)]

    if risky_clauses:
        prompt = build_batch_prompt(risky_clauses)
        raw_output = call_llm(prompt)


        try:
            llm_results = json.loads(raw_output)
        except json.JSONDecodeError:
            llm_results = {}

    else:
        llm_results = {}

    for clause in clauses:
        clause_id = str(clause["clause_id"])

        if clause_id in llm_results:
            clause["llm_explanation"] = llm_results[clause_id]
        else:
            clause["llm_explanation"] = {
                "plain_language_explanation": "This clause is standard and low risk.",
                "risk_reasoning": None,
                "suggested_alternative_clause": None,
                "llm_confidence": 1.0
            }

    return storage
