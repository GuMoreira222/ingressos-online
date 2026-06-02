from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from db.database import get_db
from models.event import Event
from models.idempotency import IdempotencyKey
from schemas.event import EventCreate, EventResponse, EventUpdatePrice, EventUpdateQuantity, EventReserveRequest, EventReserveResponse
from core.security import get_current_admin, TokenData

router = APIRouter()

@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event: EventCreate, 
    db: Session = Depends(get_db), 
    admin: TokenData = Depends(get_current_admin)
):
    db_event = Event(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@router.get("/", response_model=List[EventResponse])
def list_events(db: Session = Depends(get_db)):
    events = db.query(Event).all()
    return events

@router.patch("/{event_id}/quantity", response_model=EventResponse)
def update_event_quantity(
    event_id: int, 
    update_data: EventUpdateQuantity, 
    db: Session = Depends(get_db), 
    admin: TokenData = Depends(get_current_admin)
):
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    db_event.available_quantity = update_data.available_quantity
    db.commit()
    db.refresh(db_event)
    return db_event

@router.patch("/{event_id}/price", response_model=EventResponse)
def update_event_price(
    event_id: int, 
    update_data: EventUpdatePrice, 
    db: Session = Depends(get_db), 
    admin: TokenData = Depends(get_current_admin)
):
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    db_event.price = update_data.price
    db.commit()
    db.refresh(db_event)
    return db_event

@router.post("/{event_id}/reserve", response_model=EventReserveResponse)
def reserve_tickets(
    event_id: int, 
    reserve_data: EventReserveRequest, 
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: Session = Depends(get_db)
):
    # 1. Verificar idempotência
    existing_key = db.query(IdempotencyKey).filter(IdempotencyKey.key == idempotency_key).first()
    if existing_key:
        # Se a chave já foi processada, retorna sucesso (simulando que a transação foi aceita)
        return EventReserveResponse(
            message="Reserva já processada anteriormente (Idempotency).",
            event_id=event_id,
            reserved_quantity=reserve_data.quantity
        )

    # 2. Lock no Evento para evitar overselling (with_for_update)
    db_event = db.query(Event).filter(Event.id == event_id).with_for_update().first()
    
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    if db_event.available_quantity < reserve_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=f"Estoque insuficiente. Disponível: {db_event.available_quantity}"
        )
        
    # 3. Abater a quantidade
    db_event.available_quantity -= reserve_data.quantity
    
    # 4. Registrar a chave de idempotência
    new_idem_key = IdempotencyKey(key=idempotency_key)
    db.add(new_idem_key)
    
    # 5. Commit da transação (libera o lock do banco)
    try:
        db.commit()
    except IntegrityError:
        # Fallback caso a chave de idempotência tenha sido inserida por outra thread exata no mesmo momento
        db.rollback()
        return EventReserveResponse(
            message="Reserva já processada anteriormente (Idempotency - Fallback).",
            event_id=event_id,
            reserved_quantity=reserve_data.quantity
        )
        
    return EventReserveResponse(
        message="Reserva realizada com sucesso.",
        event_id=event_id,
        reserved_quantity=reserve_data.quantity
    )
