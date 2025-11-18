from collections.abc import AsyncGenerator, Awaitable, Callable

from fastapi import Depends, Header, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from sqlmodel.ext.asyncio.session import AsyncSession

from sophia.app.services.session_service import create_session
from sophia.app.utils.constant import CONSTANT
from sophia.app.utils.security import verift_access_token
from sophia.common.config import settings
from sophia.common.logging import logger
from sophia.core.db.crud import select_user_by_full_name
from sophia.core.db.crud.session_crud import select_session_by_id_and_user
from sophia.core.db.models import UserAccount
from sophia.core.db.session import LocalSession
from sophia.core.model.message import ChatSessionRequest
from sophia.core.model.user import ScopeType

AUTHENTICATE_HEADER = "WWW-Authenticate"
SESSION_HEADER = "X-Session-Id"


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_PREFIX}/user/access-token",
    scopes={
        ScopeType.ADMIN.value: CONSTANT.ROLE_ADMIN_DESCRIPTION,
        ScopeType.USER.value: CONSTANT.ROLE_USER_DESCRIPTION,
        ScopeType.GUEST.value: CONSTANT.ROLE_GUEST_DESCRIPTION,
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
) -> UserAccount:
    headers = {AUTHENTICATE_HEADER: "Bearer"}
    if security_scopes.scopes:
        headers = {AUTHENTICATE_HEADER: f'Bearer scope="{security_scopes.scope_str}"'}
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


def get_session_id(
    scopes: list[str] | None = None, auto_create_session: bool = False
) -> Callable[..., Awaitable[ChatSessionRequest]]:
    async def _get_session_id(
        user: UserAccount = Security(get_current_user, scopes=scopes),
        db: AsyncSession = Depends(get_db),
        sid_header: str | None = Header(default=None, alias=SESSION_HEADER),
    ) -> ChatSessionRequest:
        # create new session when header is None
        if sid_header is None:
            if not auto_create_session:
                raise HTTPException(**CONSTANT.RESP_USER_SESSION_NULL)
            session_id: str = await create_session(db=db, user=user)
            return ChatSessionRequest(
                session_id=session_id, user=user, is_new_session=True
            )

        # When header is not None, select the session status
        result = await select_session_by_id_and_user(
            db=db, id=sid_header, user_id=user.id
        )
        if result is None:
            raise HTTPException(**CONSTANT.RESP_USER_SESSION_NOT_EXISTS)
        return ChatSessionRequest(session_id=sid_header, user=user, is_new_session=False)

    return _get_session_id
