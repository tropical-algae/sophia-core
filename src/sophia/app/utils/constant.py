from fastapi import status
from pydantic_settings import BaseSettings


class Constant(BaseSettings):
    # 返回值
    RESP_SUCCESS: dict = {"status": status.HTTP_200_OK, "message": "success"}
    RESP_SERVER_ERROR: dict = {
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "detail": "服务器错误",
    }
    # 权限
    ROLE_ADMIN_DESCRIPTION: str = "系统管理员，管理所有数据"
    ROLE_USER_DESCRIPTION: str = "系统用户，查看自己用户数据"
    ROLE_GUEST_DESCRIPTION: str = "访客，查看公开数据"
    # 用户
    RESP_TOKEN_NOT_MATCH: dict = {
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "detail": "Access Token校验失败",
    }
    RESP_TOKEN_VERIFY_ERR: dict = {
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "detail": "Access Token解析失败",
    }
    RESP_TOKEN_NOT_EXISTED: dict = {
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "detail": "Access Token不存在，请先登录",
    }
    RESP_TOKEN_EXPIRED: dict = {
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "detail": "Access Token过期，需要重新登录",
    }

    RESP_USER_FORBIDDEN: dict = {
        "status_code": status.HTTP_403_FORBIDDEN,
        "detail": "当前用户权限不足",
    }
    RESP_USER_NOT_ACTIVE: dict = {
        "status_code": status.HTTP_403_FORBIDDEN,
        "detail": "当前账户已暂停使用",
    }
    RESP_USER_INCORRECT_PASSWD: dict = {
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "detail": "用户名或密码错误",
    }
    RESP_USER_EXISTS: dict = {
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "detail": "用户名已存在",
    }
    RESP_USER_EMAIL_EXISTS: dict = {
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "detail": "邮箱已被注册",
    }
    RESP_USER_NOT_EXISTS: dict = {
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "detail": "用户不存在",
    }


CONSTANT = Constant()
