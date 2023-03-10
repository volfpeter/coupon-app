from typing import TYPE_CHECKING

from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel

from app_model.customer_coupon.model import CustomerCouponTable
from app_utils.typing import UTCDatetime


if TYPE_CHECKING:
    from app_model.coupon.model import CouponTable


class BaseCustomer(SQLModel):
    """
    Base customer model with shared attributes.
    """

    username: str = Field(
        index=True, unique=True, regex=r"[a-z]+[a-z0-9-.]{2,}"
    )  # At least 3 alphanumeric characters, starting with a-z.
    name: str = Field(index=True)


class CustomerTable(BaseCustomer, table=True):
    """
    Customer database model.
    """

    __tablename__ = "customer"

    id: int | None = Field(default=None, primary_key=True)
    created_at: UTCDatetime | None = Field(default_factory=datetime.utcnow)

    coupons: list["CouponTable"] = Relationship(back_populates="customers", link_model=CustomerCouponTable)


class Customer(BaseCustomer):
    """
    Customer model.
    """

    id: int
    created_at: UTCDatetime


class CustomerCreate(BaseCustomer):
    """
    Customer creation model.
    """

    ...


class CustomerUpdate(SQLModel):
    """
    Customer update model.
    """

    name: str | None
