from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from core.logger import get_logger
from core.security import TokenData
from models.order import Order, OrderStatus
from schemas.order import OrderCreate
from services.event_client import EventClient
from services.payment_client import PaymentClient


logger = get_logger()


class OrderService:
    def __init__(
        self,
        event_client: EventClient | None = None,
        payment_client: PaymentClient | None = None,
    ):
        self.event_client = event_client or EventClient()
        self.payment_client = payment_client or PaymentClient()

    def create_order(self, db: Session, order_in: OrderCreate, user: TokenData, idempotency_key: str) -> Order:
        existing_order = db.query(Order).filter(Order.idempotency_key == idempotency_key).first()
        if existing_order:
            if existing_order.user_id != user.user_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Idempotency key already used")
            return existing_order

        order = Order(
            user_id=user.user_id,
            event_id=order_in.event_id,
            quantity=order_in.quantity,
            payment_method=order_in.payment_method,
            idempotency_key=idempotency_key,
        )
        db.add(order)
        db.commit()
        db.refresh(order)

        try:
            reservation = self.event_client.reserve(
                event_id=order.event_id,
                quantity=order.quantity,
                idempotency_key=f"order-{order.id}-{idempotency_key}",
            )
            order.status = OrderStatus.RESERVED
            db.commit()
            db.refresh(order)

            payment = self.payment_client.create_payment(
                order_id=order.id,
                user_id=order.user_id,
                amount=reservation["total_amount"],
                method=order.payment_method.value,
            )
            order.payment_id = payment["id"]
            payment_status = payment["status"]
            if payment_status == "approved":
                order.status = OrderStatus.PAID
            elif payment_status == "pending":
                order.status = OrderStatus.PAYMENT_PENDING
            else:
                order.status = OrderStatus.FAILED
                order.failure_reason = "Payment rejected"
            db.commit()
            db.refresh(order)
            return order
        except HTTPException as exc:
            order.status = OrderStatus.FAILED
            order.failure_reason = str(exc.detail)
            db.commit()
            db.refresh(order)
            logger.warning(f"Order {order.id} failed: {exc.detail}")
            raise

    def get_order(self, db: Session, order_id: int, user: TokenData) -> Order:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        if order.user_id != user.user_id and not user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot access this order")
        return order

    def list_orders(self, db: Session, user: TokenData) -> list[Order]:
        query = db.query(Order)
        if not user.is_admin:
            query = query.filter(Order.user_id == user.user_id)
        return query.order_by(Order.created_at.desc()).all()
