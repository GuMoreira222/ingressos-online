import pytest
from fastapi import HTTPException, status
from core.security import TokenData
from models.order import OrderStatus
from schemas.order import OrderCreate
from services.order_service import OrderService


class FakeEventClient:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.calls = 0

    def reserve(self, event_id: int, quantity: int, idempotency_key: str) -> dict:
        self.calls += 1
        if self.should_fail:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Estoque insuficiente")
        return {"event_id": event_id, "reserved_quantity": quantity}


class FakePaymentClient:
    def __init__(self, payment_status="approved"):
        self.payment_status = payment_status
        self.calls = 0

    def create_payment(self, order_id: int, user_id: str, amount: float, method: str) -> dict:
        self.calls += 1
        return {"id": 99, "status": self.payment_status}


def test_create_order_success(db_session):
    event_client = FakeEventClient()
    payment_client = FakePaymentClient()
    service = OrderService(event_client=event_client, payment_client=payment_client)

    order = service.create_order(
        db=db_session,
        order_in=OrderCreate(event_id=1, quantity=2, payment_method="pix"),
        user=TokenData(user_id="user-1", role="user"),
        idempotency_key="order-key-1",
    )

    assert order.status == OrderStatus.PAID
    assert order.payment_id == 99
    assert event_client.calls == 1
    assert payment_client.calls == 1


def test_create_order_idempotency_returns_same_order(db_session):
    event_client = FakeEventClient()
    payment_client = FakePaymentClient()
    service = OrderService(event_client=event_client, payment_client=payment_client)
    order_in = OrderCreate(event_id=1, quantity=2, payment_method="pix")
    user = TokenData(user_id="user-1", role="user")

    first_order = service.create_order(db_session, order_in, user, "same-key")
    second_order = service.create_order(db_session, order_in, user, "same-key")

    assert second_order.id == first_order.id
    assert event_client.calls == 1
    assert payment_client.calls == 1


def test_create_order_fails_when_stock_is_insufficient(db_session):
    service = OrderService(event_client=FakeEventClient(should_fail=True), payment_client=FakePaymentClient())

    with pytest.raises(HTTPException) as exc:
        service.create_order(
            db=db_session,
            order_in=OrderCreate(event_id=1, quantity=99, payment_method="pix"),
            user=TokenData(user_id="user-1", role="user"),
            idempotency_key="stock-fail",
        )

    assert exc.value.status_code == status.HTTP_409_CONFLICT
    assert exc.value.detail == "Estoque insuficiente"


def test_create_order_with_boleto_stays_pending(db_session):
    service = OrderService(event_client=FakeEventClient(), payment_client=FakePaymentClient("pending"))

    order = service.create_order(
        db=db_session,
        order_in=OrderCreate(event_id=1, quantity=1, payment_method="boleto"),
        user=TokenData(user_id="user-1", role="user"),
        idempotency_key="boleto-key",
    )

    assert order.status == OrderStatus.PAYMENT_PENDING


def test_user_cannot_read_other_user_order(db_session):
    service = OrderService(event_client=FakeEventClient(), payment_client=FakePaymentClient())
    admin_order = service.create_order(
        db=db_session,
        order_in=OrderCreate(event_id=1, quantity=1, payment_method="pix"),
        user=TokenData(user_id="admin-1", role="admin"),
        idempotency_key="admin-order",
    )

    with pytest.raises(HTTPException) as exc:
        service.get_order(db=db_session, order_id=admin_order.id, user=TokenData(user_id="user-1", role="user"))

    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
