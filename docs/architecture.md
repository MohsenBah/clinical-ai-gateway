# Architecture

## 1. Overview

The Clinical AI Gateway is designed as a **security-first inference layer** between users and language models.

The system enforces strict control over:
- Input (user queries)
- Output (model responses)
- Data access (clinical records)
- Observability (logs and audit trails)

---

## 2. Design Principles

- The model is treated as **untrusted**
- All access flows through a **controlled gateway**
- Every interaction is **logged and auditable**
- Security controls exist **outside the model**

---

## 3. High-Level Components

### 3.1 Client Layer

- Streamlit or React UI
- Accessed through Kasm (for sake of isolation)
- No direct access to backend services

---

### 3.2 Gateway Layer (Core)

Implemented using FastAPI.

Responsibilities:
- Request validation
- Security enforcement
- Logging and auditing
- Routing to model and data services

#### Subcomponents

- **Input Validation**
  - Detect prompt injection patterns
- **Output Filtering**
  - PHI detection and masking
- **Rate Limiting**
  - Prevent abuse and scraping
- **Audit Logger**
  - Structured logs (JSON)

---

### 3.3 Model Layer

- Local LLM via Ollama
- Example models:
  - QWEN3.5:9B

Constraints:
- Runs locally (no external API calls)
- Limited compute 

---

### 3.4 Data Layer

- Synthetic patient data (Synthea)
- Optional OpenEMR integration
- Vector database: Chroma
- PHI redaction: Microsoft Presidio

Pipeline:
1. Data ingestion from JSON/CSV
2. PHI detection and anonymization
3. Text chunking and preprocessing
4. Embedding generation (Sentence Transformers)
5. Storage in Chroma vector database
6. Semantic search for RAG queries

---

### 3.5 Observability Layer

- Structured logs from gateway
- Forwarded to SIEM (Wazuh)
- Used for:
  - Detection engineering
  - Incident analysis

---

## 4. Data Flow

1. User sends query
2. Gateway validates input
3. Gateway retrieves relevant data (RAG)
4. Query sent to LLM
5. Response filtered for PHI
6. Response returned to user
7. Full interaction logged

---

## 5. Security Boundaries

| Boundary | Purpose |
|---------|--------|
| Gateway | Primary enforcement point |
| Model | Untrusted processing |
| Data | Protected clinical context |
| Logs | Audit and detection |

---

## 6. Future Extensions

- mTLS between services
- Token-based authentication
- Advanced prompt filtering (LLM Guard)
- Real-time anomaly detection
- Integration with detection rules

---

## 7. Summary

The architecture enforces a key principle:

> The model is not the system. The gateway is.

Security, control, and observability are handled externally, making the system robust against misuse and adversarial behavior.
