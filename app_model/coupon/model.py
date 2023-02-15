from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel

from app_utils.typing import UTCDatetime


class DiscountType(str, Enum):
    """
    Discount types enum.
    """

    fix = "fix"
    percent = "percent"


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
    valid_from: UTCDatetime
    valid_until: UTCDatetime


class CouponTable(BaseCoupon, table=True):
    """
    Coupon database model.
    """

    __tablename__ = "coupons"

    id: int | None = Field(default=None, primary_key=True)
    created_at: UTCDatetime | None = Field(default_factory=datetime.utcnow)


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
