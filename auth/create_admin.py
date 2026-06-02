import os
import sys
from dotenv import load_dotenv

load_dotenv()

from db.database import SessionLocal, engine
from models.user import User, RoleEnum, Base
from core.security import get_password_hash

try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database tables already initialized or being initialized in create_admin: {e}")

def create_admin():
    email = os.getenv("USER_ADMIN")
    password = os.getenv("PASSWORD")
    
    if not email or not password:
        print("Erro: USER_ADMIN e PASSWORD devem estar preenchidos no .env")
        sys.exit(1)
        
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            if existing_user.role == RoleEnum.ADMIN:
                print(f"O admin '{email}' já existe!")
            else:
                existing_user.role = RoleEnum.ADMIN
                db.commit()
                print(f"O usuário '{email}' foi promovido a ADMIN.")
            return

        hashed_password = get_password_hash(password)
        new_admin = User(
            email=email,
            password_hash=hashed_password,
            role=RoleEnum.ADMIN
        )
        db.add(new_admin)
        db.commit()
        print(f"Administrador '{email}' criado com sucesso!")
        
    except Exception as e:
        print(f"Erro ao criar admin: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
