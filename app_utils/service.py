from typing import Generic, Type, TypeVar

from sqlmodel import SQLModel, Session, select


Self = TypeVar("Self", bound="Service")  # Python 3.10 support... Should upgrade.
TModel = TypeVar("TModel", bound=SQLModel)
TCreate = TypeVar("TCreate", bound=SQLModel)
TUpdate = TypeVar("TUpdate", bound=SQLModel)


class ServiceException(Exception):
    """Base exception raise by services."""

    ...


class CommitFailed(ServiceException):
    """Raise by the service when a commit fails."""

    ...


class NotFound(ServiceException):
    """Raise by services when an item is not found."""

    ...


class Service(Generic[TModel, TCreate, TUpdate]):
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

    def delete_by_id(self, id: int) -> None:
        """
        Deletes the item with the given ID from the database.

        Arguments:
            id: Item database ID.

        Raises:
            CommitFailed: If the service fails to commit the operation.
            NotFound: If the document with the given ID does not exist.
        """
        session = self._session

        item = self.get_by_id(id)
        if item is None:
            raise NotFound(str(id))

        session.delete(item)
        try:
            session.commit()
        except Exception:
            raise CommitFailed(f"Failed to delete item {id}.")

    def get_all(self) -> list[TModel]:
        """
        Returns all items from the database.
        """
        return self._session.exec(select(self._model)).all()

    def get_by_id(self, id: int) -> TModel | None:
        """
        Returns the item with the ID.

        Arguments:
            id: Item database ID.
        """
        return self._session.get(self._model, id)

    def update(self, id: int, data: TUpdate) -> TModel:
        """
        Updates the item with the given ID.

        Arguments:
            id: Item database ID.
            data: Update data.

        Raises:
            CommitFailed: If the service fails to commit the operation.
            NotFound: If the document with the given ID does not exist.
        """
        session = self._session

        item = self.get_by_id(id)
        if item is None:
            raise NotFound(str(id))

        changes = self._prepare_for_update(data)
        for key, value in changes.items():
            setattr(item, key, value)

        session.add(item)
        try:
            session.commit()
        except Exception:
            raise CommitFailed(f"Failed to update {id}.")

        session.refresh(item)
        return item

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
