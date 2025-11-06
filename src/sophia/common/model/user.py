import json
from datetime import datetime, timezone
from enum import StrEnum
from typing import Union

from pydantic import BaseModel, Field

from sophia.core.db.models import User


class UserPermType(StrEnum):
    ADMIN = "ADMIN"
    USER = "USER"
    GUEST = "GUEST"


class Token(BaseModel):
    user_id: str
    access_token: str
    token_type: str
    message: str
    timestamp: datetime
    scopes: list[str]
    status: int


class TokenData(BaseModel):
    id: str
    username: Union[str, None] = None
    scopes: list[str] = []


class TokenPayload(BaseModel):
    userid: str
    username: str
    scopes: list[UserPermType]
    exp: datetime = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        data = self.model_dump()
        scopes: list[UserPermType] = data.get("scopes", [])
        data["scopes"] = [s.value for s in scopes]
        return data

    def match_scope(self, scope: list[str]):
        exp_str = [s.value for s in self.scopes]
        return any(s in scope for s in exp_str)


class UserBasicInfo(BaseModel):
    full_name: str = Field(description="User name")
    password: str = Field(description="User password")
    email: str = Field(default="admin@test.com", description="The email of user")
    scopes: list[UserPermType] = Field(
        default_factory=list, description="The scope for user, include ADMIN, USER, GUEST"
    )

    def build_user(self) -> User:
        return User(
            full_name=self.full_name,
            password=self.password,
            email=self.email,
            scopes=json.dumps([i.value for i in self.scopes]),
            is_superuser=False,
            is_active=True,
        )
