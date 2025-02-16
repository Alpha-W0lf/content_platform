from typing import Any, Dict, Type

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models with proper typing support."""

    type_annotation_map: Dict[Type[Any], Any] = {}
