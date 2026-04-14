from typing import Any, Iterable, List, Type, TypeVar

from zb_quotes.dtos.base_dto import BaseDTO
from zb_quotes.models.models import Base

Dto = TypeVar('T', bound=BaseDTO)

class BaseMapper:

    @staticmethod
    def models_2_dto_list(models: Iterable[Any], dto_cls: Type[Dto]) -> List[Dto]:
        return [dto_cls.from_model(m) for m in models]

    @staticmethod
    def map_dto_2_model(dto: Dto, model: Base, exclude=("id",)):
        for name in dto.__dataclass_fields__:
            if name in exclude:
                continue
            if hasattr(model, name):
                setattr(model, name, getattr(dto, name))
