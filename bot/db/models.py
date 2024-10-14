from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Email(Base):
    __tablename__ = "email"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]


class PhoneNumber(Base):
    __tablename__ = "phone_number"
    id: Mapped[int] = mapped_column(primary_key=True)
    phone_number: Mapped[str]

