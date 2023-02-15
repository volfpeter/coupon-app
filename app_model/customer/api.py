from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session

from app_utils.service import CommitFailed, NotFound
from app_utils.typing import SessionContextProvider

from .model import Customer, CustomerCreate, CustomerUpdate
from .service import CustomerService


def make_api(
    *,
    session_provider: SessionContextProvider,
    prefix="/customer",
    add_create=True,
    add_delete=True,
    add_get_all=True,
    add_get_by_id=True,
    add_update=True,
) -> APIRouter:
    """
    Customer `APIRouter` factory.

    Arguments:
        session_provider: Session context provider dependency.
        prefix: The prefix for the created `APIRouter`.
        add_create: Whether to add the create route.
        add_delete: Whether to add the delete route.
        add_get_all: Whether to add the get all route.
        add_get_by_id: Whether to add the get by ID route.
        add_update: Whether to add the update route.
    """

    api = APIRouter(prefix=prefix)

    def get_service(session: Session = Depends(session_provider)) -> CustomerService:
        """
        FastAPI dependency that creates a service instance for the API.
        """
        return CustomerService(session)

    if add_get_all:

        @api.get("/", response_model=list[Customer])
        def get_all(service: CustomerService = Depends(get_service)):
            return service.get_all()

    if add_create:

        @api.post("/", response_model=Customer)
        def create(customer: CustomerCreate, service: CustomerService = Depends(get_service)):
            try:
                return service.create(customer)
            except Exception:  # TODO: more specific exception.
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to created customer. Username is probably already in use.",
                )

    if add_get_by_id:

        @api.get("/{id}", response_model=Customer)
        def get_by_id(id: int, service: CustomerService = Depends(get_service)):
            customer = service.get_by_id(id)
            if customer is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")
            return customer

    if add_update:

        @api.put("/{id}", response_model=Customer)
        def update_by_id(id: int, data: CustomerUpdate, service: CustomerService = Depends(get_service)):
            try:
                return service.update(id, data)
            except NotFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")
            except Exception:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer update failed.")

    if add_delete:

        @api.delete("/{id}")
        def delete_by_id(id: int, service: CustomerService = Depends(get_service)):
            try:
                service.delete_by_id(id)
            except NotFound:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")
            except CommitFailed:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to delete customer.")

            return Response(status_code=status.HTTP_200_OK)

    return api
