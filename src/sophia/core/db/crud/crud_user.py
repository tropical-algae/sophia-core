import json
import uuid
from copy import deepcopy

from sqlmodel import Session, select

from sophia.app.utils.security import get_password_hash, verify_password
from sophia.core.db.models import User


def select_all_user(db: Session) -> list[User]:
    users = db.exec(select(User)).all()
    return list(users)


def select_user_by_full_name(db: Session, full_name: str | None) -> User | None:
    if full_name:
        user_result = db.exec(select(User).where(User.full_name == full_name)).first()
        return user_result
    return None


def select_user_by_email(db: Session, email: str | None) -> User | None:
    if email:
        user_result = db.exec(select(User).where(User.email == email)).first()
        return user_result
    return None


def create_user(db: Session, user: User):
    user.password = get_password_hash(user.password)
    user.id = user.id or uuid.uuid4().hex

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, *, user_id: str, update_attr: dict) -> User | None:
    user = db.get(User, ident=user_id)
    if user:
        user.email = update_attr.get("email", user.email)
        user.password = (
            get_password_hash(update_attr["password"])
            if update_attr.get("passwd")
            else user.password
        )
        user.full_name = update_attr.get("full_name", user.full_name)

        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    return None
