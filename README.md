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
  - Detached PKCS#7 / CMS (RFC 5652) digital signatures with RSA and ECDSA keys (PEM and PKCS#12 containers). A download of a detached PKCS#7 file appends edits after the signed bytes. The original byte range still verifies. The new bytes are not covered. An encrypted PKCS#7 file is not rewritten.
  - After a user password opens the file, this process refuses its own print, copy, and edit when those `/P` bits are clear. The owner password is unrestricted. Print is one raster, allowed when low-resolution print is set. Bit 12 is stored and does not block that raster. Bit 10 is not a separate extract path. Export of the decrypted file drops `/P`. Another program is not bound by these bits. A user password with every enforced bit set is not told apart from the owner, so a later encrypt is allowed. A page already returned still holds the paragraphs it reconstructed. A live reflow that may edit and may not copy applies the edit, then refuses the returned text.
  - RFC 3161 Time-Stamp Protocol (TSA) client support embedded into unsigned CMS attributes.
  - Non-contiguous `/ByteRange` SHA-256 integrity attestation.
- **Tamper-Evident Audit Trail**:
  - In-memory structured audit logger recording critical operational events (`document_uploaded`, `redacted`, `signed`, `documents_compared`, etc.) without leaking credentials or sensitive file bytes.
- **Enterprise PDF Operations**:
  - High-precision table extraction (Lattice & Stream algorithms) with multi-format export (JSON, CSV, Markdown, HTML).
  - Surgical redaction of PII (RFC, CURP, SSN, Credit Cards) with full COS tree sanitation. Redaction of a page string also removes an embedded file whose name, filename, description, or bytes repeat that string when it is at least 4 characters. The whole file is removed. Another value is left. A match on one page removes that file from the whole document. One embedded PDF is opened and its page text is searched; a file inside that PDF is not. Zip and Office files are not unpacked. The redaction also clears a form field's value and appearance when `/V` or `/AP` repeats that string. The widget, the option list, the default value, and the field name stay. An image painted on the page loses the samples that fall inside a redaction rectangle, including pixels under invisible text, and an 8-bit DeviceGray or DeviceRGB image with one decodable filter, including a JPEG, is rewritten as Flate while a filter array, a 1-bit image, CMYK, an inline image, an image inside a form, and an image inside an appearance stay. A structure element loses `/ActualText`, `/Alt`, `/E`, and `/T` when that entry repeats a removed string of at least 4 characters. The element, `/S`, `/P`, `/K`, `/Pg`, the role map, and the parent tree stay. A match on one page clears that text in the whole tree. No page match leaves the tree unchanged. A tree deeper than 64 is not fully cleared. A value that is not a string stays.
  - Invisible searchable text layer injection (`3 Tr` rendering mode) over scanned pages via local Tesseract OCR.
  - Archival validation and conversion for PDF/A-1b and PDF/A-2b (ISO 19005).
  - Bidirectional metadata editor and synchronizer (`/Info` and XMP RDF packages).
  - Semantic and visual PDF Diff Engine powered by LCS algorithms.
  - Page composition: insert a blank page, duplicate a page, copy pages from another session at a 0-based index, or reverse the page order.
  - Read and write MediaBox, CropBox, BleedBox, TrimBox, and ArtBox. Numbers in `/pages/{n}/boxes` start at 1.
  - `POST /api/documents/{id}/search` reads reconstructed paragraph text. The query is not stored. Audit names for this work are `pages_composed`, `page_box_updated`, and `document_searched`.
  - `GET /api/documents/{id}/pages/{n}/raster?format=png|jpeg|tiff&dpi=144` paints one page. `n` starts at 1. Density is from 36 to 300. The bitmap is capped at 12000000 pixels and a side of 65535. The painter is not Acrobat: nested clips, soft masks, transparency groups, and annotation appearances are not composited, rendering mode 3 is not painted, and TIFF is one page. The audit name is `page_rendered`.
  - `POST /api/documents/{id}/pages/{n}/edit/{paragraph_id}` still replaces paragraph text. Optional `font`, `size`, `bold`, `italic`, `color`, `alignment`, and `leading` restyle that replacement. `font` is Helvetica, Times, or Courier (Arial, Times New Roman, and Courier New are aliases). Bold or italic selects that standard face and does not invent a bold twin of an embedded subset. `color` is `#RGB` or `#RRGGBB`. `leading` is points from 1 to 400. A size change with no leading scales the old leading, then keeps it inside `[new size, 400]`. The audit name `paragraph_styled` is recorded only when a style field is set. The new text is not stored in the audit log.
  - `POST /api/documents/{id}/pages/{n}/text-box` appends content-stream text inside a rectangle. `n` starts at 1. The face is Helvetica, Times, or Courier. Defaults are Helvetica, 12 points, black, left, and a leading of 1.2 times the size. The box is not a movable annotation, not `/FreeText`, and not a sticky note. Lines below the rectangle are omitted. The raster paints the standard face as the built-in 5 by 7 glyphs. The audit name `text_box_added` is recorded only after the text is appended. The text is not stored in the audit log.
  - `POST /api/documents/{id}/replace` rewrites reconstructed text. The query is 1 to 512 characters. The replacement may be empty and is at most 4000. A newline is allowed. Other control characters are rejected. A subset is kept only when the new paragraph has a real width for every character. Otherwise the paragraph moves to Helvetica, Times, or Courier and `paragraphs_on_standard_face` counts those paragraphs. A character the standard faces cannot draw changes nothing. A hit cap can stop inside a paragraph. The audit name `text_replaced` is recorded only after a replacement is written. The query and the replacement are not stored.
  - `POST /api/documents/{id}/pages/{n}/fill-sign` appends a typed, drawn, or image signature or initials as page content. `n` starts at 1. A signature name is at most 80 characters. Initials are at most 8. A drawn mark has at most 30 strokes and 2000 points. An image is at most 2000000 bytes and must be JPEG or PNG. A control character, including a newline, is rejected. A drawn point outside the rectangle changes nothing. A character the standard faces cannot draw changes nothing. The audit name `fill_signed` is recorded only after the mark is appended. The name and the image are not stored.
  - `GET /api/documents/{id}/export/docx` writes one Word section per page. The size is the CropBox, or the MediaBox when CropBox is absent. Each margin is the gap to the content, from 36 to 72 points and at most a quarter of that side. A paragraph that starts further right is left-indented. Space before is the gap to the block above, capped at 72 points, and the first block subtracts the top margin. A table uses the width of its box. A document with no pages still emits one US Letter section. Markdown export is unchanged. This is a reconstruction: no floating text boxes, no embedded images, and not Word's page design.
  - `GET /api/documents/{id}/export/xlsx` writes one worksheet for each detected table. The response is an XLSX attachment named `document.xlsx`. Every cell is reconstructed text, including a value that looks like a number or a formula. A span is not a merged cell. The grid stops at 1,048,576 rows, 16,384 columns, and 32,767 characters in a cell. A document with no detected table still returns one empty worksheet named `Tables`. This is not a binary XLS file and it is not Excel's layout. CSV, JSON, Markdown, and HTML export of one table are unchanged. A badly drawn table can still go undetected. The audit name is `document_exported_xlsx`. The cell text is not stored.
  - `GET /api/documents/{id}/export/pptx` writes one slide per page. The response is a PPTX attachment named `document.pptx`. The deck size is the first page's CropBox, or its MediaBox when CropBox is absent. A later page is stretched onto that size. Each paragraph is a text box on its box. A detected table is text in 12-point Arial, and a span is not a merged cell. A cell stops at 32,767 characters. Images are not embedded. A document with no pages still returns one empty US Letter slide. This is not a binary PPT file and it is not PowerPoint's design. DOCX, XLSX, and Markdown export are unchanged. The audit name is `document_exported_pptx`. The slide text is not stored.

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
