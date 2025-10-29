# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from app import models
# from passlib.context import CryptContext
# from app.models.user import User
# from app.schemas.user import UserCreate
# from app.crud.user import verify_password

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# async def get_user(db: AsyncSession, username: str):
#     result = await db.execute(select(User).where(User.username == username))
#     return result.scalars().first()


# # async def create_user(db: AsyncSession, user_data):
# #     hashed_password = pwd_context.hash(user_data.password)
# #     db_user = models.User(email=user_data.email, hashed_password=hashed_password, is_active=True)
# #     db.add(db_user)
# #     await db.commit()
# #     await db.refresh(db_user)
# #     return db_user

# async def create_user(db: AsyncSession, user: UserCreate):
#     hashed_password = verify_password(user.password)
#     new_user = User(
#         email=user.email,
#         hashed_password=hashed_password,
#         username=user.username,  # <- здесь None недопустимо!
#         is_active=True,
#     )
#     db.add(new_user)
#     await db.commit()
#     await db.refresh(new_user)
#     return new_user


# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)




from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.user import UserCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_user(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def create_user(db: AsyncSession, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        hashed_password=hashed_password,
        username=user.username,
        is_active=True,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
