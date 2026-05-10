from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.user import User
from schemas.user import Token
from services.user_service import get_user_by_email
from core.security import verify_password, create_access_token
from core.logger import get_logger

logger = get_logger()

def authenticate_user(db: Session, email: str, password: str) -> Token:
    logger.info(f"Authentication attempt for email: {email}")
    db_user = get_user_by_email(db, email)
    
    if not db_user:
        logger.warning(f"Authentication failed: user {email} not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
        
    if not verify_password(password, db_user.password_hash):
        logger.warning(f"Authentication failed: incorrect password for user {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
        
    logger.info(f"User {email} authenticated successfully. Generating token.")
    
    access_token = create_access_token(data={"sub": str(db_user.id), "role": db_user.role.value})
    
    return Token(access_token=access_token, token_type="bearer")
