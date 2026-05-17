from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from models.event import Event
from schemas.event import EventCreate, EventResponse, EventUpdatePrice, EventUpdateQuantity
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
