from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from db.database import get_db
from schemas.payment import PaymentCreate, PaymentResponse
from services.payment_service import PaymentService


router = APIRouter()


def get_payment_service() -> PaymentService:
    return PaymentService()


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment_in: PaymentCreate,
    db: Session = Depends(get_db),
    service: PaymentService = Depends(get_payment_service),
):
    return service.create_payment(db=db, payment_in=payment_in)


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    service: PaymentService = Depends(get_payment_service),
):
    return service.get_payment(db=db, payment_id=payment_id)
