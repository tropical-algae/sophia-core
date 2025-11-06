import json
from datetime import datetime, timedelta
from typing import Any

import pytz
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from sophia.app.api.deps import get_current_user, get_db
from sophia.app.utils import security
from sophia.app.utils.constant import CONSTANT
from sophia.common.config import settings
from sophia.common.model.user import Token, TokenPayload, UserBasicInfo
from sophia.core.db.crud import create_user, select_user_by_full_name, verify_password
from sophia.core.db.crud.crud_user import select_user_by_email
from sophia.core.db.models import User

router = APIRouter()


@router.post("/access-token", response_model=Token)
async def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = select_user_by_full_name(db, full_name=form_data.username)
    if not user:
        raise HTTPException(**CONSTANT.RESP_USER_NOT_EXISTS)

    if not user.is_active:
        raise HTTPException(**CONSTANT.RESP_USER_NOT_ACTIVE)

    if not verify_password(form_data.password, str(user.password)):
        raise HTTPException(**CONSTANT.RESP_USER_INCORRECT_PASSWD)

    scopes = json.loads(str(user.scopes))
    form_data.scopes = scopes
    return Token(
        **CONSTANT.RESP_SUCCESS,
        access_token=security.get_access_token(
            data=TokenPayload(userid=user.id, username=user.full_name, scopes=scopes),
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        ),
        token_type="bearer",
        user_id=user.id,
        scopes=scopes,
        timestamp=pytz.timezone("Asia/Shanghai")
        .localize(datetime.now())
        .strftime("%Y-%m-%d %H:%M:%S"),
    )


@router.post("/test-token", response_model=User)
async def token_test(current_user: User = Depends(get_current_user)) -> Any:
    """
    Test access token
    """
    del current_user.password
    return current_user


@router.post("/register", response_model=User)
async def user_register(
    user: UserBasicInfo,
    db: Session = Depends(get_db),
) -> Any:
    """
    Register new user (This interface has not undergone login verification)
    """
    if select_user_by_full_name(db, full_name=user.full_name):
        raise HTTPException(**CONSTANT.RESP_USER_EXISTS)

    if select_user_by_email(db, email=user.email):
        raise HTTPException(**CONSTANT.RESP_USER_EMAIL_EXISTS)
    try:
        new_user = user.build_user()
        new_user = create_user(db=db, user=new_user)
        del new_user.password
        return new_user
    except Exception as err:
        raise HTTPException(**CONSTANT.RESP_SERVER_ERROR) from err
