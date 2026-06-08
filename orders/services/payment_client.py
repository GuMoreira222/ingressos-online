import httpx
from fastapi import HTTPException, status
from tenacity import retry, stop_after_attempt, wait_fixed
from core.config import settings


class PaymentClient:
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
    def _make_request(self, url: str, order_id: int, user_id: str, amount: float, method: str) -> httpx.Response:
        return httpx.post(
            url,
            json={
                "order_id": order_id,
                "user_id": user_id,
                "amount": amount,
                "method": method,
            },
            timeout=settings.HTTP_TIMEOUT_SECONDS,
        )

    def create_payment(self, order_id: int, user_id: str, amount: float, method: str) -> dict:
        url = f"{settings.PAYMENTS_SERVICE_URL}/payments/"
        try:
            response = self._make_request(url, order_id, user_id, amount, method)
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Payments service unavailable: {exc}",
            )

        if response.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Payments service failed to create payment")

        return response.json()
