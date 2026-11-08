from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate
from app.security import hash_password



def get_user(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)



def get_user_by_email(db: Session, email: str) -> User:
    stmt = select(User).where(User.email == email)
    return db.scalars(stmt).first()



def create_user(db:Session, data: UserCreate) -> User:
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh
    return user