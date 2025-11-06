import uuid

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from sophia.app.utils.security import get_password_hash, verify_password
from sophia.core.db.models import User


async def select_all_user(db: AsyncSession) -> list[User]:
    users = await db.exec(select(User))
    return list(users.all())


async def select_user_by_full_name(
    db: AsyncSession, full_name: str | None
) -> User | None:
    if full_name:
        user_result = await db.exec(select(User).where(User.full_name == full_name))
        return user_result.first()
    return None


async def select_user_by_email(db: AsyncSession, email: str | None) -> User | None:
    if email:
        user_result = await db.exec(select(User).where(User.email == email))
        return user_result.first()
    return None


async def create_user(db: AsyncSession, user: User):
    user.password = get_password_hash(user.password)
    user.id = user.id or uuid.uuid4().hex

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# async def update_user(db: AsyncSession, user_id: str, update_attr: dict) -> User | None:
#     user = await db.get(User, ident=user_id)
#     if user:
#         user.email = update_attr.get("email", user.email)
#         user.password = (
#             get_password_hash(update_attr["password"])
#             if update_attr.get("passwd")
#             else user.password
#         )
#         user.full_name = update_attr.get("full_name", user.full_name)

#         db.add(user)
#         await db.commit()
#         await db.refresh(user)
#         return user
#     return None
