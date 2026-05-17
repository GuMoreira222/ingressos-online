import pytest
from datetime import datetime, timedelta, timezone

# Helper data
valid_event_payload = {
    "name": "Teste Event",
    "date": (datetime.now(timezone.utc) + timedelta(days=10)).isoformat(),
    "price": 100.0,
    "available_quantity": 50
}

def test_create_event_success(admin_client):
    response = admin_client.post("/events/", json=valid_event_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Teste Event"
    assert data["price"] == 100.0
    assert data["available_quantity"] == 50
    assert "id" in data

def test_create_event_unauthorized(client):
    response = client.post("/events/", json=valid_event_payload)
    assert response.status_code in [401, 403]

def test_list_events_public(client, admin_client):
    # First create an event using admin
    admin_client.post("/events/", json=valid_event_payload)
    
    # Then get as public client
    response = client.get("/events/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Teste Event"

def test_update_event_quantity(admin_client):
    # Create event
    create_resp = admin_client.post("/events/", json=valid_event_payload)
    event_id = create_resp.json()["id"]
    
    # Update quantity
    response = admin_client.patch(f"/events/{event_id}/quantity", json={"available_quantity": 100})
    assert response.status_code == 200
    assert response.json()["available_quantity"] == 100

def test_update_event_price(admin_client):
    create_resp = admin_client.post("/events/", json=valid_event_payload)
    event_id = create_resp.json()["id"]
    
    response = admin_client.patch(f"/events/{event_id}/price", json={"price": 250.0})
    assert response.status_code == 200
    assert response.json()["price"] == 250.0

def test_reserve_tickets_success(admin_client, client):
    create_resp = admin_client.post("/events/", json=valid_event_payload)
    event_id = create_resp.json()["id"]
    
    # Reserve tickets (public route, no auth needed for this internal API simulation)
    headers = {"Idempotency-Key": "test-key-1"}
    response = client.post(f"/events/{event_id}/reserve", json={"quantity": 2}, headers=headers)
    assert response.status_code == 200
    assert response.json()["reserved_quantity"] == 2
    
    # Verify stock dropped
    get_resp = client.get("/events/")
    assert get_resp.json()[0]["available_quantity"] == 48

def test_reserve_tickets_not_found(client):
    headers = {"Idempotency-Key": "test-key-2"}
    response = client.post("/events/999/reserve", json={"quantity": 1}, headers=headers)
    assert response.status_code == 404

def test_reserve_tickets_insufficient_stock(admin_client, client):
    create_resp = admin_client.post("/events/", json=valid_event_payload)
    event_id = create_resp.json()["id"]
    
    headers = {"Idempotency-Key": "test-key-3"}
    # Try to buy more than available (50)
    response = client.post(f"/events/{event_id}/reserve", json={"quantity": 51}, headers=headers)
    assert response.status_code == 409
    assert "Estoque insuficiente" in response.json()["detail"]

def test_reserve_tickets_idempotency(admin_client, client):
    create_resp = admin_client.post("/events/", json=valid_event_payload)
    event_id = create_resp.json()["id"]
    
    headers = {"Idempotency-Key": "idemp-key-same"}
    
    # First request
    response1 = client.post(f"/events/{event_id}/reserve", json={"quantity": 10}, headers=headers)
    assert response1.status_code == 200
    
    # Second request with identical key
    response2 = client.post(f"/events/{event_id}/reserve", json={"quantity": 10}, headers=headers)
    assert response2.status_code == 200
    assert "já processada" in response2.json()["message"]
    
    # Ensure it only subtracted once (50 - 10 = 40)
    get_resp = client.get("/events/")
    assert get_resp.json()[0]["available_quantity"] == 40
