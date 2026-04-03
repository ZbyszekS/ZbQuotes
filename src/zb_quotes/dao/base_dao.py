# dao/base_dao.py
from typing import Type, TypeVar, Generic
from sqlalchemy.orm import Session
from sqlalchemy import select
from zb_quotes.models.models import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseDao(Generic[ModelType]):
    """
    Base DAO with common CRUD operations.
    Subclass this for model-specific DAOs.
    """
    
    def __init__(self, model_class: Type[ModelType]):
        self.model_class = model_class
    
    def get_by_id(self, session: Session, id: int) -> ModelType | None:
        return session.get(self.model_class, id)
    
    def get_all(self, session: Session) -> list[ModelType]:
        stmt = select(self.model_class)
        return list(session.execute(stmt).scalars())
    
    def insert(self, session: Session, entity: ModelType) -> ModelType:
        session.add(entity)
        session.flush()
        return entity
    
    def update(self, session: Session, entity: ModelType) -> ModelType:
        session.flush()
        return entity
    
    def delete(self, session: Session, entity: ModelType) -> None:
        session.delete(entity)
        session.flush()
    
    def get_many_by_unique_cols(self, session: Session, **kwargs) -> list[ModelType]:
        stmt = select(self.model_class)
        for key, value in kwargs.items():
            col  = getattr(self.model_class, key)
            stmt = stmt.where(col == value)
        return list(session.execute(stmt).scalars())

    