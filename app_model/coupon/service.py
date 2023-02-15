from sqlmodel import Session

from app_utils.service import Service

from .model import CouponTable, CouponCreate, CouponUpdate


class CouponService(Service[CouponTable, CouponCreate, CouponUpdate]):
    """
    Coupon-related services.
    """

    def __init__(self, session: Session) -> None:
        """
        Initialization.

        Arguments:
            session: The session instance the service will use.
        """
        super().__init__(session, model=CouponTable)
