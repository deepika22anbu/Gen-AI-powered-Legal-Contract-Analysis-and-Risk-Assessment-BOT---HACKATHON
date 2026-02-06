# Gen-AI-powered-Legal-Contract-Analysis-and-Risk-Assessment-BOT---HACKATHON
An AI-driven legal assistant that enables SMEs to understand complex contracts, identify risks, and make informed decisions before signing.  Built as a hackathon-ready, production-deployable prototype, the platform uses Large Language Models (LLMs) and modular reasoning layers to convert dense legal documents into clear, actionable insights.

# 📌 Problem Statement
“Simplifying Legal Contracts Using AI for Small & Medium Businesses”

Small and medium businesses often enter into legal agreements such as employment contracts, vendor agreements, service contracts, and leases without fully understanding the legal implications due to:

Complex legal language 

Lack of access to legal experts 

Time and cost constraints

This results in: Unfavorable clauses, Hidden liabilities, Compliance risks, Costly disputes

# ❗ Challenge
Build an AI-powered system that can:

Analyze legal contracts

Explain clauses in plain English

Identify potential risks

Assist non-legal users in decision-making

# I developed a GenAI-powered Contract Analysis and Risk Assessment

Accepts contract documents in English or Hindi (PDF / DOCX / Text)

Extracts raw contract text from uploaded files

Translates Hindi contracts into simple English using a dedicated Translation Layer

Breaks contracts into structured clauses

Explains each clause in plain, non-legal English

Highlights potential risks and red flags

Generates a concise contract summary

Uses LLM-based reasoning with a modular, extensible design

This ensures language accessibility for Indian users who may receive contracts in Hindi but need explanations in simple, understandable English.

# 🔹 Architecture Layer Explanation
# 1️⃣ Document Ingestion Layer

Extracts raw text from uploaded PDF, DOCX, or TXT contracts

Handles formatting inconsistencies and encoding issues

# 2️⃣ Translation Layer (Hindi → Simple English)

Detects non-English (Hindi) content

Converts Hindi legal text into simple English

Ensures downstream AI reasoning works on a common language

Improves accessibility for Indian SMB users

# 3️⃣ Deterministic Layer

Splits contract text into structured clauses

Identifies headings, numbering, and sections

# 4️⃣ Reasoning Layer

Enhances clauses with contextual understanding

Prepares structured inputs for LLM analysis

# 5️⃣ Risk Indication Layer

Flags potentially unfavorable or risky clauses

Identifies payment, termination, liability, and compliance risks

# 6️⃣ LLM Integration Layer

Uses Groq LLM (LLaMA 3) for explanations and summaries

Agent-ready design for future multi-step legal reasoning

# 7️⃣ Output Layer

Displays:
Clause explanations

Risk insights

Plain-English contract summary
