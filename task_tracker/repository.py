import abc
import enum
import uuid
from decimal import Decimal
from random import choice
from typing import TypeVar, Sequence, Generic

from sqlalchemy import Table, Select, insert, select, delete, update
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.sql.functions import random
from sqlalchemy.orm import Session

from task_tracker.tables import account, task, payment
from task_tracker.types import User, Payment, Task, RoleEnum, TaskStatusEnum, Dashboard

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
        user_public_id: str,
    ) -> None:
        values = {
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "role": role,
            "user_public_id": user_public_id,
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
        user_public_id: str,
        username: str | None = None,
        role: int | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
    ) -> None:
        query = (
            update(self.table)
            .where(self.table.c.user_public_id == user_public_id)
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
        query = delete(self.table).where(self.table.c.user_public_id == str(user_id))
        self._session.execute(query)
        self._session.commit()

    def check_role(self, public_user_id: uuid.UUID) -> bool:
        query = (
            select(
                self.table.c.id,
                self.table.c.username,
                self.table.c.user_public_id,
                self.table.c.role,
            )
            .select_from(self.table)
            .where(
                self.table.c.user_public_id == public_user_id,
                self.table.c.role <= RoleEnum.manager.value,
            )
        )
        result = self._get_from_query(query)
        if len(result) == 0:
            return False
        return True


class TaskRepository(BaseRepository):
    table = task
    model_cls = Task

    def create_task(self, cost: Decimal, description: str) -> None:
        clients = self._get_clients()
        values = {
            "cost": cost,
            "description": description,
            "task_public_id": uuid.uuid4(),
            "status": TaskStatusEnum.to_do.value,
            "user_id": choice(clients[0]),
        }
        query = insert(self.table).values(**values)

        try:
            self._session.execute(query)
            self._session.commit()
        except Exception as e:
            self._session.rollback()
            print(f"something went wrong, {e}")

    def _get_clients(self):
        query = (
            select(
                account.c.user_public_id,
            )
            .select_from(account)
            .where(
                account.c.role <= RoleEnum.manager.value,
            )
        )
        with self._session.execute(query) as rows:
            result = rows.fetchall()
        return list(item[0] for item in result)

    def _get_open_tasks(self):
        query = (
            select(*self.table.c)
            .select_from(self.table)
            .where(self.table.c.status != TaskStatusEnum.done.value)
        )
        with self._session.execute(query) as rows:
            result = rows.fetchall()
        return tuple(Task(**row._mapping) for row in result)

    def reassign_task(self) -> None:
        clients = self._get_clients()

        # вообще-то за такое надо бить. Но это учебный проект и я потом переделаю (нет)
        for task in self._get_open_tasks():
            user_id = choice(clients)
            query = (
                update(self.table)
                .where(self.table.c.id == task.id)
                .values(status=TaskStatusEnum.to_do.value, user_id=user_id)
            )

            try:
                self._session.execute(query)
                self._session.commit()
            except Exception as e:
                self._session.rollback()
                print(f"something went wrong, {e}")

    def dashboard(self):
        query = (
            select(
                self.table.c.task_public_id,
                self.table.c.description,
                self.table.c.status,
                self.table.c.cost,
                account.c.username,
                account.c.email,
            )
            .select_from(self.table)
            .join(account, account.c.user_public_id == self.table.c.user_id)
        )
        with self._session.execute(query) as rows:
            result = rows.fetchall()
        return list(Dashboard(**row._mapping) for row in result)


class PaymentRepository(BaseRepository):
    table = payment
    model_cls = Payment
