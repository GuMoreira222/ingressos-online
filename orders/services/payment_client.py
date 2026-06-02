import httpx
from fastapi import HTTPException, status
from core.config import settings


class PaymentClient:
    def create_payment(self, order_id: int, user_id: str, amount: float, method: str) -> dict:
        url = f"{settings.PAYMENTS_SERVICE_URL}/payments/"
        try:
            response = httpx.post(
                url,
                json={
                    "order_id": order_id,
                    "user_id": user_id,
                    "amount": amount,
                    "method": method,
                },
                timeout=settings.HTTP_TIMEOUT_SECONDS,
            )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Payments service unavailable: {exc}",
            )

        if response.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Payments service failed to create payment")

        return response.json()
