"""
Text Extraction Service using Azure Document Intelligence.
"""
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from models import DocumentWord, BoundingBox
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class TextExtractionService:
    """Service for extracting text from images using Azure Document Intelligence."""
    
    def __init__(self, endpoint: str, key: str):
        """
        Initialize Text Extraction Service.
        
        Args:
            endpoint: Azure Document Intelligence endpoint URL
            key: Azure Document Intelligence API key
        """
        self.endpoint = endpoint
        self.credential = AzureKeyCredential(key)
        self.client = DocumentAnalysisClient(endpoint=endpoint, credential=self.credential)
    
    def extract_text_from_image(self, image_bytes: bytes) -> Tuple[str, List[DocumentWord]]:
        """
        Extract text and word-level information from an image.
        
        Args:
            image_bytes: Image content as bytes
            
        Returns:
            Tuple of (full_text_content, list_of_document_words)
        """
        try:
            logger.info(f"Extracting text from image ({len(image_bytes)} bytes)")
            
            # Analyze the document using the prebuilt-read model
            poller = self.client.begin_analyze_document("prebuilt-read", image_bytes)
            result = poller.result()
            
            # Extract full text content
            full_text = result.content
            
            # Extract word-level information with bounding boxes
            document_words = []
            for page in result.pages:
                for word in page.words:
                    # Convert Azure polygon to our BoundingBox
                    polygon = [coord for point in word.polygon for coord in (point.x, point.y)]
                    bounding_box = BoundingBox.from_polygon(polygon)
                    
                    document_word = DocumentWord(
                        content=word.content,
                        bounding_box=bounding_box,
                        confidence=word.confidence
                    )
                    document_words.append(document_word)
            
            logger.info(f"Extracted {len(document_words)} words from image")
            return full_text, document_words
        
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}", exc_info=True)
            raise
