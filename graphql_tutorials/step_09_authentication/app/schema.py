import strawberry
from strawberry.types import Info

from .auth import (
    IsAdmin,
    IsAuthenticated,
    create_token,
    hash_password,
    verify_password,
)
from .models import BookModel, UserModel


# --- GraphQL Types ---


@strawberry.type
class User:
    id: strawberry.ID
    username: str
    email: str
    role: str


@strawberry.type
class Book:
    id: strawberry.ID
    title: str
    year: int


@strawberry.type
class AuthPayload:
    """Returned after login/register with the user and JWT token."""

    user: User
    token: str


# --- Input Types ---


@strawberry.input
class RegisterInput:
    username: str
    email: str
    password: str


# --- Queries ---


@strawberry.type
class Query:
    @strawberry.field
    def books(self, info: Info) -> list[Book]:
        """Public - anyone can list books."""
        db = info.context["db"]
        rows = db.query(BookModel).all()
        return [Book(id=strawberry.ID(str(r.id)), title=r.title, year=r.year) for r in rows]

    @strawberry.field(permission_classes=[IsAuthenticated])
    def me(self, info: Info) -> User:
        """Protected - requires login. Returns current user."""
        user = info.context["user"]
        return User(
            id=strawberry.ID(str(user.id)),
            username=user.username,
            email=user.email,
            role=user.role,
        )

    @strawberry.field(permission_classes=[IsAdmin])
    def users(self, info: Info) -> list[User]:
        """Admin only - list all users."""
        db = info.context["db"]
        rows = db.query(UserModel).all()
        return [
            User(
                id=strawberry.ID(str(r.id)),
                username=r.username,
                email=r.email,
                role=r.role,
            )
            for r in rows
        ]


# --- Mutations ---


@strawberry.type
class Mutation:
    @strawberry.mutation
    def register(self, info: Info, input: RegisterInput) -> AuthPayload:
        """Create a new user account."""
        db = info.context["db"]

        if db.query(UserModel).filter(UserModel.email == input.email).first():
            raise ValueError("Email already registered")
        if db.query(UserModel).filter(UserModel.username == input.username).first():
            raise ValueError("Username already taken")

        user = UserModel(
            username=input.username,
            email=input.email,
            password_hash=hash_password(input.password),
            role="user",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        token = create_token(user.id, user.role)
        return AuthPayload(
            user=User(
                id=strawberry.ID(str(user.id)),
                username=user.username,
                email=user.email,
                role=user.role,
            ),
            token=token,
        )

    @strawberry.mutation
    def login(self, info: Info, email: str, password: str) -> AuthPayload:
        """Login with email and password. Returns JWT token."""
        db = info.context["db"]
        user = db.query(UserModel).filter(UserModel.email == email).first()

        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")

        token = create_token(user.id, user.role)
        return AuthPayload(
            user=User(
                id=strawberry.ID(str(user.id)),
                username=user.username,
                email=user.email,
                role=user.role,
            ),
            token=token,
        )
