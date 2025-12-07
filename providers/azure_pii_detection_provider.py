"""
Azure PII Detection Service Provider using Azure Language Service.
"""
from typing import List
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from interfaces import IPiiDetectionServiceProvider
import logging

logger = logging.getLogger(__name__)


class AzurePiiDetectionServiceProvider(IPiiDetectionServiceProvider):
    """PII detection using Azure Language Service."""
    
    def __init__(self, endpoint: str, key: str):
        """
        Initialize Azure PII Detection Service.
        
        Args:
            endpoint: Azure Language Service endpoint URL
            key: Azure Language Service API key
        """
        self.endpoint = endpoint
        self.credential = AzureKeyCredential(key)
        self.client = TextAnalyticsClient(endpoint=endpoint, credential=self.credential)
    
    def detect_pii(self, text_content: str) -> List[str]:
        """
        Detect PII entities in text using Azure Language Service.
        
        Args:
            text_content: Text to analyze for PII
            
        Returns:
            List of PII entity strings
        """
        try:
            logger.info(f"Detecting PII in text ({len(text_content)} characters)")
            
            # Call Azure Language Service to recognize PII entities
            response = self.client.recognize_pii_entities([text_content], language="en")
            
            pii_entities = []
            for doc in response:
                if not doc.is_error:
                    for entity in doc.entities:
                        pii_entities.append(entity.text)
                        logger.debug(f"Found PII: {entity.text} (category: {entity.category})")
                else:
                    logger.error(f"Error in PII detection: {doc.error}")
            
            logger.info(f"Found {len(pii_entities)} PII entities")
            return pii_entities
        
        except Exception as e:
            logger.error(f"Error during PII detection: {str(e)}", exc_info=True)
            raise
