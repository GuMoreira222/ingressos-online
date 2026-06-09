import httpx
from fastapi import HTTPException, status
from tenacity import retry, stop_after_attempt, wait_fixed
from core.config import settings


class EventClient:
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
    def _make_request(self, url: str, quantity: int, idempotency_key: str) -> httpx.Response:
        return httpx.post(
            url,
            json={"quantity": quantity},
            headers={"Idempotency-Key": idempotency_key},
            timeout=settings.HTTP_TIMEOUT_SECONDS,
        )

    def reserve(self, event_id: int, quantity: int, idempotency_key: str) -> dict:
        url = f"{settings.EVENTS_SERVICE_URL}/events/{event_id}/reserve"
        try:
            response = self._make_request(url, quantity, idempotency_key)
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Events service unavailable: {exc}",
            )

        if response.status_code == status.HTTP_409_CONFLICT:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=response.json().get("detail", "Insufficient stock"))
        if response.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
        if response.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Events service failed to reserve tickets")

        return response.json()
