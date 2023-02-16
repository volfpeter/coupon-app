from typing import TYPE_CHECKING

from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel

from app_model.customer_coupon.model import CustomerCouponTable
from app_utils.typing import UTCDatetime

if TYPE_CHECKING:
    from app_model.customer.model import CustomerTable


class DiscountType(str, Enum):
    """
    Discount types enum.
    """

    fix = "fix"
    percent = "percent"


class CouponStatus(str, Enum):
    """
    Coupon status enum.
    """

    valid = "valid"
    invalid = "invalid"


class CouponStatusResponse(BaseModel):
    """
    Coupon status response model.
    """

    status: CouponStatus


class BaseCoupon(SQLModel):
    """
    Base coupon model with shared attributes.
    """

    code: str = Field(
        unique=True, regex=r"[A-Z]+[A-Z0-9]{3,}"
    )  # At least 4 capital alphanumeric characters, starting with A-Z.
    description: str
    discount: float = Field(gt=0)
    discount_type: DiscountType
    valid_from: UTCDatetime  # Inclusive
    valid_until: UTCDatetime  # Exclusive


class CouponTable(BaseCoupon, table=True):
    """
    Coupon database model.
    """

    __tablename__ = "coupon"

    id: int | None = Field(default=None, primary_key=True)
    created_at: UTCDatetime | None = Field(default_factory=datetime.utcnow)

    customers: list["CustomerTable"] = Relationship(back_populates="coupons", link_model=CustomerCouponTable)


class Coupon(BaseCoupon):
    """
    Coupon model.
    """

    id: int
    created_at: UTCDatetime


class CouponCreate(BaseCoupon):
    """
    Coupon creation model.
    """

    ...


class CouponUpdate(SQLModel):
    """
    Coupon update model.
    """

    description: str | None
    valid_until: UTCDatetime | None
