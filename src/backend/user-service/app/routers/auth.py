from fastapi import APIRouter, status

from app.dependencies import UserServiceDep
from app.lib.security import create_access_token
from app.schemas.response import APIResponse, ok
from app.schemas.user import Token, UserLogin, UserRead, UserRegister

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=APIResponse[UserRead],
    status_code=status.HTTP_201_CREATED,
)
def register(payload: UserRegister, service: UserServiceDep):
    user = service.register(payload)
    return ok(user, "User registered")


@router.post("/login", response_model=APIResponse[Token])
def login(payload: UserLogin, service: UserServiceDep):
    user = service.authenticate(payload)
    token = create_access_token(str(user.id), role=user.role.value)
    return ok(Token(access_token=token), "Login successful")
