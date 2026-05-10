from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from db.database import get_db
from schemas.user import UserCreate, UserRead, Token
from services.user_service import create_user
from services.auth_service import authenticate_user
from api.dependencies import get_current_user, get_current_user_optional
from models.user import User

router = APIRouter()

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, current_user: User | None = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    return create_user(db=db, user_in=user_in, current_user=current_user)

@router.post("/login", response_model=Token)
def login(credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return authenticate_user(db=db, email=credentials.username, password=credentials.password)

@router.get("/me", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
