from fastapi import APIRouter

from app.dependencies import CurrentUserDep
from app.schemas.response import APIResponse, ok
from app.schemas.user import UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=APIResponse[UserRead])
def get_me(current_user: CurrentUserDep):
    return ok(current_user, "Current user retrieved")
