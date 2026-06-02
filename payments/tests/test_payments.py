from models.payment import PaymentStatus
from schemas.payment import PaymentCreate
from services.payment_service import PaymentService


class FakeNotificationService:
    def __init__(self):
        self.events = []

    def publish_payment_event(self, payment):
        self.events.append(payment)


def test_pix_payment_is_approved(db_session):
    notification_service = FakeNotificationService()
    service = PaymentService(notification_service=notification_service)

    payment = service.create_payment(
        db_session,
        PaymentCreate(order_id=1, user_id="user-1", amount=120.0, method="pix"),
    )

    assert payment.status == PaymentStatus.APPROVED
    assert notification_service.events == [payment]


def test_boleto_payment_is_pending(db_session):
    service = PaymentService(notification_service=FakeNotificationService())

    payment = service.create_payment(
        db_session,
        PaymentCreate(order_id=1, user_id="user-1", amount=120.0, method="boleto"),
    )

    assert payment.status == PaymentStatus.PENDING


def test_credit_card_payment_can_be_rejected(db_session):
    service = PaymentService(notification_service=FakeNotificationService())

    payment = service.create_payment(
        db_session,
        PaymentCreate(
            order_id=1,
            user_id="user-1",
            amount=120.0,
            method="credit_card",
            force_reject=True,
        ),
    )

    assert payment.status == PaymentStatus.REJECTED


def test_get_payment_by_id(db_session):
    service = PaymentService(notification_service=FakeNotificationService())
    created = service.create_payment(
        db_session,
        PaymentCreate(order_id=1, user_id="user-1", amount=120.0, method="pix"),
    )

    payment = service.get_payment(db_session, created.id)

    assert payment.id == created.id
