#!/usr/bin/env python3
"""Create a test user and print a JWT token for Golden Demo testing."""
import asyncio
import uuid
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.auth.jwt import create_access_token
from app.db.session import AsyncSessionLocal
from app.db.models import User
from sqlalchemy import select


async def main():
    user_id = uuid.uuid4()
    email = "demo@factanchor.test"
    # Pre-computed bcrypt hash for "test1234"
    password_hash = "$2b$12$LJ3xF1R8ZsQZ.z5g.4f.aeQ5iGw5j2QWQX0l3VmYV5F3r6Gy.q5G"

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == email))
        existing = result.scalar_one_or_none()

        if existing:
            user_id = existing.id
        else:
            user = User(
                id=user_id,
                email=email,
                hashed_password=password_hash,
                is_active=True,
                is_superuser=False,
            )
            session.add(user)
            await session.commit()

    token = create_access_token(str(user_id))
    print(f"TOKEN={token}")


if __name__ == "__main__":
    asyncio.run(main())
