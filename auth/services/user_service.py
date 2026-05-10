from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.user import User, RoleEnum
from schemas.user import UserCreate
from core.security import get_password_hash
from core.logger import get_logger

logger = get_logger()

def create_user(db: Session, user_in: UserCreate, current_user: User | None = None) -> User:
    logger.info(f"Attempting to create user with email: {user_in.email}")
    db_user = db.query(User).filter(User.email == user_in.email).first()
    if db_user:
        logger.warning(f"User creation failed: email {user_in.email} already registered")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    hashed_password = get_password_hash(user_in.password)
    
    # Logic for admin creation
    final_role = RoleEnum.USER
    if current_user and current_user.role == RoleEnum.ADMIN:
        final_role = user_in.role or RoleEnum.USER
        
    new_user = User(
        email=user_in.email,
        password_hash=hashed_password,
        role=final_role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"User created successfully: {new_user.id} ({new_user.email}) with role {final_role}")
    return new_user

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()
