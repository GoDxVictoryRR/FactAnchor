import uuid
import sys
import os
import asyncio

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SyncSessionLocal
from app.db.models import User
from app.auth.jwt import hash_password
from sqlalchemy import select

def seed_user():
    email = "admin@factanchor.io"
    password = "password123"
    
    session = SyncSessionLocal()
    try:
        # Check if user exists
        stmt = select(User).where(User.email == email)
        user = session.execute(stmt).scalar_one_or_none()
        
        if user:
            print(f"User {email} already exists.")
            # Update password just in case
            user.hashed_password = hash_password(password)
            session.commit()
            print("Password updated.")
        else:
            new_user = User(
                id=uuid.uuid4(),
                email=email,
                hashed_password=hash_password(password),
                is_active=True,
                is_superuser=True
            )
            session.add(new_user)
            session.commit()
            print(f"User {email} created successfully.")
            
    except Exception as e:
        print(f"Error seeding user: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    seed_user()
