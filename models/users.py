from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, min_length=3, max_length=50)
    email: str = Field(index=True, unique=True)
    full_name: Optional[str] = None
    password: str = Field(index=True, unique=True)
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)
    orders: List["Order"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})
    cart: Optional["Cart"] = Relationship(back_populates="user")

class UserCreate(SQLModel):
    username: str
    email: str
    full_name: Optional[str] = None
    password: str

class UserRead(SQLModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    is_admin: bool
    password: str

class UserUpdate(SQLModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    password: Optional[str] = None 
