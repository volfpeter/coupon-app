from typing import Generic, Mapping, Type, TypeVar

from sqlmodel import SQLModel, Session, select

AtomicPrimaryKey = int | str
PrimaryKey = AtomicPrimaryKey | tuple[AtomicPrimaryKey, ...] | list[AtomicPrimaryKey] | Mapping[str, AtomicPrimaryKey]

TModel = TypeVar("TModel", bound=SQLModel)
TCreate = TypeVar("TCreate", bound=SQLModel)
TUpdate = TypeVar("TUpdate", bound=SQLModel)
TPK = TypeVar("TPK", bound=PrimaryKey)


class ServiceException(Exception):
    """Base exception raise by services."""

    ...


class CommitFailed(ServiceException):
    """Raise by the service when a commit fails."""

    ...


class NotFound(ServiceException):
    """Raise by services when an item is not found."""

    ...


class Service(Generic[TModel, TCreate, TUpdate, TPK]):
    """
    Base service implementation.

    It's a wrapper `sqlmodel`'s `Session`. When using the service, use the practices
    that are recommended in `sqlmodel`'s [documentation](https://sqlmodel.tiangolo.com/).
    For example don't reuse the same service instance across multiple requests.
    """

    __slots__ = (
        "_model",
        "_session",
    )

    def __init__(self, session: Session, *, model: Type[TModel]) -> None:
        """
        Initialization.

        Arguments:
            session: The session instance the service will use.
            model: The database *table* model.
        """
        self._model = model
        self._session = session

    def create(self, data: TCreate) -> TModel:
        """
        Creates a new database entry from the given data.

        Arguments:
            data: Creation data.

        Raises:
            CommitFailed: If the service fails to commit the operation.
        """
        session = self._session
        db_item = self._model.from_orm(data)
        session.add(db_item)
        try:
            session.commit()
        except Exception:
            raise CommitFailed("Commit failed.")
        session.refresh(db_item)
        return db_item

    def delete_by_pk(self, pk: TPK) -> None:
        """
        Deletes the item with the given primary key from the database.

        Arguments:
            pk: The primary key.

        Raises:
            CommitFailed: If the service fails to commit the operation.
            NotFound: If the document with the given primary key does not exist.
        """
        session = self._session

        item = self.get_by_pk(pk)
        if item is None:
            raise NotFound(self._format_primary_key(pk))

        session.delete(item)
        try:
            session.commit()
        except Exception:
            raise CommitFailed("Failed to delete item.")

    def get_all(self) -> list[TModel]:
        """
        Returns all items from the database.
        """
        return self._session.exec(select(self._model)).all()

    def get_by_pk(self, pk: PrimaryKey) -> TModel | None:
        """
        Returns the item with the given primary key if it exists.

        Arguments:
            pk: The primary key.
        """
        return self._session.get(self._model, pk)

    def update(self, pk: TPK, data: TUpdate) -> TModel:
        """
        Updates the item with the given primary key.

        Arguments:
            pk: The primary key.
            data: Update data.

        Raises:
            CommitFailed: If the service fails to commit the operation.
            NotFound: If the document with the given primary key does not exist.
        """
        session = self._session

        item = self.get_by_pk(pk)
        if item is None:
            raise NotFound(self._format_primary_key(pk))

        changes = self._prepare_for_update(data)
        for key, value in changes.items():
            setattr(item, key, value)

        session.add(item)
        try:
            session.commit()
        except Exception:
            raise CommitFailed(f"Failed to update {self._format_primary_key(pk)}.")

        session.refresh(item)
        return item

    def _format_primary_key(self, pk: TPK) -> str:
        """
        Returns the string-formatted version of the primary key.

        Arguments:
            pk: The primary key to format.

        Raises:
            ValueError: If formatting fails.
        """
        if isinstance(pk, (str, int)):
            return str(pk)
        elif isinstance(pk, (tuple, list)):
            return "|".join(pk)
        elif isinstance(pk, dict):
            return "|".join(f"{k}:{v}" for k, v in pk.items())

        raise ValueError("Unrecognized primary key type.")

    def _prepare_for_update(self, data: TUpdate) -> dict:
        """
        Hook that is called before applying the given update.

        The methods role is to convert the given data into a `dict` of
        attribute name - new value pairs, omitting unchanged values.

        The default implementation is `data.dict(exclude_unset=True)`.

        Arguments:
            data: The update data.
        """
        return data.dict(exclude_unset=True)
