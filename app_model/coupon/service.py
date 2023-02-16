from datetime import datetime

from sqlmodel import Session

from app_utils.service import Service, NotFound

from .model import CouponTable, CouponCreate, CouponStatus, CouponUpdate


class CouponService(Service[CouponTable, CouponCreate, CouponUpdate, int]):
    """
    Coupon-related services.
    """

    __slots__ = ()

    def __init__(self, session: Session) -> None:
        """
        Initialization.

        Arguments:
            session: The session instance the service will use.
        """
        super().__init__(session, model=CouponTable)

    def status_by_id(self, id: int) -> CouponStatus:
        """
        Returns the current status of the coupon with the given ID.

        Arguments:
            id: Coupon database ID.

        Raises:
            NotFound: If the coupon doesn't exist.
        """
        coupon = self.get_by_pk(id)
        if coupon is None:
            raise NotFound(self._format_primary_key(id))
        return (
            CouponStatus.valid
            if coupon.valid_from <= datetime.utcnow() < coupon.valid_until
            else CouponStatus.invalid
        )
