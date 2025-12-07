"""
OpenAI PII Detection Service Provider using GPT models.
"""
from typing import List
from openai import OpenAI
from interfaces import IPiiDetectionServiceProvider
import logging
import os

logger = logging.getLogger(__name__)


class OpenAiPiiDetectionServiceProvider(IPiiDetectionServiceProvider):
    """PII detection using OpenAI GPT models."""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        """
        Initialize OpenAI PII Detection Service.
        
        Args:
            api_key: OpenAI API key (optional, can use OPENAI_API_KEY env var)
            model: Model to use for PII detection (default: gpt-4)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        self.client = OpenAI(api_key=self.api_key)
    
    def detect_pii(self, text_content: str) -> List[str]:
        """
        Detect PII entities in text using OpenAI GPT.
        
        Args:
            text_content: Text to analyze for PII
            
        Returns:
            List of PII entity strings
        """
        try:
            logger.info(f"Detecting PII using OpenAI ({len(text_content)} characters)")
            
            user_message = f"""You are detecting personally identifiable information (PII) in the provided text.
List each token or group of tokens in the text that may contain PII (for example: credit card numbers, security codes, names, addresses).
Do not modify or change the text in any way, or add labels.
Exclude labels, descriptive text, other text elements which may refer to or label PII, but are not actually PII themselves (for example: "Card number", "Expiration", "Country").
Also exclude text artifacts, incorrectly extracted text, or miscellaneous text that is unrelated to the PII.
Display each piece of PII as-is with no additional quotes, symbols, or other characters:

{text_content}"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": user_message}
                ],
                temperature=0,
                max_tokens=512,
                n=1
            )
            
            if not response.choices:
                raise Exception("No response from OpenAI")
            
            response_text = response.choices[0].message.content
            
            if not response_text:
                logger.warning("Empty response from OpenAI")
                return []
            
            # Parse the response - each line is a PII entity
            pii_entities = [
                line.strip() 
                for line in response_text.strip().split('\n') 
                if line.strip()
            ]
            
            logger.info(f"Found {len(pii_entities)} PII entities using OpenAI")
            return pii_entities
        
        except Exception as e:
            logger.error(f"Error during OpenAI PII detection: {str(e)}", exc_info=True)
            raise
