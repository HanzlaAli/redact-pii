"""
Image Redaction Service for drawing rectangles over PII areas.
"""
from PIL import Image, ImageDraw
from models import BoundingBox, ImageRedactionResult
from typing import List
import io
import logging

logger = logging.getLogger(__name__)


class ImageRedactionService:
    """Service for redacting PII from images by drawing black rectangles."""
    
    def redact_image(
        self, 
        source_image_bytes: bytes, 
        redaction_areas: List[BoundingBox]
    ) -> ImageRedactionResult:
        """
        Redact PII from an image by drawing black rectangles over specified areas.
        
        Args:
            source_image_bytes: Original image content as bytes
            redaction_areas: List of bounding boxes to redact
            
        Returns:
            ImageRedactionResult with redacted image bytes and content type
        """
        try:
            logger.info(f"Redacting image with {len(redaction_areas)} areas")
            
            # Open the image
            image = Image.open(io.BytesIO(source_image_bytes))
            
            # Convert to RGB if necessary (e.g., for PNG with transparency)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Create a drawing context
            draw = ImageDraw.Draw(image)
            
            # Draw black rectangles over PII areas
            for bbox in redaction_areas:
                # PIL uses (left, top, right, bottom) format
                rectangle = [
                    bbox.x,
                    bbox.y,
                    bbox.x + bbox.width,
                    bbox.y + bbox.height
                ]
                draw.rectangle(rectangle, fill='black')
                logger.debug(f"Drew redaction rectangle at {rectangle}")
            
            # Save the redacted image to bytes
            output_buffer = io.BytesIO()
            image.save(output_buffer, format='PNG')
            redacted_bytes = output_buffer.getvalue()
            
            logger.info(f"Successfully redacted image ({len(redacted_bytes)} bytes)")
            
            return ImageRedactionResult(
                content=redacted_bytes,
                content_type='image/png'
            )
        
        except Exception as e:
            logger.error(f"Error redacting image: {str(e)}", exc_info=True)
            raise
