import os
import time

import redis

from core.logger import get_logger
from db.database import SessionLocal
from models.order import Order, OrderStatus


logger = get_logger()
STREAM_NAME = "payment-events"


def update_order_status(order_id: int, payment_status: str) -> None:
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            logger.warning(f"orders_worker.order_not_found order_id={order_id}")
            return

        if payment_status == "approved":
            order.status = OrderStatus.PAID
            order.failure_reason = None
        elif payment_status == "rejected":
            order.status = OrderStatus.FAILED
            order.failure_reason = "Payment rejected"
        else:
            return

        db.commit()
        logger.info(f"orders_worker.order_updated order_id={order_id} status={order.status.value}")
    finally:
        db.close()


def process_event(fields: dict) -> None:
    event_name = fields.get("event", "")
    if not event_name.startswith("payment."):
        return

    order_id = fields.get("order_id")
    payment_status = fields.get("status")
    if not order_id or not payment_status:
        logger.warning(f"orders_worker.invalid_event payload={fields}")
        return

    update_order_status(int(order_id), payment_status)


def main() -> None:
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        logger.warning("orders_worker.redis_url_missing")
        return

    client = redis.Redis.from_url(redis_url, decode_responses=True)
    last_id = "0-0"
    logger.info("orders_worker.started")

    while True:
        try:
            messages = client.xread({STREAM_NAME: last_id}, count=10, block=5000)
            for _, entries in messages:
                for message_id, fields in entries:
                    last_id = message_id
                    process_event(fields)
        except Exception as exc:
            logger.warning(f"orders_worker.failed error={exc}")
            time.sleep(2)


if __name__ == "__main__":
    main()
