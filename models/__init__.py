"""
Data models for the PII redaction application.
"""
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class BoundingBox:
    """Represents a bounding box for text in an image."""
    x: float
    y: float
    width: float
    height: float
    
    @classmethod
    def from_polygon(cls, polygon: List[float]) -> 'BoundingBox':
        """
        Create a BoundingBox from a polygon (list of x,y coordinates).
        
        Args:
            polygon: List of coordinates [x1, y1, x2, y2, x3, y3, x4, y4]
        
        Returns:
            BoundingBox instance
        """
        if len(polygon) < 8:
            raise ValueError("Polygon must have at least 4 points (8 coordinates)")
        
        # Extract x and y coordinates
        x_coords = [polygon[i] for i in range(0, len(polygon), 2)]
        y_coords = [polygon[i] for i in range(1, len(polygon), 2)]
        
        # Calculate bounding box
        x = min(x_coords)
        y = min(y_coords)
        width = max(x_coords) - x
        height = max(y_coords) - y
        
        return cls(x=x, y=y, width=width, height=height)


@dataclass
class DocumentWord:
    """Represents a word extracted from a document."""
    content: str
    bounding_box: BoundingBox
    confidence: float = 1.0


@dataclass
class ImageRedactionResult:
    """Result of image redaction operation."""
    content: bytes
    content_type: str
