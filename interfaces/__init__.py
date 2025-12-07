from abc import ABC, abstractmethod
from typing import List


class IPiiDetectionServiceProvider(ABC):
    """Interface for PII detection service providers."""
    
    @abstractmethod
    async def detect_pii(self, text_content: str) -> List[str]:
        """
        Detect PII entities in the given text.
        
        Args:
            text_content: Text to analyze for PII
            
        Returns:
            List of PII entity strings found in the text
        """
        pass
