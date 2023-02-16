from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session

from app_utils.service import CommitFailed, NotFound
from app_utils.typing import SessionContextProvider

from .model import CustomerCoupon, CustomerCouponCreate
from .service import CustomerCouponService


def make_api(
    *,
    session_provider: SessionContextProvider,
    prefix="/customer-coupon",
    add_create=True,
    add_delete=True,
    add_get_all=True,
    add_get_by_id=True,
) -> APIRouter:
    """
    Customer coupon `APIRouter` factory.

    Arguments:
        session_provider: Session context provider dependency.
        prefix: The prefix for the created `APIRouter`.
        add_create: Whether to add the create route.
        add_delete: Whether to add the delete route.
        add_get_all: Whether to add the get all route.
        add_get_by_id: Whether to add the get by ID route.
    """

    api = APIRouter(prefix=prefix)

    def get_service(session: Session = Depends(session_provider)) -> CustomerCouponService:
        """
        FastAPI dependency that creates a service instance for the API.
        """
        return CustomerCouponService(session)

    if add_get_all:

        @api.get("/", response_model=list[CustomerCoupon])
        def get_all(service: CustomerCouponService = Depends(get_service)):
            return service.get_all()

    if add_create:

        @api.post("/", response_model=CustomerCoupon)
        def create(customer: CustomerCouponCreate, service: CustomerCouponService = Depends(get_service)):
            try:
                return service.create(customer)
            except Exception:  # TODO: more specific exception.
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create customer-coupon link.",
                )

    if add_get_by_id:

        @api.get("/{customer_id}/{coupon_id}", response_model=CustomerCoupon)
        def get_by_id(coupon_id: int, customer_id: int, service: CustomerCouponService = Depends(get_service)):
            customer_coupon = service.get_by_pk({"customer_id": customer_id, "coupon_id": coupon_id})
            if customer_coupon is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer coupon link not found.")
            return customer_coupon

    if add_delete:

        @api.delete("/{customer_id}/{coupon_id}")
        def delete_by_id(coupon_id: int, customer_id: int, service: CustomerCouponService = Depends(get_service)):
            try:
                service.delete_by_pk({"customer_id": customer_id, "coupon_id": coupon_id})
            except NotFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer coupon not found.")
            except CommitFailed:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to delete customer coupon."
                )

            return Response(status_code=status.HTTP_200_OK)

    return api
