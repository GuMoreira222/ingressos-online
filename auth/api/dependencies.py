from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session
from db.database import get_db
from models.user import User
from core.config import settings
from core.logger import get_logger

logger = get_logger()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("Token validation failed: missing 'sub'")
            raise credentials_exception
    except jwt.PyJWTError as e:
        logger.warning(f"Token validation failed: {str(e)}")
        raise credentials_exception
        
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        logger.warning(f"Token validation failed: user {user_id} not found")
        raise credentials_exception
        
    return user

oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

def get_current_user_optional(token: str | None = Depends(oauth2_scheme_optional), db: Session = Depends(get_db)) -> User | None:
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except jwt.PyJWTError:
        return None
        
    user = db.query(User).filter(User.id == user_id).first()
    return user
