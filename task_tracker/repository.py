import abc
import enum
import uuid
from typing import TypeVar, Sequence, Generic

from sqlalchemy import Table, Select, insert, delete, update
from sqlalchemy.orm import Session

from task_tracker.tables import account
from task_tracker.types import User


ModelT = TypeVar("ModelT")


class KafkaKey(enum.Enum):
    create = "create"
    update = "update"
    delete = "delete"


class BaseRepository(Generic[ModelT], abc.ABC):
    @property
    @abc.abstractmethod
    def model_cls(self) -> type[ModelT]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def table(self) -> Table:
        raise NotImplementedError

    def __init__(self, session: Session) -> None:
        self._session = session

    def _get_from_query(self, query: Select) -> Sequence[ModelT]:
        model_cls = self.model_cls
        with self._session.execute(query) as rows:
            result = rows.fetchall()
        return tuple(model_cls(**row._mapping) for row in result)


class UserRepository(BaseRepository):
    table = account
    model_cls = User

    def listen_user_info(self, key: str, value: dict) -> None:
        match key:
            case KafkaKey.create.value:
                self.create_user(**value)
            case KafkaKey.update.value:
                self.update_user(**value)
            case KafkaKey.delete.value:
                self.delete_user(**value)

    def create_user(
        self,
        username: str,
        role: int,
        first_name: str,
        last_name: str,
        email: str,
        public_id: str,
    ) -> None:
        values = {
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "role": role,
            "public_id": public_id,
        }
        query = insert(self.table).values(**values)

        try:
            self._session.execute(query)
            self._session.commit()
        except Exception as e:
            self._session.rollback()
            print(f"something went wrong, {e}")

    def update_user(
        self,
        public_id: str,
        username: str | None = None,
        role: int | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
    ) -> None:
        query = (
            update(self.table)
            .where(self.table.c.public_id == public_id)
            .values(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                role=role,
            )
        )
        self._session.execute(query)
        self._session.commit()

    def delete_user(self, user_id: uuid.UUID) -> None:
        query = delete(self.table).where(self.table.c.public_id == str(user_id))
        self._session.execute(query)
        self._session.commit()
