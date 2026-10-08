# PDFAPI — REST Service & Surgical PDF Orchestrator

PDFAPI is the high-concurrency commercial backend service for **PDF Engine**, built with **FastAPI**, **Pydantic v2**, and direct integration with native safe **Rust** extensions (`pdf_engine`). It provides a robust RESTful API and WebSocket channels for surgical PDF manipulation, SceneGraph layout inspection, real-time typographic reflow, and cryptographic document security.

---

## PDFEngine Ecosystem

PDFAPI is the service orchestration layer within the decoupled **PDFEngine** multi-repository architecture:

| Repository | Role | Tech Stack | Status |
| :--- | :--- | :--- | :--- |
| [**PDFEngine**](https://github.com/rgarduno/PDFEngine) | High-performance core engine & Python extension module | Rust (ISO 32000-1) + PyO3 | Production-ready |
| [**PDFAPI**](https://github.com/rgarduno/PDFAPI) *(This Repo)* | Commercial multi-tenant REST & WebSocket service | Python 3.13 + FastAPI + Pydantic v2 | Production-ready |
| [**PDFWeb**](https://github.com/rgarduno/PDFWeb) | Interactive Dual-Canvas Web Studio | Next.js 16 (App Router) + React 19 + Tailwind CSS | Production-ready |

---

## Key Features

- **Multi-Tenant Cryptographic Isolation**:
  - Mandatory authentication via `Authorization: Bearer <token>` header.
  - Document sessions indexed by SHA-256 tenant hash; unauthorized or non-existent access requests return `404 Not Found` to prevent timing attacks and document enumeration.
- **Thread-Safe Concurrency & Atomic Locking (`@serialized_mutation`)**:
  - Per-document mutual exclusion (`document_mutation(doc_id)`) preventing race conditions during simultaneous editing operations.
  - Canonical document ID ordering in multi-document operations (merge) to eliminate deadlocks.
- **SceneGraph Inspection & Faithful Typography**:
  - Glyph extraction, bounding boxes ($BBox$), text matrices ($T_m$), leading, baseline calculations, and metric resolution for subsetted and composite Type0 CID fonts.
- **Surgical AST Mutation & Real-Time Live Reflow**:
  - Atomic in-place replacement of text nodes within the page content stream without recompiling or altering non-edited vector artwork, blend modes, or images.
  - Dedicated WebSocket endpoint (`/ws/documents/{id}/pages/{page}/reflow`) for live line-wrap and bounding box calculations as the user types.
- **Enterprise Security & Electronic Signatures**:
  - Detached PKCS#7 / CMS (RFC 5652) digital signatures with RSA and ECDSA keys (PEM and PKCS#12 containers).
  - RFC 3161 Time-Stamp Protocol (TSA) client support embedded into unsigned CMS attributes.
  - Non-contiguous `/ByteRange` SHA-256 integrity attestation.
- **Tamper-Evident Audit Trail**:
  - In-memory structured audit logger recording critical operational events (`document_uploaded`, `redacted`, `signed`, `documents_compared`, etc.) without leaking credentials or sensitive file bytes.
- **Enterprise PDF Operations**:
  - High-precision table extraction (Lattice & Stream algorithms) with multi-format export (JSON, CSV, Markdown, HTML).
  - Surgical redaction of PII (RFC, CURP, SSN, Credit Cards) with full COS tree sanitation.
  - Invisible searchable text layer injection (`3 Tr` rendering mode) over scanned pages via local Tesseract OCR.
  - Archival validation and conversion for PDF/A-1b and PDF/A-2b (ISO 19005).
  - Bidirectional metadata editor and synchronizer (`/Info` and XMP RDF packages).
  - Semantic and visual PDF Diff Engine powered by LCS algorithms.

---

## Prerequisites

- **Python**: `>= 3.10` (Python 3.12 or 3.13 recommended)
- **Tesseract OCR**: (Optional, required only for invisible OCR endpoints)
- **`pdf_engine`**: Native Rust extension module.

---

## Configuration & Environment Variables

Copy `.env.example` to create `.env`:

```bash
cp .env.example .env
```

| Variable | Description | Default |
| :--- | :--- | :--- |
| `PDFENGINE_API_KEYS` | Comma-separated authorized Bearer tokens | `""` |
| `PDFENGINE_CORS_ORIGINS` | Allowed HTTP origins for CORS | `http://localhost:3000` |
| `PDFENGINE_MAX_UPLOAD_BYTES` | Maximum file upload size in bytes | `33554432` (32 MiB) |
| `PDFENGINE_MAX_SESSIONS` | Maximum active document sessions in memory | `32` |
| `PDFENGINE_MAX_RETAINED_BYTES` | Total memory budget for resident documents | `268435456` (256 MiB) |
| `PDFENGINE_SESSION_TTL_SECONDS` | Inactivity TTL before session eviction | `1800` (30 min) |

---

## Installation & Local Development

```bash
# 1. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install the native pdf_engine extension
# Option A: From local PDFEngine repository (editable development mode)
pip install -e ../PDFEngine

# Option B: From precompiled binary wheel
# pip install /path/to/pdf_engine-0.1.0-cp313-cp313-macosx_11_0_arm64.whl

# 4. Start the API server
uvicorn app.main:app --reload --port 8000
```

Interactive OpenAPI / Swagger UI documentation is available at:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Testing & Quality Assurance

Run the comprehensive integration test suite:

```bash
source .venv/bin/activate
pytest tests/ -v
```

---

## Production Deployment with Docker

```bash
# Build container image
docker build -t pdf-api:latest .

# Run containerized service
docker run -d -p 8000:8000 \
  -e PDFENGINE_API_KEYS="your-production-secret-token" \
  -e PDFENGINE_CORS_ORIGINS="https://your-web-studio.com" \
  pdf-api:latest
```

---

## License

Distributed under the MIT License.
