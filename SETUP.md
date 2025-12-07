# Quick Setup Guide

## Prerequisites

- Python 3.8 or higher
- Azure subscription with Document Intelligence and Language Service
- pip (Python package manager)

## Setup Steps

### 1. Navigate to the python-version directory

```bash
cd python-version
```

### 2. Create and activate a virtual environment (Recommended)

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env`:

```bash
# Windows PowerShell
Copy-Item .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` with your Azure credentials:

```env
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=your_key_here

AZURE_LANGUAGE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_LANGUAGE_KEY=your_key_here
```

### 5. Run the application

```bash
python app.py
```

Or use the quick start script:

```bash
python start.py
```

### 6. Test the API

**Option A: Using the test script**
```bash
python test_api.py path/to/your/image.png
```

**Option B: Using cURL**
```bash
curl -X POST http://localhost:5000/redact-pii -F "file=@image.png" --output redacted.png
```

**Option C: Import the Postman collection**
- Import `pii-redaction-python.postman_collection.json` into Postman
- Select an image file in the "file" field
- Send the request

## Getting Azure Credentials

### Azure Document Intelligence
1. Go to [Azure Portal](https://portal.azure.com)
2. Create a "Document Intelligence" resource
3. Go to "Keys and Endpoint"
4. Copy the endpoint URL and key

### Azure Language Service
1. Go to [Azure Portal](https://portal.azure.com)
2. Create a "Language Service" resource
3. Go to "Keys and Endpoint"
4. Copy the endpoint URL and key

## Troubleshooting

### "Module not found" errors
Make sure you're in the virtual environment and have installed dependencies:
```bash
pip install -r requirements.txt
```

### "Missing required configuration" error
Check that your `.env` file has all required variables set.

### Port already in use
Change the port in `app.py`:
```python
app.run(host='0.0.0.0', port=5001, debug=Config.DEBUG)
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Test with sample images from the `samples/` directory
- Customize the PII detection provider in `app.py`
- Deploy to production using Gunicorn or similar WSGI server

## Quick Reference

| Command | Description |
|---------|-------------|
| `python app.py` | Start the Flask server |
| `python test_api.py <image>` | Test with an image |
| `curl http://localhost:5000/health` | Check API health |

## Support

For detailed information, see [README.md](README.md)
