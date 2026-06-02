import json
from core.config import settings
from core.logger import get_logger
from models.payment import Payment


logger = get_logger()


class NotificationService:
    def publish_payment_event(self, payment: Payment) -> None:
        event = {
            "event": f"payment.{payment.status.value}",
            "payment_id": payment.id,
            "order_id": payment.order_id,
            "user_id": payment.user_id,
            "status": payment.status.value,
        }

        if not settings.REDIS_URL:
            logger.info(f"notification.sent {event}")
            return

        try:
            import redis

            client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
            client.xadd("payment-events", event)
            logger.info(f"notification.queued {event}")
        except Exception as exc:
            # Payment cannot fail just because the mocked notification did.
            logger.warning(f"notification.failed payload={json.dumps(event)} error={exc}")
