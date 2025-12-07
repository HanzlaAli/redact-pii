# Python PII Redaction Project - File Index

## Quick Navigation

### 📚 Documentation
- **[README.md](README.md)** - Main documentation with full API reference
- **[SETUP.md](SETUP.md)** - Quick setup guide (START HERE)
- **[SUMMARY.md](SUMMARY.md)** - Project overview and conversion summary
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Architecture diagrams and flow charts
- **[COMPARISON.md](COMPARISON.md)** - Side-by-side C# vs Python comparison

### 🚀 Getting Started Files
- **[start.py](start.py)** - Quick start script (automatic setup)
- **[.env.example](.env.example)** - Environment variables template
- **[requirements.txt](requirements.txt)** - Python dependencies

### 🔧 Core Application
- **[app.py](app.py)** - Flask application and API endpoints
- **[config.py](config.py)** - Configuration management

### 📦 Services Layer
- **[services/pii_redaction_service.py](services/pii_redaction_service.py)** - Main orchestrator
- **[services/text_extraction_service.py](services/text_extraction_service.py)** - OCR/text extraction
- **[services/pii_detection_service.py](services/pii_detection_service.py)** - PII coordination
- **[services/image_redaction_service.py](services/image_redaction_service.py)** - Image manipulation

### 🔌 Providers
- **[providers/azure_pii_detection_provider.py](providers/azure_pii_detection_provider.py)** - Azure Language Service
- **[providers/openai_pii_detection_provider.py](providers/openai_pii_detection_provider.py)** - OpenAI GPT-4

### 📊 Models & Interfaces
- **[models/__init__.py](models/__init__.py)** - Data models (BoundingBox, DocumentWord, etc.)
- **[interfaces/__init__.py](interfaces/__init__.py)** - Abstract interfaces

### 🧪 Testing & Tools
- **[test_api.py](test_api.py)** - API testing script
- **[pii-redaction-python.postman_collection.json](pii-redaction-python.postman_collection.json)** - Postman collection

### ⚙️ Configuration
- **[.env.example](.env.example)** - Environment variables template (copy to `.env`)
- **[.gitignore](.gitignore)** - Git ignore rules

---

## File Descriptions

### Documentation Files

#### README.md (Main Documentation)
Complete documentation including:
- Features and how it works
- Installation instructions
- API reference
- Configuration guide
- Usage examples
- Deployment guide
- Troubleshooting

#### SETUP.md (Quick Setup)
Step-by-step setup for:
- Creating virtual environment
- Installing dependencies
- Configuring Azure credentials
- Running the application
- Testing the API

#### SUMMARY.md (Project Overview)
- Conversion summary
- Key files created
- Dependencies comparison
- Setup instructions
- Cost considerations

#### ARCHITECTURE.md (Architecture)
- System flow diagrams
- Component architecture
- Data flow details
- Class relationships
- Deployment architecture

#### COMPARISON.md (C# vs Python)
- Side-by-side code comparison
- Language feature differences
- Framework comparisons
- When to use which version

---

## Core Application Files

### app.py
**Purpose**: Flask web application and API endpoints

**Key Functions**:
- `redact_pii()` - POST endpoint for image redaction
- `health_check()` - GET endpoint for health checks
- `get_redaction_service()` - Service factory
- `allowed_file()` - File validation

**Dependencies**: Flask, services, providers, config

### config.py
**Purpose**: Configuration management

**Key Components**:
- `Config` class with all settings
- Environment variable loading
- Configuration validation
- File upload limits

---

## Services Layer

### services/pii_redaction_service.py
**Purpose**: Main orchestrator service

**Key Method**: `redact_pii(source_image_bytes)` 
- Coordinates entire workflow
- Calls other services in sequence
- Returns redacted image

**Dependencies**: All other services

### services/text_extraction_service.py
**Purpose**: Text extraction using Azure Document Intelligence

**Key Method**: `extract_text_from_image(image_bytes)`
- OCR text extraction
- Word-level bounding boxes
- Returns full text + word locations

**Azure SDK**: azure-ai-formrecognizer

### services/pii_detection_service.py
**Purpose**: PII detection coordination

**Key Methods**:
- `extract_pii(text_content)` - Detect PII entities
- `get_words_containing_pii()` - Map PII to words

**Dependencies**: PII detection provider

### services/image_redaction_service.py
**Purpose**: Image manipulation

**Key Method**: `redact_image(image_bytes, redaction_areas)`
- Draws black rectangles over PII
- Converts to PNG
- Returns redacted image bytes

**Image Library**: Pillow (PIL)

---

## Provider Layer

### providers/azure_pii_detection_provider.py
**Purpose**: PII detection using Azure Language Service

**Key Method**: `detect_pii(text_content)`
- Calls Azure Language Service
- Recognizes PII entities
- Returns list of PII strings

**Azure SDK**: azure-ai-textanalytics

### providers/openai_pii_detection_provider.py
**Purpose**: PII detection using OpenAI GPT-4

**Key Method**: `detect_pii(text_content)`
- Calls OpenAI API
- Uses custom prompt for PII detection
- Parses response for PII entities

**API**: OpenAI GPT-4

---

## Models & Interfaces

### models/__init__.py
**Data Classes**:
- `BoundingBox` - Rectangle coordinates (x, y, width, height)
- `DocumentWord` - Word content + bounding box + confidence
- `ImageRedactionResult` - Output container (bytes + content type)

### interfaces/__init__.py
**Abstract Classes**:
- `IPiiDetectionServiceProvider` - Interface for PII providers
  - `detect_pii(text_content)` - Abstract method

---

## Testing & Tools

### test_api.py
**Purpose**: API testing script

**Usage**:
```bash
python test_api.py path/to/image.png
python test_api.py image.png http://localhost:5000
```

**Tests**:
1. Health endpoint
2. Redaction endpoint
3. Saves output image

### start.py
**Purpose**: Automated setup and start script

**Features**:
- Checks Python version
- Creates .env from template
- Installs dependencies
- Offers to start server

**Usage**:
```bash
python start.py
```

### pii-redaction-python.postman_collection.json
**Purpose**: Postman API collection

**Endpoints Included**:
1. Health Check (GET /health)
2. Redact PII (POST /redact-pii)

**Usage**: Import into Postman

---

## Configuration Files

### .env.example
**Purpose**: Environment variables template

**Variables**:
- Azure Document Intelligence (endpoint + key)
- Azure Language Service (endpoint + key)
- OpenAI API key (optional)
- Flask settings

**Setup**: Copy to `.env` and fill in values

### requirements.txt
**Purpose**: Python dependencies

**Key Packages**:
- Flask (web framework)
- azure-ai-formrecognizer (OCR)
- azure-ai-textanalytics (PII detection)
- Pillow (image processing)
- openai (optional)
- python-dotenv (config)

**Install**: `pip install -r requirements.txt`

### .gitignore
**Purpose**: Git ignore rules

**Ignores**:
- Python cache files
- Virtual environments
- .env file (secrets)
- IDE files
- Log files

---

## Typical Workflow

```
1. User uploads image
   ↓
2. app.py validates and routes
   ↓
3. PiiRedactionService orchestrates:
   a. TextExtractionService extracts text
   b. PiiDetectionService detects PII
   c. Maps PII to word locations
   d. ImageRedactionService draws rectangles
   ↓
4. Returns redacted PNG image
```

---

## Common Tasks

### Run the application
```bash
python app.py
# or
python start.py
```

### Test with an image
```bash
python test_api.py image.png
```

### Change PII provider
Edit `app.py` → `get_redaction_service()` function:
```python
# Use OpenAI instead of Azure
from providers.openai_pii_detection_provider import OpenAiPiiDetectionServiceProvider

openai_provider = OpenAiPiiDetectionServiceProvider()
pii_detection_service = PiiDetectionService(openai_provider)
```

### Deploy to production
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## Learning Path

### For Beginners
1. Read [SETUP.md](SETUP.md) - Get it running
2. Read [README.md](README.md) - Understand features
3. Run [test_api.py](test_api.py) - Test it out
4. Read [ARCHITECTURE.md](ARCHITECTURE.md) - See how it works

### For Developers
1. Read [ARCHITECTURE.md](ARCHITECTURE.md) - System design
2. Read [app.py](app.py) - API endpoints
3. Read [services/](services/) - Business logic
4. Read [COMPARISON.md](COMPARISON.md) - C# differences

### For DevOps
1. Read [SETUP.md](SETUP.md) - Setup process
2. Read [requirements.txt](requirements.txt) - Dependencies
3. Read [config.py](config.py) - Configuration
4. Read [README.md](README.md) - Deployment section

---

## Support & Resources

- **Original C# Project**: https://github.com/david-acker/redact-pii
- **Azure Documentation**: https://docs.microsoft.com/azure/
- **Flask Documentation**: https://flask.palletsprojects.com/
- **Pillow Documentation**: https://pillow.readthedocs.io/

---

## Project Statistics

- **Total Files**: 24 files
- **Code Files**: 13 Python files
- **Documentation**: 5 markdown files
- **Configuration**: 3 config files
- **Testing**: 2 test files
- **Lines of Code**: ~1500 lines (approx)
- **Dependencies**: 8 packages

---

## Version Information

- **Python Version**: 3.8+
- **Flask Version**: 3.0.0
- **Azure SDK**: Latest stable
- **Pillow**: 10.1.0
- **OpenAI**: 1.3.7 (optional)

---

## License & Credits

This is a Python conversion of the C# PII redaction project.  
Original project by david-acker: https://github.com/david-acker/redact-pii

---

*Last Updated: December 2025*
