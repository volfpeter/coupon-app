from datetime import datetime, timedelta

from sqlmodel import Session

from app.app import get_database_engine
from app_model import initialize_database
from app_model.coupon.model import CouponTable, CouponCreate, DiscountType
from app_model.customer.model import CustomerTable, CustomerCreate


def run_fixture():
    """
    Executes the demo fixture.
    """
    engine = get_database_engine()
    initialize_database(engine)

    now = datetime.utcnow()

    with Session(engine) as session:
        # -- Clear database
        for table in (CouponTable, CustomerTable):
            session.query(table).delete()
            session.commit()

        # -- Create customers.

        session.add_all(
            [CustomerTable.from_orm(CustomerCreate(name=f"Customer {i}", username=f"customer{i}")) for i in range(10)]
        )

        session.commit()

        # -- Create tables.

        session.add_all(
            [
                CouponTable.from_orm(
                    CouponCreate(
                        code=f"ABCDEFG{i}",
                        description="Fancy coupon {i}",
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
