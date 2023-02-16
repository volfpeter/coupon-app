from datetime import datetime, timedelta
import random

from sqlmodel import Session, select

from app.app import get_database_engine
from app.settings import get_settings

from app_model import initialize_database
from app_model.coupon.model import CouponTable, CouponCreate, DiscountType
from app_model.customer.model import CustomerTable, CustomerCreate
from app_model.customer_coupon.model import CustomerCouponTable


def run_fixture():
    """
    Executes the demo fixture.
    """
    engine = get_database_engine(get_settings())
    initialize_database(engine)

    now = datetime.utcnow()

    with Session(engine) as session:
        # -- Clear database
        for table in (CouponTable, CustomerTable):
            session.query(table).delete()
            session.commit()

        # -- Create customers.

        session.add_all(
            [
                CustomerTable.from_orm(
                    CustomerCreate(
                        name=f"Customer {i}",
                        username=f"customer{i}",
                    )
                )
                for i in range(10)
            ]
        )

        session.commit()

        # -- Create tables.

        session.add_all(
            [
                CouponTable.from_orm(
                    CouponCreate(
                        code=f"ABCDEFG{i}",
                        description=f"Fancy coupon {i}",
                        discount=42,
                        discount_type=DiscountType.fix,
                        valid_from=now + timedelta(days=7 + 2 * i),
                        valid_until=now + timedelta(days=14 + 2 * 2),
                    )
                )
                for i in range(20)
            ]
        )

        session.commit()

        # -- Customer coupons

        all_coupons = session.exec(select(CouponTable)).all()

        def get_random_coupons() -> list[CouponTable]:
            return random.sample(all_coupons, 3)

        for customer in session.exec(select(CustomerTable)).all():
            session.add_all(
                [
                    CustomerCouponTable(
                        customer_id=customer.id,
                        coupon_id=coupon.id,
                    )
                    for coupon in get_random_coupons()
                ]
            )

        session.commit()
