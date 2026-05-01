# Clinical AI Gateway

A security-hardened LLM gateway for healthcare applications.

This project demonstrates how to safely expose a local language model for querying clinical data, with controls for PHI protection, prompt injection defense, and full audit logging.

---

##  What This Is

A reference implementation of a **secure AI inference layer** for clinical environments.

It allows:
- Controlled querying of synthetic patient data
- Enforcement of PHI protection boundaries
- Detection of misuse and adversarial input

---

##  Architecture Overview

```
Client (Streamlit / React via Kasm)
        │
        ▼
FastAPI Gateway (Security Layer)
        │
 ├── Input Validation (Prompt Injection Defense)
 ├── PHI Output Filtering
 ├── Rate Limiting
 ├── Audit Logging → SIEM (Wazuh)
        │
        ▼
Local LLM (Ollama)
        │
        ▼
Vector DB (Qdrant / Chroma)
        │
        ▼
Synthetic Clinical Data (Synthea / OpenEMR)
```

---

## Security Controls

| Control | Description |
|--------|------------|
| Input Validation | Detect and block prompt injection attempts |
| Output Filtering | Prevent PHI leakage |
| Rate Limiting | Prevent abuse |
| Audit Logging | Full request/response metadata logging |
| Access Control | Authenticated gateway access |

Mapped to:
- OWASP LLM Top 10
- HIPAA §164.312
- NIST AI RMF

---

## ⚡ Quickstart

```bash
docker compose up --build
```

Then:

```bash
curl http://localhost:8000/query -d '{"query": "List patient medications"}'
```

---

## Testing

Includes:
- Prompt injection test cases
- PHI leakage scenarios
- Authorization checks

Run:

```bash
pytest
```

---

##  Demo

(will be uploaded later)

---

##  Limitations

- Not production-ready
- Uses synthetic data only
- Limited model performance on CPU
- Basic detection logic (to be extended)

---

##  Documentation

- [Architecture](docs/architecture.md)
- Threat model (coming next)
- Compliance mapping (coming next)

---

##  Why This Matters

Most LLM applications expose models directly.

This project demonstrates how to:
- Treat LLMs as untrusted components
- Enforce security at the gateway
- Build observable and auditable AI systems

---

##  Status

Active development — evolving with security features and detection capabilities.
