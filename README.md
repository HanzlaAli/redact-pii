# PII Redaction Service - Python Version

A Flask-based REST API for detecting and redacting Personally Identifiable Information (PII) from images using Azure AI services and OpenAI.

## Features

- 🔍 **Text Extraction**: Extract text from images using Azure Document Intelligence (OCR)
- 🛡️ **PII Detection**: Detect PII using Azure Language Service or OpenAI GPT-4
- 🖼️ **Image Redaction**: Automatically redact PII with black rectangles
- 🚀 **REST API**: Simple POST endpoint for easy integration
- 🔧 **Configurable**: Support for multiple PII detection providers

## How It Works

1. **Upload Image**: Send an image containing PII (credit cards, names, addresses, etc.)
2. **Text Extraction**: Azure Document Intelligence extracts text and word locations
3. **PII Detection**: Azure Language Service or OpenAI identifies PII entities
4. **Smart Mapping**: Words containing PII are matched with their locations
5. **Redaction**: Black rectangles are drawn over PII areas
6. **Return**: Redacted image is returned as PNG

## Example

Input: Image with credit card information  
Output: Same image with PII redacted (black rectangles)

## Architecture

```
app.py                          # Flask application and API endpoints
├── config.py                   # Configuration management
├── models/                     # Data models
│   └── __init__.py            # BoundingBox, DocumentWord, ImageRedactionResult
├── interfaces/                 # Abstract interfaces
│   └── __init__.py            # IPiiDetectionServiceProvider
├── providers/                  # PII detection providers
│   ├── azure_pii_detection_provider.py
│   └── openai_pii_detection_provider.py
└── services/                   # Core business logic
    ├── text_extraction_service.py
    ├── pii_detection_service.py
    ├── image_redaction_service.py
    └── pii_redaction_service.py
```

## Prerequisites

- Python 3.8 or higher
- Azure subscription with:
  - Azure Document Intelligence (Form Recognizer) resource
  - Azure Language Service resource
- (Optional) OpenAI API key for alternative PII detection

## Installation

### 1. Clone or download this repository

```bash
cd python-version
```

### 2. Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` file:

```env
# Required: Azure Document Intelligence (for OCR)
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=your_key_here

# Required: Azure Language Service (for PII detection)
AZURE_LANGUAGE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_LANGUAGE_KEY=your_key_here

# Optional: OpenAI API (alternative PII detection)
OPENAI_API_KEY=your_openai_key_here
```

## Usage

### Running the API

Start the Flask server:

```bash
python app.py
```

The API will be available at `http://localhost:5000`

### API Endpoints

#### POST /redact-pii

Redact PII from an uploaded image.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: Form data with `file` field containing the image

**Response:**
- Content-Type: `image/png`
- Body: Redacted image with black rectangles over PII

**Example using cURL:**

```bash
curl -X POST http://localhost:5000/redact-pii \
  -F "file=@path/to/your/image.png" \
  --output redacted_image.png
```

**Example using Python requests:**

```python
import requests

url = "http://localhost:5000/redact-pii"
files = {"file": open("input_image.png", "rb")}

response = requests.post(url, files=files)

if response.status_code == 200:
    with open("redacted_image.png", "wb") as f:
        f.write(response.content)
    print("Image redacted successfully!")
else:
    print(f"Error: {response.json()}")
```

#### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "PII Redaction API"
}
```

### Using Postman

1. Create a new POST request to `http://localhost:5000/redact-pii`
2. Go to the "Body" tab
3. Select "form-data"
4. Add a key named `file` with type "File"
5. Select an image file to upload
6. Send the request
7. The response will be the redacted image (PNG format)

## PII Detection Providers

### Azure Language Service (Default)

The default provider uses Azure's AI Language service to detect PII entities:
- Credit card numbers
- Social security numbers
- Names
- Addresses
- Phone numbers
- Email addresses
- And more...

### OpenAI GPT-4 (Alternative)

To use OpenAI instead of Azure for PII detection, modify `app.py`:

```python
# Replace this line in get_redaction_service()
from providers.openai_pii_detection_provider import OpenAiPiiDetectionServiceProvider

# Replace the provider initialization
openai_pii_provider = OpenAiPiiDetectionServiceProvider(
    api_key=Config.OPENAI_API_KEY,
    model="gpt-4"
)

pii_detection_service = PiiDetectionService(
    pii_detection_provider=openai_pii_provider
)
```

### Custom GPT-4 Prompt

The OpenAI provider uses this prompt to detect PII:

```
You are detecting personally identifiable information (PII) in the provided text.
List each token or group of tokens in the text that may contain PII 
(for example: credit card numbers, security codes, names, addresses).
Do not modify or change the text in any way, or add labels.
Exclude labels, descriptive text, other text elements which may refer to 
or label PII, but are not actually PII themselves 
(for example: "Card number", "Expiration", "Country").
Display each piece of PII as-is with no additional quotes, symbols, or other characters.
```

## Configuration

### Environment Variables

All configuration is managed through environment variables in the `.env` file:

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT` | Yes | Azure Document Intelligence endpoint URL |
| `AZURE_DOCUMENT_INTELLIGENCE_KEY` | Yes | Azure Document Intelligence API key |
| `AZURE_LANGUAGE_ENDPOINT` | Yes | Azure Language Service endpoint URL |
| `AZURE_LANGUAGE_KEY` | Yes | Azure Language Service API key |
| `OPENAI_API_KEY` | No | OpenAI API key (for alternative PII detection) |
| `FLASK_DEBUG` | No | Enable Flask debug mode (default: True) |

### File Upload Limits

- Maximum file size: 16 MB
- Allowed file types: PNG, JPG, JPEG, BMP, GIF, TIFF

To modify these limits, edit `config.py`:

```python
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'gif', 'tiff'}
```

## Development

### Project Structure

```
python-version/
├── app.py                     # Main Flask application
├── config.py                  # Configuration management
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── README.md                 # This file
├── models/
│   └── __init__.py           # Data models
├── interfaces/
│   └── __init__.py           # Abstract interfaces
├── providers/
│   ├── __init__.py
│   ├── azure_pii_detection_provider.py
│   └── openai_pii_detection_provider.py
└── services/
    ├── __init__.py
    ├── text_extraction_service.py
    ├── pii_detection_service.py
    ├── image_redaction_service.py
    └── pii_redaction_service.py
```

### Adding New PII Detection Providers

1. Create a new provider class that implements `IPiiDetectionServiceProvider`
2. Implement the `detect_pii(text_content: str) -> List[str]` method
3. Update `app.py` to use your new provider

Example:

```python
from interfaces import IPiiDetectionServiceProvider

class CustomPiiDetectionProvider(IPiiDetectionServiceProvider):
    def detect_pii(self, text_content: str) -> List[str]:
        # Your custom PII detection logic
        return ["detected", "pii", "values"]
```

## Logging

The application uses Python's built-in logging module. Logs include:
- Request processing information
- Text extraction results
- PII detection results
- Redaction operations
- Error details

Logs are output to console with INFO level by default.

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK`: Successfully redacted image
- `400 Bad Request`: Invalid request (no file, wrong file type, etc.)
- `413 Payload Too Large`: File exceeds 16 MB limit
- `500 Internal Server Error`: Processing error (with error details)

Example error response:

```json
{
  "error": "File type not allowed. Allowed types: png, jpg, jpeg, bmp, gif, tiff"
}
```

## Troubleshooting

### "Missing required configuration" error

Make sure all required environment variables are set in your `.env` file:
- `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT`
- `AZURE_DOCUMENT_INTELLIGENCE_KEY`
- `AZURE_LANGUAGE_ENDPOINT`
- `AZURE_LANGUAGE_KEY`

### Azure authentication errors

Verify your Azure credentials:
1. Check that endpoints are correct (should end with `.cognitiveservices.azure.com/`)
2. Verify API keys are valid
3. Ensure resources are active in Azure portal

### No PII detected

If PII is not being detected:
1. Check image quality (text should be clear and readable)
2. Verify the language is supported (default: English)
3. Try the OpenAI provider for comparison
4. Check logs for extraction and detection details

### Image quality issues

For best results:
- Use high-resolution images
- Ensure text is clear and not blurred
- Avoid heavily compressed images
- Use standard fonts when possible

## Deployment

### Production Considerations

1. **Security**:
   - Use environment variables for all secrets
   - Enable HTTPS
   - Implement authentication/authorization
   - Validate and sanitize all inputs

2. **Performance**:
   - Use a production WSGI server (Gunicorn, uWSGI)
   - Implement request queuing for high loads
   - Cache Azure client instances
   - Consider async processing for large files

3. **Monitoring**:
   - Implement structured logging
   - Set up application monitoring
   - Track API usage and costs
   - Monitor Azure service quotas

### Example Gunicorn Deployment

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Cost Considerations

This application uses paid Azure services:

- **Azure Document Intelligence**: Pay per page analyzed
- **Azure Language Service**: Pay per text record
- **OpenAI API** (optional): Pay per token

Check Azure pricing pages for current rates and free tier options.

## License

This is a Python conversion of the original C# project. Please refer to the original repository for license information.

## Credits

This Python version is based on the original C# implementation:
https://github.com/david-acker/redact-pii

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review Azure service status
3. Check application logs for error details
4. Refer to the original C# project for conceptual guidance

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Future Enhancements

- [ ] Async processing support
- [ ] Batch processing endpoint
- [ ] Multiple file upload
- [ ] Configurable redaction styles (blur, pixelate, etc.)
- [ ] Support for additional languages
- [ ] PDF support
- [ ] Custom PII entity types
- [ ] Result caching
- [ ] API rate limiting
- [ ] Docker containerization
