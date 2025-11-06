from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from loguru import logger
from sqlmodel.ext.asyncio.session import AsyncSession

from sophia.app.utils.constant import CONSTANT
from sophia.app.utils.security import verift_access_token
from sophia.common.config import settings
from sophia.common.model.user import UserPermType
from sophia.core.db.crud import select_user_by_full_name
from sophia.core.db.models import User
from sophia.core.db.session import LocalSession

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_PREFIX}/user/access-token",
    scopes={
        UserPermType.ADMIN.value: CONSTANT.ROLE_ADMIN_DESCRIPTION,
        UserPermType.USER.value: CONSTANT.ROLE_USER_DESCRIPTION,
        UserPermType.GUEST.value: CONSTANT.ROLE_GUEST_DESCRIPTION,
    },
    auto_error=False,
)


async def get_db() -> AsyncGenerator:
    db = None
    try:
        db = LocalSession()
        yield db
    finally:
        if db:
            await db.close()


async def get_current_user(
    security_scopes: SecurityScopes,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(reusable_oauth2),
) -> User:
    headers = {"WWW-Authenticate": "Bearer"}
    if security_scopes.scopes:
        headers = {"WWW-Authenticate": f'Bearer scope="{security_scopes.scope_str}"'}
    payload = verift_access_token(token=token, headers=headers)
    user = await select_user_by_full_name(db, full_name=payload.username)
    if user is None:
        raise HTTPException(headers=headers, **CONSTANT.RESP_USER_NOT_EXISTS)
    # Check whether the permission of the current user is in the allowed permission list
    if len(security_scopes.scopes) != 0 and not payload.match_scope(
        security_scopes.scopes
    ):
        raise HTTPException(headers=headers, **CONSTANT.RESP_USER_FORBIDDEN)
    return user
