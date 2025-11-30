from fastapi import APIRouter, Depends

from api.dependencies import get_current_user
from config.logger_conf import setup_logger
from models.user_model import User

logger = setup_logger()


router = APIRouter(prefix="/auth")


@router.get("/me")
def protected_route(current_user: User = Depends(get_current_user)):
    return {"user": current_user}
