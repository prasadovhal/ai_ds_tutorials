import datetime

import jwt
from passlib.context import CryptContext
from strawberry.permission import BasePermission
from strawberry.types import Info

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
TOKEN_EXPIRY_HOURS = 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_token(user_id: int, role: str) -> str:
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=TOKEN_EXPIRY_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None


class IsAuthenticated(BasePermission):
    message = "You must be logged in"

    def has_permission(self, source, info: Info, **kwargs) -> bool:
        return info.context.get("user") is not None


class IsAdmin(BasePermission):
    message = "Admin access required"

    def has_permission(self, source, info: Info, **kwargs) -> bool:
        user = info.context.get("user")
        return user is not None and user.role == "admin"
