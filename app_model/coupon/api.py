from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session

from app_utils.service import CommitFailed, NotFound
from app_utils.typing import SessionContextProvider

from .model import Coupon, CouponCreate, CouponStatus, CouponStatusResponse, CouponUpdate
from .service import CouponService


def make_api(
    *,
    session_provider: SessionContextProvider,
    prefix="/coupon",
    add_create=True,
    add_delete=True,
    add_get_all=True,
    add_get_by_id=True,
    add_status=True,
    add_update=True,
) -> APIRouter:
    """
    Coupon `APIRouter` factory.

    Arguments:
        session_provider: Session context provider dependency.
        prefix: The prefix for the created `APIRouter`.
        add_create: Whether to add the create route.
        add_delete: Whether to add the delete route.
        add_get_all: Whether to add the get all route.
        add_get_by_id: Whether to add the get by ID route.
        add_status: Whether to add the `{id}/status` route.
        add_update: Whether to add the update route.
    """

    api = APIRouter(prefix=prefix)

    def get_service(session: Session = Depends(session_provider)) -> CouponService:
        """
        FastAPI dependency that creates a service instance for the API.
        """
        return CouponService(session)

    if add_get_all:

        @api.get("/", response_model=list[Coupon])
        def get_all(service: CouponService = Depends(get_service)):
            return service.get_all()

    if add_create:

        @api.post("/", response_model=Coupon)
        def create(coupon: CouponCreate, service: CouponService = Depends(get_service)):
            try:
                return service.create(coupon)
            except Exception:  # TODO: more specific exception.
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to created coupon. Username is probably already in use.",
                )

    if add_get_by_id:

        @api.get("/{id}", response_model=Coupon)
        def get_by_id(id: int, service: CouponService = Depends(get_service)):
            coupon = service.get_by_id(id)
            if coupon is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coupon not found.")
            return coupon

    if add_update:

        @api.put("/{id}", response_model=Coupon)
        def update_by_id(id: int, data: CouponUpdate, service: CouponService = Depends(get_service)):
            try:
                return service.update(id, data)
            except NotFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coupon not found.")
            except Exception:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Coupon update failed.")

    if add_delete:

        @api.delete("/{id}")
        def delete_by_id(id: int, service: CouponService = Depends(get_service)):
            try:
                service.delete_by_id(id)
            except NotFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coupon not found.")
            except CommitFailed:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to delete coupon.")

            return Response(status_code=status.HTTP_200_OK)

    if add_status:

        @api.get("/{id}/status", response_model=CouponStatusResponse)
        def coupon_status(id: int, service: CouponService = Depends(get_service)):
            """
            Returns the status of the coupon with the given ID at the time of the request.
            """
            coupon = service.get_by_id(id)
            if coupon is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coupon not found.")

            now = datetime.utcnow()
            return CouponStatusResponse(
                status=CouponStatus.valid if coupon.valid_from <= now <= coupon.valid_until else CouponStatus.invalid
            )

    return api
