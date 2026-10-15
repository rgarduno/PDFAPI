"""Pydantic data models for the PDFEngine REST API.

Defines serialized representations for document metadata, layout scene graphs,
and surgical editing requests.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Bounding box coordinates in PDF page points."""
    min_x: float
    min_y: float
    max_x: float
    max_y: float
    width: float
    height: float


class ParagraphModel(BaseModel):
    """Extracted paragraph with typographic layout attributes."""
    id: int
    text: str
    bbox: BoundingBox
    alignment: str = Field(description="left, center, right, or justified")
    leading: float
    line_count: int
    font_size: float = 0
    font_family: str = ""
    font_weight: int = 400
    font_style: str = "normal"


class PageSceneGraph(BaseModel):
    """Complete layout scene graph for a page."""
    page_number: int
    paragraphs: List[ParagraphModel]


class PageOverviewItem(BaseModel):
    """Overview metadata and layout preview for a single page in thumbnail navigation."""
    page_number: int
    page_index: int
    rotation: int
    paragraph_count: int
    preview_snippet: str
    width: float = 612.0
    height: float = 792.0


class DocumentOverviewResponse(BaseModel):
    """One window of page summaries for thumbnail navigation.

    `pages` covers `[offset, offset + len(pages))`. `total_pages` is the
    document length. A client pages with `offset` instead of requesting
    every page in one call.
    """
    document_id: str
    filename: str
    total_pages: int
    offset: int = 0
    limit: int = 24
    pages: List[PageOverviewItem]


class DocumentUploadResponse(BaseModel):
    """Response returned upon successful document upload."""
    document_id: str
    filename: str
    page_count: int


class EditParagraphRequest(BaseModel):
    """Payload to perform an in-place surgical paragraph edit.

    Style fields are optional. When every style field is omitted, the edit
    keeps the current font, size, alignment, and leading and writes no color.
    """
    new_text: str
    font: Optional[str] = None
    size: Optional[float] = None
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    color: Optional[str] = None
    alignment: Optional[str] = None
    leading: Optional[float] = None


class EditParagraphResponse(BaseModel):
    """Response returned after surgical edit execution."""
    success: bool
    document_id: str
    page_number: int
    paragraph_id: int
    updated_text: str
    message: str
    font: Optional[str] = None
    size: Optional[float] = None
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    color: Optional[str] = None
    alignment: Optional[str] = None
    leading: Optional[float] = None


class TextBoxRequest(BaseModel):
    """Content-stream text drawn inside a rectangle.

    Style fields are optional. Omitted fields become Helvetica, 12 points,
    black, left, and a leading of 1.2 times the size. This is not a
    `/FreeText` annotation.
    """
    text: str
    x: float
    y: float
    width: float
    height: float
    font: Optional[str] = None
    size: Optional[float] = None
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    color: Optional[str] = None
    alignment: Optional[str] = None
    leading: Optional[float] = None


class TextBoxResponse(BaseModel):
    """Response returned after a text box is appended to the page content."""
    success: bool
    document_id: str
    page_number: int
    text: str
    font_resource: str
    base_font: str
    line_count: int


class ImageModel(BaseModel):
    """Extracted image XObject on a page with spatial layout attributes."""
    id: int
    name: str
    width_px: int
    height_px: int
    color_space: str
    bits_per_component: int
    filter: Optional[str] = None
    byte_size: int
    bbox: BoundingBox


class PageImagesResponse(BaseModel):
    """Response containing all extracted images on a page."""
    page_number: int
    images: List[ImageModel]
    count: int


class FormFieldModel(BaseModel):
    """Interactive AcroForm field definition."""
    id: int
    name: str
    alt_name: Optional[str] = None
    field_type: str
    value: str
    default_value: Optional[str] = None
    bbox: BoundingBox
    page_number: int
    options: List[str] = Field(default_factory=list)
    is_read_only: bool = False
    is_required: bool = False
    is_multiline: bool = False
    max_length: Optional[int] = None


class DocumentFormsResponse(BaseModel):
    """Response containing all extracted interactive form fields in the document."""
    document_id: str
    count: int
    fields: List[FormFieldModel]


class FillFormFieldRequest(BaseModel):
    """Request payload to fill a single form field."""
    name_or_id: str
    value: str


class BatchFillFormsRequest(BaseModel):
    """Request payload to fill multiple form fields by name in batch."""
    fields: dict[str, str]


class FillFormsResponse(BaseModel):
    """Response returned upon filling form fields."""
    success: bool
    document_id: str
    updated_count: int
    message: str


class FlattenFormsResponse(BaseModel):
    """Response returned upon permanently flattening form fields into page vectors."""
    success: bool
    document_id: str
    flattened_count: int
    message: str


class CreateFormFieldRequest(BaseModel):
    """Payload to create and place a new interactive form field on a page."""
    name: str
    field_type: str = Field(default="Text", description="Field type: Text, Checkbox, RadioButton, PushButton, Choice, Signature")
    min_x: float = Field(default=72.0)
    min_y: float = Field(default=700.0)
    max_x: float = Field(default=250.0)
    max_y: float = Field(default=724.0)
    value: Optional[str] = ""
    default_value: Optional[str] = None
    alt_name: Optional[str] = None
    options: Optional[List[str]] = None
    is_read_only: bool = False
    is_required: bool = False
    is_multiline: bool = False
    max_length: Optional[int] = None
    font_size: Optional[float] = 12.0


class CreateFormFieldResponse(BaseModel):
    """Response returned upon successfully creating an AcroForm field."""
    status: str = "ok"
    document_id: str
    field: FormFieldModel


class DeleteFormFieldResponse(BaseModel):
    """Response returned upon deleting an AcroForm field."""
    status: str = "ok"
    document_id: str
    deleted: bool
    field_name: str


class UpdateFormFieldRequest(BaseModel):
    """Payload to update an existing form field's geometry or properties."""
    min_x: Optional[float] = None
    min_y: Optional[float] = None
    max_x: Optional[float] = None
    max_y: Optional[float] = None
    alt_name: Optional[str] = None
    is_read_only: Optional[bool] = None
    is_required: Optional[bool] = None
    is_multiline: Optional[bool] = None


class UpdateFormFieldResponse(BaseModel):
    """Response returned upon updating an AcroForm field."""
    status: str = "ok"
    document_id: str
    field: FormFieldModel
    message: str


class DetectedFormFieldCandidateModel(BaseModel):
    """Candidate form field detected from vector graphics and labels."""
    candidate_id: int
    field_type: str = Field(description="Inferred field type: Text, Checkbox, Signature, Choice")
    suggested_name: str
    label: Optional[str] = None
    bbox: BoundingBox
    confidence: float = Field(ge=0.0, le=1.0, description="Detection confidence score")


class DetectFormFieldsResponse(BaseModel):
    """Response returned upon detecting form field candidates on a page."""
    document_id: str
    page_number: int
    total_candidates: int
    candidates: List[DetectedFormFieldCandidateModel]


class ApplyDetectedFormFieldItem(BaseModel):
    """Specific candidate field to apply as an interactive AcroForm widget."""
    candidate_id: Optional[int] = None
    suggested_name: Optional[str] = None
    field_type: str = Field(default="Text")
    min_x: float
    min_y: float
    max_x: float
    max_y: float
    label: Optional[str] = None
    confidence: Optional[float] = 1.0


class ApplyDetectedFormsRequest(BaseModel):
    """Payload to apply detected form field candidates."""
    candidates: Optional[List[ApplyDetectedFormFieldItem]] = Field(
        default=None,
        description="Explicit candidates to apply. If omitted or null, all detected candidates on page are applied.",
    )
    min_confidence: Optional[float] = Field(
        default=0.5,
        description="Minimum confidence threshold when auto-applying all detected candidates.",
    )


class ApplyDetectedFormsResponse(BaseModel):
    """Response returned upon converting candidates into interactive AcroForms."""
    success: bool
    document_id: str
    page_number: int
    created_fields_count: int
    fields: List[FormFieldModel]
    message: str


class RotatePageRequest(BaseModel):
    """Request payload to rotate a page."""
    degrees: int = Field(default=90, description="Degrees to rotate: 90, 180, 270, or relative offset")


class RotatePageResponse(BaseModel):
    """Response returned after page rotation."""
    success: bool
    document_id: str
    page_number: int
    new_rotation: int


class SplitDocumentRequest(BaseModel):
    """Request payload to extract or split pages from a document."""
    page_indices: Optional[List[int]] = None
    chunk_size: Optional[int] = None


class SplitDocumentResponse(BaseModel):
    """Response returned after splitting document."""
    success: bool
    source_document_id: str
    extracted_document_ids: List[str]
    count: int


class MergeDocumentsRequest(BaseModel):
    """Request payload to merge multiple documents into one."""
    document_ids: List[str] = Field(description="Ordered list of document IDs to merge")


class MergeDocumentsResponse(BaseModel):
    """Response returned after merging documents."""
    success: bool
    merged_document_id: str
    filename: str
    page_count: int


class ReorderPagesRequest(BaseModel):
    """Request payload to reorder pages in a document."""
    new_order: List[int] = Field(description="Permutation of 0-based or 1-based page indices")


class DeletePagesRequest(BaseModel):
    """Request payload to delete pages from a document."""
    page_indices: List[int] = Field(description="List of 0-based or 1-based page indices to delete")


class PageOperationResponse(BaseModel):
    """General response for page assembly/manipulation operations."""
    success: bool
    document_id: str
    page_count: int
    message: str


class InsertBlankPageRequest(BaseModel):
    """Insert an empty page. ``index`` is 0-based and may equal the page count."""
    index: int = Field(ge=0)
    width: float = Field(default=612, gt=0, le=14400)
    height: float = Field(default=792, gt=0, le=14400)


class DuplicatePageRequest(BaseModel):
    """Copy one page inside the same document. Both indexes are 0-based."""
    source_index: int = Field(ge=0)
    insert_at: int = Field(ge=0)


class InsertPagesRequest(BaseModel):
    """Copy pages from another session. Indexes in the body are 0-based."""
    source_doc_id: str
    source_indices: List[int] = Field(min_length=1, max_length=200)
    insert_at: int = Field(ge=0)


class SetPageBoxRequest(BaseModel):
    """Write or clear one page box. ``rect`` is ``[x0, y0, x1, y1]`` in points."""
    kind: str = Field(min_length=1, max_length=32)
    rect: Optional[List[float]] = None


class PageBoxesResponse(BaseModel):
    """The five ISO 32000-1 page boxes. ``page_index`` is 0-based."""
    document_id: str
    page_index: int
    page_number: int
    media: List[float]
    crop: Optional[List[float]] = None
    bleed: Optional[List[float]] = None
    trim: Optional[List[float]] = None
    art: Optional[List[float]] = None


class TextSearchRequest(BaseModel):
    """Search reconstructed paragraph text. The query is not stored."""
    query: str = Field(min_length=1, max_length=512)
    ignore_case: bool = True
    max_hits: int = Field(default=100, ge=1, le=500)


class TextSearchHitModel(BaseModel):
    """One match. Offsets count Unicode scalars in the paragraph."""
    page_index: int
    paragraph_id: int
    char_start: int
    char_end: int
    snippet: str
    min_x: float
    min_y: float
    max_x: float
    max_y: float


class TextSearchResponse(BaseModel):
    """Search hits. ``truncated`` means the hit cap stopped the scan."""
    document_id: str
    hit_count: int
    truncated: bool
    pages_skipped: List[int]
    hits: List[TextSearchHitModel]


class TextReplaceRequest(BaseModel):
    """Replace reconstructed paragraph text. The query and replacement are not stored."""
    query: str = Field(min_length=1, max_length=512)
    replacement: str = Field(default="", max_length=4000)
    ignore_case: bool = True
    max_hits: int = Field(default=100, ge=1, le=500)


class TextReplaceResponse(BaseModel):
    """Counts for one replace. ``truncated`` means the hit cap stopped the scan."""
    document_id: str
    replacements: int
    paragraphs: int
    paragraphs_on_standard_face: int
    truncated: bool
    pages_skipped: List[int]


class AnnotationModel(BaseModel):
    """Structured representation of a PDF annotation."""
    id: int
    page_index: int
    page_number: int
    subtype: str
    bbox: BoundingBox
    color: Optional[List[float]] = None
    opacity: float = 1.0
    contents: Optional[str] = None
    link_type: Optional[str] = None
    link_uri: Optional[str] = None
    link_target_page: Optional[int] = None
    stamp_type: Optional[str] = None
    date_str: Optional[str] = None
    border_width: float = 1.0
    fill_color: Optional[List[float]] = None
    points: List[List[float]] = []
    line_ending: Optional[str] = None


class PageAnnotationsResponse(BaseModel):
    """Response containing annotations on a given page."""
    document_id: str
    page_number: int
    count: int
    annotations: List[AnnotationModel]


class AddMarkupRequest(BaseModel):
    """Request payload to add a text markup annotation (Highlight, Underline, StrikeOut)."""
    subtype: str = Field(default="Highlight", description="Highlight, Underline, or StrikeOut")
    min_x: float
    min_y: float
    max_x: float
    max_y: float
    color: Optional[List[float]] = None
    opacity: Optional[float] = None
    contents: Optional[str] = None


class AddLinkRequest(BaseModel):
    """Request payload to add an interactive clickable link or GoTo destination."""
    min_x: float
    min_y: float
    max_x: float
    max_y: float
    uri: Optional[str] = None
    target_page: Optional[int] = None
    show_border: bool = False


class AddShapeRequest(BaseModel):
    """Ink stroke or vector shape. Arrow is a line with an open arrow ending."""
    kind: str
    points: List[List[float]]
    stroke: List[float]
    fill: Optional[List[float]] = None
    line_width: float = 1.5
    opacity: float = 1.0


class AddStampRequest(BaseModel):
    """Request payload to add a rubber stamp annotation."""
    stamp_type: str = Field(default="Approved", description="Approved, Confidential, Draft, Rejected, Final, TopSecret, or Custom")
    min_x: Optional[float] = None
    min_y: Optional[float] = None
    max_x: Optional[float] = None
    max_y: Optional[float] = None
    custom_text: Optional[str] = None
    color: Optional[List[float]] = None
    date_str: Optional[str] = None


class OcrRequest(BaseModel):
    """Selects the local tesseract traineddata name. Empty uses eng."""
    language: Optional[str] = None


class OcrResponse(BaseModel):
    """Counts for a searchable-text pass. Recognized words are not included."""
    success: bool
    document_id: str
    pages_seen: int
    pages_recognized: int
    words_inserted: int
    message: str


class PdfARequest(BaseModel):
    """Archive part. Only `1b` and `2b` are accepted."""
    part: str


class PdfAResponse(BaseModel):
    """Archive conversion or structural check. Issues are stable sentences."""
    success: bool
    document_id: str
    part: str
    conformance: str
    issues: List[str]
    message: str


class AnnotationActionResponse(BaseModel):
    """Response returned upon creating or modifying an annotation."""
    success: bool
    document_id: str
    page_number: int
    annotation_id: int
    message: str


class FlattenAnnotationsResponse(BaseModel):
    """Response returned upon flattening visual annotations into page vectors."""
    success: bool
    document_id: str
    flattened_count: int
    message: str


class AddPaginationRequest(BaseModel):
    """Request payload to apply dynamic pagination, headers, or footers."""
    format: Optional[str] = Field(default="Página {page} de {total}", description="Format template with {page} and {total}")
    position: Optional[str] = Field(default="bottom_center", description="top_left, top_center, top_right, bottom_left, bottom_center, bottom_right")
    font_size: Optional[float] = Field(default=9.0, description="Font size in points")
    color: Optional[List[float]] = Field(default=[0.35, 0.35, 0.35], description="RGB color array [r, g, b] in [0.0, 1.0]")
    margin: Optional[float] = Field(default=36.0, description="Margin distance from page edge")
    start_page_num: Optional[int] = Field(default=1, description="Starting page count number")
    skip_first_page: Optional[bool] = Field(default=False, description="Whether to omit numbering on first page")
    page_indices: Optional[List[int]] = Field(default=None, description="Specific 0-based page indices or null for all")


class AddTextWatermarkRequest(BaseModel):
    """Request payload to apply a semi-transparent text watermark."""
    text: str = Field(default="CONFIDENCIAL", description="Watermark text")
    font_size: Optional[float] = Field(default=52.0, description="Font size in points")
    color: Optional[List[float]] = Field(default=[0.80, 0.20, 0.20], description="RGB color array [r, g, b]")
    opacity: Optional[float] = Field(default=0.22, description="Alpha opacity between 0.0 and 1.0")
    rotation_degrees: Optional[float] = Field(default=45.0, description="Rotation angle in degrees")
    placement: Optional[str] = Field(default="background", description="background or foreground")
    page_indices: Optional[List[int]] = Field(default=None, description="Specific 0-based page indices or null for all")


class WatermarkActionResponse(BaseModel):
    """Response returned upon applying pagination or watermarks."""
    success: bool
    document_id: str
    affected_pages: int
    message: str


class RedactionRegionItem(BaseModel):
    """Spatial bounding box rectangle for redaction."""
    min_x: float
    min_y: float
    max_x: float
    max_y: float


class RedactRegionsRequest(BaseModel):
    """Request payload to redact specific rectangular areas on a page."""
    page_number: int = Field(default=1, description="Target 1-based page number")
    regions: List[RedactionRegionItem] = Field(description="Bounding boxes to redact")
    fill_color: Optional[List[float]] = Field(default=[0.0, 0.0, 0.0], description="RGB fill color [r, g, b]")
    overlay_text: Optional[str] = Field(default="[REDACTADO]", description="Overlay label centered on blackout box")
    text_color: Optional[List[float]] = Field(default=[1.0, 1.0, 1.0], description="RGB overlay text color [r, g, b]")
    font_size: Optional[float] = Field(default=None, description="Font size or auto-calculated if None")
    prune_annotations: Optional[bool] = Field(default=True, description="Remove intersecting link and markup annotations")


class RedactPatternRequest(BaseModel):
    """Request payload to scan and redact sensitive PII patterns across pages."""
    pattern_type: str = Field(default="email", description="email, phone, ssn, credit_card, rfc, curp, text")
    custom_query: Optional[str] = Field(default=None, description="Search query if pattern_type is text")
    case_sensitive: Optional[bool] = Field(default=False, description="Case-sensitive matching")
    page_numbers: Optional[List[int]] = Field(default=None, description="1-based page numbers or null for all")
    fill_color: Optional[List[float]] = Field(default=[0.0, 0.0, 0.0], description="RGB fill color [r, g, b]")
    overlay_text: Optional[str] = Field(default="[REDACTADO]", description="Overlay label centered on blackout box")
    text_color: Optional[List[float]] = Field(default=[1.0, 1.0, 1.0], description="RGB overlay text color [r, g, b]")
    font_size: Optional[float] = Field(default=None, description="Font size or auto-calculated if None")
    prune_annotations: Optional[bool] = Field(default=True, description="Remove intersecting link and markup annotations")
    scrub_metadata: Optional[bool] = Field(default=False, description="Scrub Info dictionary and XMP metadata")


class RedactTextRequest(BaseModel):
    """Request payload to redact exact text occurrences."""
    query: str = Field(description="Search text to excise and redact")
    case_sensitive: Optional[bool] = Field(default=False, description="Case-sensitive search")
    page_numbers: Optional[List[int]] = Field(default=None, description="1-based page numbers or null for all")
    fill_color: Optional[List[float]] = Field(default=[0.0, 0.0, 0.0], description="RGB fill color [r, g, b]")
    overlay_text: Optional[str] = Field(default="[REDACTADO]", description="Overlay label centered on blackout box")
    text_color: Optional[List[float]] = Field(default=[1.0, 1.0, 1.0], description="RGB overlay text color [r, g, b]")
    font_size: Optional[float] = Field(default=None, description="Font size or auto-calculated if None")
    prune_annotations: Optional[bool] = Field(default=True, description="Remove intersecting link and markup annotations")


class SanitizeDocumentRequest(BaseModel):
    """Request payload to purge sensitive metadata from the document."""
    scrub_metadata: Optional[bool] = Field(default=True, description="Wipe Author, Title, Creator, and XMP Metadata")


class RedactionSummaryModel(BaseModel):
    """Summary of redaction results per page."""
    page_number: int
    purged_glyphs_count: int
    modified_blocks_count: int
    blackout_boxes_count: int
    pruned_annotations_count: int
    applied_rects: List[List[float]]


class RedactionActionResponse(BaseModel):
    """Response returned upon applying redactions."""
    success: bool
    document_id: str
    total_purged_glyphs: int
    total_blackout_boxes: int
    total_pruned_annotations: int
    summaries: List[RedactionSummaryModel]
    message: str


class SanitizeDocumentResponse(BaseModel):
    """Response returned upon sanitizing document metadata."""
    success: bool
    document_id: str
    modified: bool
    message: str


class PermissionsModel(BaseModel):
    """Bits stored in the encryption dictionary `/P` entry. This process does not enforce them."""
    print_low_res: bool = True
    print_high_res: bool = True
    modify_contents: bool = True
    copy_extract: bool = True
    modify_annotations: bool = True
    fill_forms: bool = True
    accessibility_extract: bool = True
    assemble_document: bool = True


class EncryptDocumentRequest(BaseModel):
    """Request payload to encrypt document with AES-128 or AES-256 and password protection."""
    user_password: str = Field(default="", description="Password required to open and read document")
    owner_password: str = Field(min_length=1, description="Owner password required to change permissions. No default is applied.")
    permissions: Optional[PermissionsModel] = Field(default=None, description="Bits stored in /P. This process does not enforce them.")
    encrypt_metadata: Optional[bool] = Field(default=True, description="Whether to encrypt metadata stream")
    algorithm: Optional[str] = Field(default="aes128", description="Encryption algorithm: 'aes128' (Rev 4), 'aes256' (Rev 6), or 'aes256-r5' (Rev 5)")


class DecryptDocumentRequest(BaseModel):
    """Request payload to remove encryption from a document."""
    password: str = Field(description="User or Owner password to decrypt the document")


class SignDocumentRequest(BaseModel):
    """Stamp a SHA-256 attestation, or a detached PKCS#7 signature when a certificate is supplied.

    PKCS#7 verification checks the certificate inside the CMS. It does not decide trust.
    """
    signer_name: str = Field(default="PDFEngine Certified Signer", description="Name stored in /Name. This does not prove identity.")
    reason: str = Field(default="Integridad del archivo", description="Note stored in /Reason")
    location: str = Field(default="Ciudad de México, MX", description="Physical or corporate signing location")
    page_number: int = Field(default=1, description="1-based page number where signature badge will appear")
    rect: Optional[List[float]] = Field(default=None, description="[min_x, min_y, max_x, max_y] bounding box or default placement")
    contact_info: Optional[str] = Field(default=None, description="Optional contact email or URL")
    certificate_pem: Optional[str] = Field(default=None, description="PEM X.509 certificate. With private_key_pem, writes a detached PKCS#7 signature.")
    private_key_pem: Optional[str] = Field(default=None, description="PEM PKCS#8 or PKCS#1 private key. Encrypted PEM is rejected.")
    chain_pem: Optional[str] = Field(default=None, description="Optional extra PEM certificates stored beside the leaf. They are not a trust path.")
    pkcs12_base64: Optional[str] = Field(default=None, description="Base64 PKCS#12 or PFX. Mutually exclusive with the PEM fields.")
    pkcs12_password: Optional[str] = Field(default=None, description="Password for pkcs12_base64. An empty string is a supplied password.")
    tsa_url: Optional[str] = Field(default=None, description="HTTPS RFC 3161 time-stamping authority. Requires a certificate and private key.")


class SignatureModel(BaseModel):
    """One signature dictionary and its integrity check.

    contents_hex is the SHA-256 digest for PDFEngine.sha256, and the CMS bytes
    (including zero padding) for adbe.pkcs7.detached. byte_range_valid checks
    that CMS against the certificate embedded in it. It is not a trust decision.
    """
    field_name: str
    signer_name: str
    reason: str
    location: str
    date: str
    sub_filter: str
    byte_range: List[int]
    contents_hex: str
    byte_range_valid: bool
    rect: List[float]
    page_number: int


class SecurityStatusResponse(BaseModel):
    """Encryption state plus each signature integrity check."""
    document_id: str
    is_encrypted: bool
    encryption_algorithm: Optional[str] = None
    signatures: List[SignatureModel]


class SecurityActionResponse(BaseModel):
    """Generic action response for security operations."""
    success: bool
    document_id: str
    message: str
    is_encrypted: Optional[bool] = None
    encryption_algorithm: Optional[str] = None
    signature: Optional[SignatureModel] = None


class TableCellModel(BaseModel):
    """A single cell inside an extracted table."""
    row: int
    col: int
    row_span: int = 1
    col_span: int = 1
    text: str
    is_header: bool = False
    bbox: BoundingBox


class TableModel(BaseModel):
    """A structured table extracted from a page."""
    table_idx: int
    page_number: int
    row_count: int
    col_count: int
    bbox: BoundingBox
    headers: List[str]
    rows: List[List[str]]
    cells: List[TableCellModel]


class PageTablesResponse(BaseModel):
    """Response containing all tables detected on a page."""
    document_id: str
    page_number: int
    total_tables: int
    tables: List[TableModel]


class TableExportResponse(BaseModel):
    """Response containing the formatted export content of a table."""
    document_id: str
    page_number: int
    table_idx: int
    format: str
    content: str
    row_count: int
    col_count: int


class OptimizeRequest(BaseModel):
    """Request payload to optimize document size and compress streams."""
    remove_unused: bool = Field(default=True, description="Eliminate unreferenced orphaned objects (Garbage Collection)")
    pack_object_streams: bool = Field(default=True, description="Pack indirect objects into compressed /ObjStm streams (PDF 1.5+)")
    recompress_flate: bool = Field(default=True, description="Recompress streams using optimal Flate (Zlib Best)")
    deduplicate_streams: bool = Field(default=True, description="Deduplicate identical streams and consolidate references")
    max_objects_per_stream: int = Field(default=100, description="Max indirect objects per /ObjStm container")


class OptimizeResponse(BaseModel):
    """Response containing optimization results and quantitative metrics."""
    success: bool
    document_id: str
    original_size: int
    optimized_size: int
    bytes_saved: int
    compression_ratio_pct: float
    objects_removed: int
    streams_recompressed: int
    object_streams_created: int
    streams_deduplicated: int
    message: str


class AuditEventResponse(BaseModel):
    """One entry from the caller's action log.

    The log names the action, the document, and the time. It does not carry
    file bytes, the upload name, a password, or a bearer token.
    """
    action: str
    document_id: str
    at: str


class SystemCapabilitiesResponse(BaseModel):
    """System capabilities, runtime tools, and format support."""
    tesseract_available: bool = Field(description="True if local tesseract binary was located")
    tesseract_path: Optional[str] = Field(default=None, description="Absolute path to the tesseract executable")
    ocr_languages: List[str] = Field(default_factory=list, description="Available tesseract language models")
    pdfa_supported: bool = Field(default=True, description="PDF/A-1b and PDF/A-2b conversion support")
    pkcs7_supported: bool = Field(default=True, description="Detached PKCS#7 & RFC 3161 support")
    concurrency_locks: bool = Field(default=True, description="Per-document concurrency serialization active")


class DocumentMetadataModel(BaseModel):
    """Document metadata properties synchronized between /Info and XMP."""
    title: Optional[str] = Field(default=None, description="Document title (/Title, dc:title)")
    author: Optional[str] = Field(default=None, description="Primary author (/Author, dc:creator)")
    subject: Optional[str] = Field(default=None, description="Subject or description (/Subject, dc:description)")
    keywords: Optional[str] = Field(default=None, description="Keywords (/Keywords, pdf:Keywords)")
    creator: Optional[str] = Field(default=None, description="Creating application (/Creator, xmp:CreatorTool)")
    producer: Optional[str] = Field(default=None, description="PDF producer (/Producer, pdf:Producer)")
    creation_date: Optional[str] = Field(default=None, description="Creation timestamp in ISO-8601 or PDF format")
    mod_date: Optional[str] = Field(default=None, description="Modification timestamp in ISO-8601 or PDF format")


class DocumentMetadataResponse(BaseModel):
    """Response containing synchronized document metadata."""
    success: bool = True
    document_id: str
    metadata: DocumentMetadataModel


class UpdateDocumentMetadataRequest(BaseModel):
    """Payload to update document metadata across /Info and XMP."""
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    keywords: Optional[str] = None
    creator: Optional[str] = None
    producer: Optional[str] = None
    creation_date: Optional[str] = None
    mod_date: Optional[str] = None


class WordDiffModel(BaseModel):
    """Token-level word diff within a modified text item."""
    kind: str
    text: str


class TextDiffItemModel(BaseModel):
    """Textual discrepancy between base and target."""
    kind: str
    base_text: Optional[str] = None
    target_text: Optional[str] = None
    base_bbox: Optional[List[float]] = None
    target_bbox: Optional[List[float]] = None
    word_diffs: List[WordDiffModel] = []


class ImageDiffItemModel(BaseModel):
    """Image discrepancy between base and target."""
    kind: str
    resource_name: str
    base_bbox: Optional[List[float]] = None
    target_bbox: Optional[List[float]] = None
    base_dimensions: Optional[List[int]] = None
    target_dimensions: Optional[List[int]] = None


class PageDimensionsModel(BaseModel):
    """Page boundary dimensions in points."""
    width: float
    height: float


class PageDiffModel(BaseModel):
    """Page-level comparison result."""
    page_number_base: Optional[int] = None
    page_number_target: Optional[int] = None
    kind: str
    base_dimensions: Optional[PageDimensionsModel] = None
    target_dimensions: Optional[PageDimensionsModel] = None
    dimensions_changed: bool = False
    text_diffs: List[TextDiffItemModel] = []
    image_diffs: List[ImageDiffItemModel] = []


class MetadataDiffItemModel(BaseModel):
    """Discrepancy in metadata fields."""
    field: str
    base_value: Optional[str] = None
    target_value: Optional[str] = None


class DiffSummaryModel(BaseModel):
    """Quantitative summary of document differences."""
    base_page_count: int
    target_page_count: int
    total_pages_with_changes: int
    text_additions: int
    text_deletions: int
    text_modifications: int
    image_additions: int
    image_deletions: int
    image_modifications: int
    metadata_changes: int


class CompareDocumentsRequest(BaseModel):
    """Request payload to compare the base document with a target document revision."""
    target_doc_id: str = Field(description="Document ID of the comparison target revision")
    ignore_case: bool = Field(default=False, description="Whether to ignore character casing")
    similarity_threshold: float = Field(default=0.35, description="Similarity score threshold for paragraph matching")
    compare_images: bool = Field(default=True, description="Whether to detect image additions, deletions and modifications")
    compare_metadata: bool = Field(default=True, description="Whether to compare document metadata fields")


class CompareDocumentsResponse(BaseModel):
    """Comprehensive comparison report between base and target document."""
    base_doc_id: str
    target_doc_id: str
    is_identical: bool
    summary: DiffSummaryModel
    metadata_diffs: List[MetadataDiffItemModel] = []
    pages: List[PageDiffModel] = []


class OutlineItemModel(BaseModel):
    """Hierarchical bookmark / Table of Contents item (ISO 32000-1 §12.3.3)."""
    title: str = Field(min_length=1, description="Display title of the bookmark")
    page_number: Optional[int] = Field(default=None, description="1-based target page number")
    top: Optional[float] = Field(default=None, description="Optional vertical Y coordinate on target page")
    left: Optional[float] = Field(default=None, description="Optional horizontal X coordinate on target page")
    zoom: Optional[float] = Field(default=None, description="Optional zoom factor on target page")
    uri: Optional[str] = Field(default=None, description="Optional external http/https URL")
    is_open: bool = Field(default=True, description="Whether child bookmarks are expanded by default")
    bold: bool = Field(default=False, description="Bold title text")
    italic: bool = Field(default=False, description="Italic title text")
    color: Optional[List[float]] = Field(default=None, description="Optional RGB color [r, g, b] in [0.0, 1.0]")
    children: List["OutlineItemModel"] = Field(default_factory=list, description="Nested child bookmarks")


OutlineItemModel.model_rebuild()


class DocumentOutlinesResponse(BaseModel):
    """Response containing the document's Table of Contents / Bookmarks hierarchy."""
    success: bool = True
    document_id: str
    total_items: int
    outlines: List[OutlineItemModel]


class UpdateOutlinesRequest(BaseModel):
    """Request payload to replace the document's Table of Contents / Bookmarks tree."""
    outlines: List[OutlineItemModel] = Field(default_factory=list, description="Root-level outline items")


class AddOutlineItemRequest(BaseModel):
    """Request payload to append a single bookmark node at root or under parent_indices."""
    item: OutlineItemModel
    parent_indices: Optional[List[int]] = Field(default=None, description="0-based index path to parent node, or null for root")


class EmbeddedAttachmentInfoModel(BaseModel):
    """Metadata describing an embedded file attachment (ISO 32000-1 §7.11.4)."""
    name: str = Field(description="Logical key in the /EmbeddedFiles name tree")
    filename: str = Field(description="Resolved filename from /UF or /F")
    mime_type: str = Field(description="MIME type from /Subtype")
    size: int = Field(description="Uncompressed byte size of the embedded payload")
    description: Optional[str] = Field(default=None, description="Optional description from /Desc")
    creation_date: Optional[str] = Field(default=None, description="Optional creation timestamp")
    modification_date: Optional[str] = Field(default=None, description="Optional modification timestamp")
    checksum_md5: Optional[str] = Field(default=None, description="Lowercase hex MD5 digest")
    checksum_sha256: str = Field(description="Lowercase hex SHA-256 digest of the payload")
    source: str = Field(description="Origin: 'embedded_files' or 'page_annotation'")
    page_number: Optional[int] = Field(default=None, description="1-based page number if attached via page annotation")


class DocumentAttachmentsResponse(BaseModel):
    """Response listing all embedded file attachments in a document."""
    success: bool = True
    document_id: str
    total_attachments: int
    attachments: List[EmbeddedAttachmentInfoModel]


class AddAttachmentRequest(BaseModel):
    """Request payload to embed a file into the document's /Names /EmbeddedFiles tree."""
    name: str = Field(min_length=1, max_length=255, description="Attachment filename")
    content_base64: str = Field(min_length=1, description="Base64-encoded binary content of the file")
    mime_type: Optional[str] = Field(default="application/octet-stream", description="MIME type of the attachment")
    description: Optional[str] = Field(default=None, description="Optional human-readable description")


class ExtractedAttachmentResponse(BaseModel):
    """Response containing extracted attachment metadata and base64-encoded payload."""
    success: bool = True
    document_id: str
    attachment: EmbeddedAttachmentInfoModel
    content_base64: str


class DeleteAttachmentResponse(BaseModel):
    """Response confirming deletion of an embedded attachment."""
    success: bool = True
    document_id: str
    deleted: bool
    name: str


class OptionalContentLayerModel(BaseModel):
    """Represents an Optional Content Group (/Type /OCG — PDF Layer, ISO 32000-1 §8.11)."""
    id: str = Field(description="Stable layer identifier (e.g. 'ocg_12')")
    object_number: int = Field(description="Underlying PDF COS object number")
    name: str = Field(description="Human-readable layer name (/Name)")
    visible: bool = Field(description="Current visibility state (ON=True, OFF=False)")
    intent: List[str] = Field(default_factory=list, description="Intended usage contexts (e.g. ['View', 'Design'])")
    locked: bool = Field(default=False, description="Whether the layer is locked in UI (/Locked)")


class DocumentLayersResponse(BaseModel):
    """Response listing all Optional Content Groups (OCG Layers) in a document."""
    success: bool = True
    document_id: str
    total_layers: int
    layers: List[OptionalContentLayerModel]


class AddLayerRequest(BaseModel):
    """Request payload to create a new Optional Content Group (/Type /OCG) in the document."""
    name: str = Field(min_length=1, max_length=255, description="Human-readable layer name")
    visible: bool = Field(default=True, description="Initial visibility state (True=ON, False=OFF)")
    intent: Optional[List[str]] = Field(default=None, description="Optional usage intents, e.g. ['View', 'Design']")
    locked: bool = Field(default=False, description="Whether the layer is locked in viewer UI")
    page_number: Optional[int] = Field(default=None, ge=1, description="Optional 1-based page number to bind a /Resources /Properties key")
    property_name: Optional[str] = Field(default=None, description="Optional property tag name (e.g. 'L1' or 'MC0') to bind on page_number")


class ToggleLayerRequest(BaseModel):
    """Request payload to toggle the visibility (ON/OFF) of an Optional Content Group."""
    target: str = Field(min_length=1, description="Layer ID (e.g. 'ocg_12') or exact layer name")
    visible: bool = Field(description="New visibility state (True=ON, False=OFF)")


class DeleteLayerResponse(BaseModel):
    """Response confirming deletion of an Optional Content Group (/Type /OCG)."""
    success: bool = True
    document_id: str
    deleted: bool
    target: str


class HardFlattenRequest(BaseModel):
    """Request payload to permanently flatten interactive forms, annotations, stamps, and shapes."""
    page_numbers: Optional[List[int]] = Field(
        default=None,
        description="Optional list of 1-based page numbers to flatten. If null, flattens the entire document.",
    )


class HardFlattenResponse(BaseModel):
    """Response summarizing permanent hard-flattening (burn-in) metrics."""
    success: bool = True
    document_id: str
    pages_flattened: int
    forms_flattened: int
    annotations_flattened: int
    appearance_streams_compiled: int
    objects_purged: int
    message: str


class MarkdownExportResponse(BaseModel):
    """Response containing the reconstructed GitHub-Flavored Markdown for an entire document."""
    document_id: str
    format: str = "markdown"
    content: str


class StructureElementModel(BaseModel):
    """Logical structure element (/StructElem) in the PDF/UA accessibility tree."""
    struct_type: str
    title: Optional[str] = None
    alt_text: Optional[str] = None
    actual_text: Optional[str] = None
    lang: Optional[str] = None
    page_number: Optional[int] = None
    mcids: List[int] = Field(default_factory=list)
    children: List["StructureElementModel"] = Field(default_factory=list)


StructureElementModel.model_rebuild()


class PdfUaValidationIssueModel(BaseModel):
    """Single ISO 14289-1 (PDF/UA-1) accessibility validation finding."""
    code: str
    description: str
    clause: str


class PdfUaTaggingRequest(BaseModel):
    """Request payload for automatic ISO 14289-1 (PDF/UA-1) semantic structure tagging."""
    lang: str = Field(
        default="en-US",
        min_length=2,
        max_length=32,
        description="Primary natural language BCP-47 tag (e.g. 'en-US', 'es-MX').",
    )
    title: Optional[str] = Field(
        default=None,
        max_length=512,
        description="Optional document title override for /Info /Title and XMP dc:title.",
    )
    figure_alt_fallback: str = Field(
        default="Document figure or illustration",
        max_length=512,
        description="Fallback /Alt description for /Figure structure elements.",
    )


class PdfUaReportResponse(BaseModel):
    """Response containing the ISO 14289-1 (PDF/UA-1) accessibility inspection and structure tree."""
    success: bool = True
    document_id: str
    is_compliant: bool
    is_tagged: bool
    lang: Optional[str] = None
    title: Optional[str] = None
    display_doc_title: bool
    has_pdfua_xmp: bool
    role_map: dict[str, str] = Field(default_factory=dict)
    total_elements: int
    elements: List[StructureElementModel] = Field(default_factory=list)
    issues: List[PdfUaValidationIssueModel] = Field(default_factory=list)



