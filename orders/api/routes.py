from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session
from core.security import TokenData, get_current_user
from db.database import get_db
from schemas.order import OrderCreate, OrderResponse
from services.order_service import OrderService


router = APIRouter()


def get_order_service() -> OrderService:
    return OrderService()


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_in: OrderCreate,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
):
    return service.create_order(db=db, order_in=order_in, user=current_user, idempotency_key=idempotency_key)


@router.get("/", response_model=list[OrderResponse])
def list_orders(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
):
    return service.list_orders(db=db, user=current_user)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
):
    return service.get_order(db=db, order_id=order_id, user=current_user)
