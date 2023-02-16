from typing import Mapping, TypedDict

from sqlmodel import Session

from app_utils.service import Service

from .model import CustomerCouponTable, CustomerCouponCreate, CustomerCouponUpdate


class CustomerCouponKey(TypedDict):
    customer_id: int
    coupon_id: int


class CustomerCouponService(
    Service[CustomerCouponTable, CustomerCouponCreate, CustomerCouponUpdate, tuple[int, int] | Mapping[str, int]]
):
    """
    Customer coupon service.
    """

    __slots__ = ()

    def __init__(self, session: Session) -> None:
        super().__init__(session, model=CustomerCouponTable)
