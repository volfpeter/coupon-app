from sqlmodel import Field, SQLModel


class BaseCustomerCoupon(SQLModel):
    """
    Base customer coupon model with shared attributes.
    """

    customer_id: int = Field(foreign_key="customer.id", primary_key=True)
    coupon_id: int = Field(foreign_key="coupon.id", primary_key=True)


class CustomerCouponTable(BaseCustomerCoupon, table=True):
    """
    Customer-coupon link.
    """

    __tablename__ = "customer_coupon"


class CustomerCoupon(BaseCustomerCoupon):
    """
    Customer coupon model.
    """

    ...


class CustomerCouponCreate(BaseCustomerCoupon):
    """
    Customer coupon creation model.
    """

    ...


class CustomerCouponUpdate(SQLModel):
    """
    Customer coupon update model.
    """

    ...
