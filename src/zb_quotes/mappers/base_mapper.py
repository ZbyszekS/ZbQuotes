from typing import Any, Iterable, List, Type, TypeVar

from zb_quotes.dtos.base_dto import BaseDTO
from zb_quotes.models.models import Base

T = TypeVar('T', bound=BaseDTO)

class BaseMapper:

    @staticmethod
    def map_list(models: Iterable[Any], dto_cls: Type[T]) -> List[T]:
        return [dto_cls.from_model(m) for m in models]

    @staticmethod
    def map_dto_to_model(dto: T, model: Base, exclude=("id",)):
        for name in dto.__dataclass_fields__:
            if name in exclude:
                continue
            if hasattr(model, name):
                setattr(model, name, getattr(dto, name))
