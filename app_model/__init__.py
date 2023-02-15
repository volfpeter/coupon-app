from typing import TYPE_CHECKING

from sqlmodel import SQLModel

if TYPE_CHECKING:
    from sqlalchemy.future import Engine


def initialize_database(engine: "Engine") -> None:
    from .coupon.model import CouponTable  # noqa
    from .customer.model import CustomerTable  # noqa

    SQLModel.metadata.create_all(engine)
