import textwrap

import streamlit as st
import pdfplumber
import docx
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import tempfile

from LLMPrompt import apply_llm_explanations
from ingestionLayer import build_storage_json
from reasoning import enrich_storage_with_ner, save_enriched_storage
from translator import normalize_to_english
from DeterministicLayer import apply_role_classification
from riskIndication import apply_risk_type_detection, apply_risk_scoring, compute_contract_risk


headers = {
    "authorization" : st.secrets["auth_key"]
}
# Page Config

st.set_page_config(
    page_title="GenAI Contract Analysis and Risk Assessment Bot (MVP)",
    layout="centered"
)

st.title("GenAI Contract Analysis and Risk Assessment for SMEs (MVP)")
st.caption("Understand contracts. Identify risks. Get Suggestion and clarity.")


# Sidebar Controls

st.sidebar.header("Input Settings")

language = st.sidebar.selectbox(
    "Select Contract Language",
    ["English", "Hindi"]
)

file_format = st.sidebar.selectbox(
    "Select Contract File Format",
    [".pdf", ".docx", ".doc", ".txt"]
)


# File Upload

uploaded_file = st.file_uploader(
    "Upload Contract File",
    type=[file_format.replace(".", "")]
)


# Utility Functions

def extract_text(file, ext):
    if ext == ".pdf":
        with pdfplumber.open(file) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)

    elif ext in [".doc", ".docx"]:
        doc = docx.Document(file)
        return "\n".join(p.text for p in doc.paragraphs)

    elif ext == ".txt":
        return file.read().decode("utf-8")

    return ""


# Normalizing Layer for Analysis




def generate_summary(json):
    """
    Generate an English business-friendly contract summary
    based on clause-level risk analysis.
    """

    clauses = json.get("clauses", [])
    contract_risk = json.get("contract_risk_summary", {})

    high_risk = []
    medium_risk = []
    key_risk_types = set()

    for clause_item in clauses:
        risk_score = clause_item.get("risk_score", {})
        risk_level = risk_score.get("level")
        risk_types = clause_item.get("risk_types", [])

        if risk_level == "High":
            high_risk.append(str(clause_item.get("clause_id")))
        elif risk_level == "Medium":
            medium_risk.append(str(clause_item.get("clause_id")))

        for r in risk_types:
            key_risk_types.add(r)

    output_summary = (
        "This contract defines the business relationship between the parties. "
        f"Based on clause-level analysis, the overall contract risk level is "
        f"**{contract_risk.get('risk_level', 'Unknown')}**.\n\n"
    )

    if high_risk:
        output_summary += (
            f"⚠️ **High-risk clauses** were identified in sections "
            f"{', '.join(high_risk)}. These clauses may significantly impact "
            "financial exposure, termination rights, or intellectual property ownership.\n\n"
        )

    if medium_risk:
        output_summary += (
            f"🟠 **Medium-risk clauses** were found in sections "
            f"{', '.join(medium_risk)} and may require clarification or renegotiation.\n\n"
        )

    if key_risk_types:
        output_summary += (
            "🔍 **Key risk areas identified** include: "
            f"{', '.join(sorted(key_risk_types))}.\n\n"
        )

    output_summary += (
        "📌 **Business Advice:** While the agreement covers standard commercial terms, "
        "certain clauses appear one-sided and could expose your business to avoidable risk. "
        "It is recommended to review and renegotiate high-risk sections before signing."
    )

    return output_summary


def create_pdf(summary_text):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix= ".pdf")
    c = canvas.Canvas(temp_file.name, pagesize=A4)
    width, height = A4

    text_obj = c.beginText(40, height - 50)
    text_obj.setFont("Helvetica", 11)

    wrapped_lines = textwrap.wrap(summary_text, width=90)

    for line in wrapped_lines:
        text_obj.textLine(line)

    c.drawText(text_obj)
    c.showPage()
    c.save()

    return temp_file.name


# Main Logic

if uploaded_file:
    st.success("File uploaded successfully!")

if st.button("🔍 Analyze Contract"):

    with st.spinner("Reading contract..."):
        extracted_text = extract_text(uploaded_file, file_format)
        normalized_text =  normalize_to_english(extracted_text)

        storage_json = build_storage_json(normalized_text, uploaded_file.name)

        # 1️⃣ NER Enrichment
        enriched_storage = enrich_storage_with_ner(storage_json)

        # 2️⃣ Obligation / Right / Prohibition
        enriched_storage = apply_role_classification(enriched_storage)

        # 3️⃣ Risk Type Detection
        enriched_storage = apply_risk_type_detection(enriched_storage)

        # 4️⃣ Clause-Level Risk Scoring
        enriched_storage = apply_risk_scoring(enriched_storage)

        llm_storage = apply_llm_explanations(enriched_storage)


        storage = compute_contract_risk(llm_storage)

        # UI Output (Clause-Level)
        for clause in storage["clauses"]:
            with st.expander(f"Clause {clause['clause_id']}"):
                st.write("**Clause Text:**", clause["text_original"])
                st.write("**Risk Level:**", clause["risk_score"]["level"])

                llm = clause.get("llm_explanation", {})
                st.write("**Explanation:**", llm.get("plain_language_explanation"))
                st.write("**Why Risky:**", llm.get("risk_reasoning"))
                st.write("**Suggested Alternative:**", llm.get("suggested_alternative_clause"))


        # Persist JSON
        final_json = save_enriched_storage(llm_storage)

        summary = generate_summary(final_json)
        st.subheader("📘 Contract Summary")
        st.write(summary)



        # Export as PDF
        pdf_path = create_pdf(summary)

        with open(pdf_path, "rb") as f:
            st.download_button(
                    label="⬇️ Download Summary as PDF",
                    data=f,
                    file_name="Contract_summary.pdf",
                    mime="application/pdf"
                )

            # os.remove(pdf_path)


# Footer

st.markdown("---")
st.caption(
    "⚠️ Disclaimer: This tool provides informational insights only and does not constitute legal advice."
)


