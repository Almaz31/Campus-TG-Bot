from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
from sqlalchemy import String,Text,DateTime,func
from typing import Optional

class Base(DeclarativeBase):
    created:Mapped[DateTime]=mapped_column(DateTime,default=func.now())
    updated:Mapped[DateTime]=mapped_column(DateTime,default=func.now(),onupdate=func.now())

class Info(Base):
    __tablename__="info"

    id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    name:Mapped[str]=mapped_column(String(150),nullable=False)
    description:Mapped[str]=mapped_column(Text,nullable=False)
    image:Mapped[str]=mapped_column(String(150))

class Members(Base):
    __tablename__="members"

    id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    name:Mapped[str]=mapped_column(String(150),nullable=False)
    surname:Mapped[str]=mapped_column(String(150),nullable=False)
    team:Mapped[str]=mapped_column(String(150),nullable=False)
    mark:Mapped[Optional[int]]=mapped_column( nullable=True)
    id_user:Mapped[int]=mapped_column(nullable=False)

