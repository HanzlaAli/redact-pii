"""
Main PII Redaction Service that orchestrates all sub-services.
"""
from services.pii_detection_service import PiiDetectionService
from services.text_extraction_service import TextExtractionService
from services.image_redaction_service import ImageRedactionService
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class PiiRedactionService:
    """Main service that orchestrates the PII redaction workflow."""
    
    def __init__(
        self,
        pii_detection_service: PiiDetectionService,
        text_extraction_service: TextExtractionService,
        image_redaction_service: ImageRedactionService
    ):
        """
        Initialize PII Redaction Service.
        
        Args:
            pii_detection_service: Service for detecting PII in text
            text_extraction_service: Service for extracting text from images
            image_redaction_service: Service for redacting images
        """
        self.pii_detection_service = pii_detection_service
        self.text_extraction_service = text_extraction_service
        self.image_redaction_service = image_redaction_service
    
    def redact_pii(self, source_image_bytes: bytes) -> Tuple[bytes, str]:
        """
        Main workflow to redact PII from an image.
        
        Steps:
        1. Extract text and word locations from the image
        2. Detect PII entities in the extracted text
        3. Map PII entities to word locations
        4. Draw black rectangles over PII locations
        
        Args:
            source_image_bytes: Original image content as bytes
            
        Returns:
            Tuple of (redacted_image_bytes, content_type)
        """
        try:
            logger.info("Starting PII redaction workflow")
            
            # Step 1: Extract text from image
            full_text, extracted_words = self.text_extraction_service.extract_text_from_image(
                source_image_bytes
            )
            
            logger.info(f"Extracted text length: {len(full_text)} characters")
            
            # Step 2: Detect PII in the extracted text
            pii_values = self.pii_detection_service.extract_pii(full_text)
            
            logger.info(f"Detected {len(pii_values)} unique PII values")
            
            # Step 3: Map PII to word bounding boxes
            redaction_areas = []
            if pii_values:
                words_containing_pii = self.pii_detection_service.get_words_containing_pii(
                    extracted_words, 
                    pii_values
                )
                
                # Extract bounding boxes from words containing PII
                redaction_areas = [word.bounding_box for word in words_containing_pii]
                
                logger.info(f"Identified {len(redaction_areas)} redaction areas")
            else:
                logger.info("No PII detected, returning original image")
            
            # Step 4: Redact the image
            result = self.image_redaction_service.redact_image(
                source_image_bytes, 
                redaction_areas
            )
            
            logger.info("PII redaction workflow completed successfully")
            
            return result.content, result.content_type
        
        except Exception as e:
            logger.error(f"Error in PII redaction workflow: {str(e)}", exc_info=True)
            raise
