# PII Redaction Service - Architecture Diagram

## System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT REQUEST                           │
│                  POST /redact-pii (image file)                  │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                         app.py (Flask)                           │
│  • Validate file upload                                          │
│  • Check file type and size                                      │
│  • Initialize service dependencies                               │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PiiRedactionService                            │
│               (Main Orchestrator Service)                        │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
         Step 1     │  Step 2    │  Step 3    │  Step 4
         Extract    │  Detect    │  Map PII   │  Redact
         Text       │  PII       │  to Words  │  Image
                    │            │            │
                    ▼            ▼            ▼
         ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
         │   Text       │  │  PII         │  │   Image      │
         │  Extraction  │  │  Detection   │  │  Redaction   │
         │   Service    │  │   Service    │  │   Service    │
         └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
                │                 │                 │
                ▼                 ▼                 │
         ┌──────────────┐  ┌──────────────┐        │
         │   Azure      │  │   Azure      │        │
         │  Document    │  │  Language    │        │
         │Intelligence  │  │   Service    │        │
         └──────────────┘  └──────────────┘        │
                │                 │                 │
                └─────────────────┴─────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                       REDACTED IMAGE (PNG)                       │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Application Layer                         │
├─────────────────────────────────────────────────────────────────┤
│  app.py                                                          │
│  • Flask route handlers                                          │
│  • Request validation                                            │
│  • Dependency injection                                          │
│  • Error handling                                                │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Service Layer                             │
├─────────────────────────────────────────────────────────────────┤
│  services/pii_redaction_service.py                               │
│  • Main orchestrator                                             │
│  • Coordinates workflow                                          │
│                                                                  │
│  services/text_extraction_service.py                             │
│  • Azure Document Intelligence client                            │
│  • OCR text extraction                                           │
│  • Word-level bounding boxes                                     │
│                                                                  │
│  services/pii_detection_service.py                               │
│  • PII provider coordination                                     │
│  • PII to word mapping                                           │
│  • Multi-word PII handling                                       │
│                                                                  │
│  services/image_redaction_service.py                             │
│  • Image manipulation with Pillow                                │
│  • Draw black rectangles                                         │
│  • PNG conversion                                                │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Provider Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  providers/azure_pii_detection_provider.py                       │
│  • Azure Language Service integration                            │
│  • PII entity recognition                                        │
│                                                                  │
│  providers/openai_pii_detection_provider.py                      │
│  • OpenAI GPT-4 integration                                      │
│  • Custom PII detection prompt                                   │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Model Layer                              │
├─────────────────────────────────────────────────────────────────┤
│  models/__init__.py                                              │
│  • BoundingBox - Rectangle coordinates                           │
│  • DocumentWord - Word + location + confidence                   │
│  • ImageRedactionResult - Output container                       │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Interface Layer                             │
├─────────────────────────────────────────────────────────────────┤
│  interfaces/__init__.py                                          │
│  • IPiiDetectionServiceProvider - Abstract interface             │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Detail

```
1. Image Upload
   ├─ Client sends multipart/form-data
   ├─ Flask validates file type & size
   └─ Image bytes extracted

2. Text Extraction
   ├─ Image bytes → Azure Document Intelligence
   ├─ OCR processing
   ├─ Returns: Full text + word locations
   └─ Each word has bounding box polygon

3. PII Detection
   ├─ Full text → PII Provider (Azure/OpenAI)
   ├─ AI analyzes text for PII entities
   ├─ Returns: List of PII strings
   └─ Examples: "4532 1234 5678 9012", "John Doe"

4. PII Mapping
   ├─ For each PII value:
   │  ├─ Split into components ("John Doe" → ["John", "Doe"])
   │  ├─ Find matching words in extracted words
   │  └─ Collect bounding boxes
   └─ Result: List of areas to redact

5. Image Redaction
   ├─ Open original image with Pillow
   ├─ For each redaction area:
   │  └─ Draw black filled rectangle
   ├─ Convert to PNG
   └─ Return redacted image bytes

6. Response
   └─ Send PNG file to client
```

## Class Relationships

```
PiiRedactionService
    │
    ├─── uses ──→ TextExtractionService
    │                  │
    │                  └─── uses ──→ Azure Document Intelligence SDK
    │
    ├─── uses ──→ PiiDetectionService
    │                  │
    │                  └─── uses ──→ IPiiDetectionServiceProvider
    │                                       │
    │                                       ├─ AzurePiiDetectionServiceProvider
    │                                       │       └─→ Azure Language SDK
    │                                       │
    │                                       └─ OpenAiPiiDetectionServiceProvider
    │                                               └─→ OpenAI SDK
    │
    └─── uses ──→ ImageRedactionService
                       │
                       └─── uses ──→ Pillow (PIL)
```

## Configuration Flow

```
.env file
    │
    ├─ AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT
    ├─ AZURE_DOCUMENT_INTELLIGENCE_KEY
    ├─ AZURE_LANGUAGE_ENDPOINT
    ├─ AZURE_LANGUAGE_KEY
    └─ OPENAI_API_KEY (optional)
    │
    ▼
config.py (Config class)
    │
    ├─ Loads from environment
    ├─ Validates required values
    └─ Provides to Flask app
    │
    ▼
app.py
    │
    └─ Injects into service constructors
```

## API Endpoints

```
┌─────────────────────────────────────────────────────────────────┐
│                      Flask Application                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  POST /redact-pii                                                │
│  ├─ Input: multipart/form-data with 'file' field                │
│  ├─ Accepts: png, jpg, jpeg, bmp, gif, tiff                     │
│  ├─ Max Size: 16 MB                                             │
│  ├─ Process: Extract → Detect → Map → Redact                    │
│  └─ Output: PNG image with PII redacted                         │
│                                                                  │
│  GET /health                                                     │
│  ├─ Returns: {"status": "healthy", "service": "..."}            │
│  └─ Use for monitoring/health checks                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Error Handling Flow

```
Request
    ↓
┌─────────────────────┐
│ Validation Errors   │ → 400 Bad Request
│ • No file           │
│ • Empty file        │
│ • Wrong file type   │
└─────────────────────┘
    ↓
┌─────────────────────┐
│ File Size Error     │ → 413 Payload Too Large
│ • File > 16 MB      │
└─────────────────────┘
    ↓
┌─────────────────────┐
│ Processing Errors   │ → 500 Internal Server Error
│ • Azure API errors  │   + Error details in JSON
│ • Image errors      │
│ • Network errors    │
└─────────────────────┘
    ↓
Success → 200 OK + PNG image
```

## Deployment Architecture

```
                    Internet
                       │
                       ▼
              ┌──────────────────┐
              │  Reverse Proxy   │
              │  (nginx/Apache)  │
              │  • HTTPS         │
              │  • Load Balance  │
              └─────────┬────────┘
                        │
                        ▼
              ┌──────────────────┐
              │   WSGI Server    │
              │   (Gunicorn)     │
              │   • Multiple     │
              │     Workers      │
              └─────────┬────────┘
                        │
                        ▼
              ┌──────────────────┐
              │  Flask App       │
              │  (app.py)        │
              └─────────┬────────┘
                        │
           ┌────────────┼────────────┐
           │            │            │
           ▼            ▼            ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │  Azure   │  │  Azure   │  │  OpenAI  │
    │Document  │  │Language  │  │   API    │
    │   Intel  │  │ Service  │  │(Optional)│
    └──────────┘  └──────────┘  └──────────┘
```

This architecture ensures:
- **Separation of Concerns**: Each layer has specific responsibility
- **Maintainability**: Easy to update individual components
- **Testability**: Services can be tested independently
- **Extensibility**: New PII providers can be added easily
- **Scalability**: Can run multiple workers for high traffic
