# Basic DTO class providing from_model class method for easy model-to-DTO conversion
from dataclasses import dataclass, fields
from typing import Type, TypeVar, Any, Optional

T = TypeVar("T", bound="BaseDTO")


class BaseDTO:
    @classmethod
    def from_model(cls: Type[T], model: Any) -> Optional[T]:
        """Create DTO from SQLAlchemy model instance. Returns None if model is None."""
        if model is None:
            return None
            
        dto_field_names = {f.name for f in fields(cls)}
        
        data = {
            name: getattr(model, name)
            for name in dto_field_names
            if hasattr(model, name)
        }
        
        return cls(**data)  # type: ignore