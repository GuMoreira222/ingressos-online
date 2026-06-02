from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.payment import Payment, PaymentMethod, PaymentStatus
from schemas.payment import PaymentCreate
from services.notification_service import NotificationService


class PaymentService:
    def __init__(self, notification_service: NotificationService | None = None):
        self.notification_service = notification_service or NotificationService()

    def create_payment(self, db: Session, payment_in: PaymentCreate) -> Payment:
        payment_status = self._resolve_status(payment_in)
        payment = Payment(
            order_id=payment_in.order_id,
            user_id=payment_in.user_id,
            amount=payment_in.amount,
            method=payment_in.method,
            status=payment_status,
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        self.notification_service.publish_payment_event(payment)
        return payment

    def get_payment(self, db: Session, payment_id: int) -> Payment:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
        return payment

    def _resolve_status(self, payment_in: PaymentCreate) -> PaymentStatus:
        if payment_in.force_reject:
            return PaymentStatus.REJECTED
        if payment_in.method == PaymentMethod.BOLETO:
            return PaymentStatus.PENDING
        return PaymentStatus.APPROVED
