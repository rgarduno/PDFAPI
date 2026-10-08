# PDFAPI — Servicio REST y Orquestador de Edición Quirúrgica de PDFs

PDFAPI es el backend comercial de alta concurrencia para **PDF Engine**, construido con **FastAPI**, **Pydantic v2** y comunicación directa a través de extensiones nativas en **Rust** (`pdf_engine`). Proporciona una interfaz RESTful y WebSockets para la manipulación quirúrgica, inspección de SceneGraph, reflow en vivo y seguridad criptográfica de documentos PDF.

---

## Ecosistema PDFEngine

PDFAPI es el componente de servicios dentro de la arquitectura de repositorios desacoplados de **PDFEngine**:

| Repositorio | Rol | Stack Tecnológico | Estado |
| :--- | :--- | :--- | :--- |
| [**PDFEngine**](https://github.com/rgarduno/PDFEngine) | Núcleo algorítmico de alto rendimiento y extensión nativa Python | Rust (ISO 32000-1) + PyO3 | Producción |
| [**PDFAPI**](https://github.com/rgarduno/PDFAPI) *(Este Repo)* | Backend comercial REST, WebSockets y control multi-tenant | Python 3.13 + FastAPI + Pydantic v2 | Producción |
| [**PDFWeb**](https://github.com/rgarduno/PDFWeb) | Estudio web interactivo con arquitectura Dual-Canvas | Next.js 16 + React 19 + Tailwind CSS | Producción |

---

## Características Principales

- **Aislamiento Criptográfico Multi-Inquilino (Multi-Tenant)**:
  - Autenticación obligatoria mediante encabezado `Authorization: Bearer <token>`.
  - Las sesiones de documentos están indexadas por hash SHA-256 del inquilino; peticiones ajenas o inexistentes retornan `404 Not Found` para evitar enumeración.
- **Concurrencia Segura y Bloqueo Atómico (`@serialized_mutation`)**:
  - Exclusión mutua por documento (`document_mutation(doc_id)`) para evitar condiciones de carrera durante ediciones simultáneas.
  - Ordenamiento canónico de IDs en operaciones multi-documento (fusión/merge) para prevenir interbloqueos (*deadlocks*).
- **Inspección de SceneGraph y Tipografía Fidedigna**:
  - Extracción de glifos, cajas delimitadoras ($BBox$), matrices de texto ($T_m$), interlineado y anchos de fuentes subsetteadas y compuestas Type0.
- **Mutación Quirúrgica & Reflow en Vivo**:
  - Sustitución atómica de nodos de texto y actualización del content stream sin recomponer el documento ni alterar vectores/imágenes no modificados.
  - Canal WebSocket (`/ws/documents/{id}/pages/{page}/reflow`) para cálculo de saltos de línea y ancho en tiempo real mientras el usuario escribe en Web Studio.
- **Seguridad Documental y Firma Electrónica**:
  - Firma digital detached PKCS#7 / CMS (RFC 5652) con llaves RSA o ECDSA (formatos PEM y PKCS#12).
  - Embebido de sellos de tiempo RFC 3161 mediante cliente TSA integrado.
  - Atestación de rango de bytes SHA-256 sobre rangos no contiguos `/ByteRange`.
- **Auditoría Inmutable**:
  - Pista de auditoría en memoria que registra eventos (`document_uploaded`, `redacted`, `signed`, `documents_compared`, etc.) sin exponer secretos ni contenido sensible.
- **Herramientas de Valor Empresarial**:
  - Detección de tablas (Lattice & Stream) y exportación a JSON, CSV, Markdown y HTML.
  - Censura quirúrgica de datos personales (RFC, CURP, SSN, tarjetas bancarias) con purga en árbol COS.
  - Inyección de capa de búsqueda OCR invisible (`3 Tr`) en páginas escaneadas.
  - Validación y conversión archivística PDF/A-1b y PDF/A-2b (ISO 19005).
  - Sincronización bidireccional de metadatos `/Info` y XMP.
  - Motor de comparación y diferencias (Diff Engine) con algoritmo LCS seguro.

---

## Requisitos Previos

- **Python**: `>= 3.10` (Recomendado Python 3.12 o 3.13)
- **Tesseract OCR**: (Opcional, necesario para endpoints de OCR invisible)
- **`pdf_engine`**: Extensión nativa de Rust compilada.

---

## Configuración y Variables de Entorno

Crea un archivo `.env` basado en `.env.example`:

```bash
cp .env.example .env
```

| Variable | Descripción | Valor por Defecto |
| :--- | :--- | :--- |
| `PDFENGINE_API_KEYS` | Claves Bearer autorizadas separadas por comas | `""` |
| `PDFENGINE_CORS_ORIGINS` | Orígenes HTTP permitidos para CORS | `http://localhost:3000` |
| `PDFENGINE_MAX_UPLOAD_BYTES` | Tamaño máximo de archivo por carga | `33554432` (32 MiB) |
| `PDFENGINE_MAX_SESSIONS` | Capacidad máxima de documentos en memoria | `32` |
| `PDFENGINE_MAX_RETAINED_BYTES` | Límite total de bytes retenidos en memoria | `268435456` (256 MiB) |
| `PDFENGINE_SESSION_TTL_SECONDS` | Tiempo de vida de sesión inactiva | `1800` (30 min) |

---

## Instalación y Desarrollo Local

```bash
# 1. Crear y activar entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Instalar la extensión nativa pdf_engine
# Opción A: Desde el repositorio local PDFEngine (modo editable)
pip install -e ../PDFEngine

# Opción B: Desde un wheel compilado
# pip install /ruta/a/pdf_engine-0.1.0-cp313-cp313-macosx_11_0_arm64.whl

# 4. Iniciar el servidor API
uvicorn app.main:app --reload --port 8000
```

La documentación interactiva OpenAPI / Swagger UI estará disponible en:
- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Pruebas de Integración y Calidad

Para ejecutar la suite completa de pruebas:

```bash
source .venv/bin/activate
pytest tests/ -v
```

---

## Despliegue con Docker

```bash
# Construir imagen Docker
docker build -t pdf-api:latest .

# Ejecutar contenedor
docker run -d -p 8000:8000 \
  -e PDFENGINE_API_KEYS="tu-clave-secreta-de-produccion" \
  -e PDFENGINE_CORS_ORIGINS="https://tu-estudio-web.com" \
  pdf-api:latest
```

---

## Licencia

Distribuido bajo la licencia MIT.
