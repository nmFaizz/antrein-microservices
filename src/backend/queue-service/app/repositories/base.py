from typing import Generic, Optional, Type, TypeVar

from sqlmodel import Session, SQLModel, select

ModelT = TypeVar("ModelT", bound=SQLModel)


class BaseRepository(Generic[ModelT]):
    """Generic data-access helper over a single SQLModel table.

    Repositories add/delete on the session; committing is the service layer's
    responsibility so a whole business operation stays one transaction.
    """

    model: Type[ModelT]

    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, id_: object) -> Optional[ModelT]:
        return self.session.get(self.model, id_)

    def list(self, *, offset: int = 0, limit: int = 50) -> list[ModelT]:
        statement = select(self.model).offset(offset).limit(limit)
        return list(self.session.exec(statement).all())

    def add(self, obj: ModelT) -> ModelT:
        self.session.add(obj)
        return obj

    def delete(self, obj: ModelT) -> None:
        self.session.delete(obj)
