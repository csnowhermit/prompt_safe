from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.auth import Token, UserCreate, LoginRequest
from app.services.auth_service import AuthService

router = APIRouter()
auth_service = AuthService()

fake_users_db = {
    "admin": {
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": auth_service.get_password_hash("admin123"),
        "role": "admin"
    },
    "employee": {
        "username": "employee",
        "email": "employee@example.com",
        "hashed_password": auth_service.get_password_hash("employee123"),
        "role": "employee"
    },
    "user": {
        "username": "user",
        "email": "user@example.com",
        "hashed_password": auth_service.get_password_hash("user123"),
        "role": "end_user"
    }
}


@router.post("/login", response_model=Token)
async def login_for_access_token(login_request: LoginRequest):
    user = fake_users_db.get(login_request.username)
    if not user or not auth_service.verify_password(login_request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = auth_service.create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register")
async def register_user(user: UserCreate):
    if user.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    fake_users_db[user.username] = {
        "username": user.username,
        "email": user.email,
        "hashed_password": auth_service.get_password_hash(user.password),
        "role": "end_user"
    }
    return {"message": "用户注册成功", "username": user.username}