"""
Utility functions for the backend.
These functions provide common functionality across different parts of the application.
"""

from datetime import datetime
from typing import Any, Dict, Optional
import json
import uuid


def generate_uuid() -> str:
    """Generate a unique UUID string."""
    return str(uuid.uuid4())


def parse_json(json_str: Optional[str]) -> Dict[str, Any]:
    """
    Safely parse JSON string to dictionary.
    Returns empty dict if input is None or invalid JSON.
    """
    if not json_str:
        return {}
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return {}


def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """Format datetime to ISO 8601 string."""
    if dt is None:
        return None
    return dt.isoformat()


def is_valid_uuid(val: str) -> bool:
    """Check if string is a valid UUID."""
    try:
        uuid.UUID(str(val))
        return True
    except (ValueError, AttributeError):
        return False
