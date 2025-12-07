"""
PII Detection Service that coordinates PII detection providers.
"""
from typing import List, Set
from interfaces import IPiiDetectionServiceProvider
from models import DocumentWord
import logging

logger = logging.getLogger(__name__)


class PiiDetectionService:
    """Service for detecting PII in text and mapping to document words."""
    
    def __init__(self, pii_detection_provider: IPiiDetectionServiceProvider):
        """
        Initialize PII Detection Service.
        
        Args:
            pii_detection_provider: Provider for PII detection (Azure or OpenAI)
        """
        self.pii_detection_provider = pii_detection_provider
    
    def extract_pii(self, text_content: str) -> Set[str]:
        """
        Extract PII entities from text.
        
        Args:
            text_content: Text to analyze
            
        Returns:
            Set of unique PII entity strings
        """
        try:
            pii_values = self.pii_detection_provider.detect_pii(text_content)
            return set(pii_values)
        except Exception as e:
            logger.error(f"Error extracting PII: {str(e)}", exc_info=True)
            raise
    
    def get_words_containing_pii(
        self, 
        extracted_words: List[DocumentWord], 
        pii_values: Set[str]
    ) -> List[DocumentWord]:
        """
        Find document words that contain PII.
        
        This handles multi-word PII values by matching word components.
        For example, "John Doe" will match both "John" and "Doe" words.
        
        Args:
            extracted_words: List of words extracted from document
            pii_values: Set of PII values to search for
            
        Returns:
            List of DocumentWord objects that contain PII
        """
        words_containing_pii = set()
        
        for pii_value in pii_values:
            # Split PII value into components (handles multi-word PII)
            pii_components = [
                component.strip() 
                for component in pii_value.strip().split() 
                if component.strip()
            ]
            
            # Find words that contain any of the PII components
            for word in extracted_words:
                for component in pii_components:
                    if component.lower() in word.content.lower() or \
                       word.content.lower() in component.lower():
                        words_containing_pii.add(word)
                        logger.debug(f"Word '{word.content}' matches PII component '{component}'")
        
        logger.info(f"Found {len(words_containing_pii)} words containing PII")
        return list(words_containing_pii)
