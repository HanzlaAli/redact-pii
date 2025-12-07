from flask import Flask, request, send_file, jsonify
from werkzeug.utils import secure_filename
import io
import logging
from config import Config
from services.pii_redaction_service import PiiRedactionService
from services.pii_detection_service import PiiDetectionService
from services.text_extraction_service import TextExtractionService
from services.image_redaction_service import ImageRedactionService
from providers.azure_pii_detection_provider import AzurePiiDetectionServiceProvider

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Validate configuration
try:
    Config.validate()
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    raise


def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def get_redaction_service():
    """Factory function to create PII redaction service with all dependencies."""
    # Initialize providers
    azure_pii_provider = AzurePiiDetectionServiceProvider(
        endpoint=Config.AZURE_LANGUAGE_ENDPOINT,
        key=Config.AZURE_LANGUAGE_KEY
    )
    
    # Initialize services
    text_extraction_service = TextExtractionService(
        endpoint=Config.AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT,
        key=Config.AZURE_DOCUMENT_INTELLIGENCE_KEY
    )
    
    pii_detection_service = PiiDetectionService(
        pii_detection_provider=azure_pii_provider
    )
    
    image_redaction_service = ImageRedactionService()
    
    # Create and return the main redaction service
    return PiiRedactionService(
        pii_detection_service=pii_detection_service,
        text_extraction_service=text_extraction_service,
        image_redaction_service=image_redaction_service
    )


@app.route('/redact-pii', methods=['POST'])
def redact_pii():
    """
    Endpoint to redact PII from an uploaded image.
    
    Accepts: multipart/form-data with 'file' field containing an image
    Returns: PNG image with PII redacted (black rectangles)
    """
    try:
        # Check if file is present in the request
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400
        
        file = request.files['file']
        
        # Check if a file was selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if the file has an allowed extension
        if not allowed_file(file.filename):
            return jsonify({
                'error': f'File type not allowed. Allowed types: {", ".join(Config.ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Read the file content
        file_content = file.read()
        
        if not file_content:
            return jsonify({'error': 'Empty file'}), 400
        
        logger.info(f"Processing file: {file.filename} ({len(file_content)} bytes)")
        
        # Get the redaction service and process the image
        redaction_service = get_redaction_service()
        redacted_image_bytes, content_type = redaction_service.redact_pii(file_content)
        
        logger.info(f"Successfully redacted PII from {file.filename}")
        
        # Return the redacted image
        return send_file(
            io.BytesIO(redacted_image_bytes),
            mimetype=content_type,
            as_attachment=True,
            download_name=secure_filename(file.filename)
        )
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'PII Redaction API'
    }), 200


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    return jsonify({
        'error': 'File too large. Maximum file size is 16MB.'
    }), 413


if __name__ == '__main__':
    logger.info("Starting PII Redaction API...")
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)
