import httpx
from fastapi import HTTPException, status
from core.config import settings


class EventClient:
    def reserve(self, event_id: int, quantity: int, idempotency_key: str) -> dict:
        url = f"{settings.EVENTS_SERVICE_URL}/events/{event_id}/reserve"
        try:
            response = httpx.post(
                url,
                json={"quantity": quantity},
                headers={"Idempotency-Key": idempotency_key},
                timeout=settings.HTTP_TIMEOUT_SECONDS,
            )
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
