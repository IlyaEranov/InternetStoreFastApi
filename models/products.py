from typing import Optional, List
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, min_length=1, max_length=100)
    type: str = Field(index=True)
    preview_image: Optional[str] = None
    images: Optional[str] = None
    description: Optional[str] = None
    price: Decimal = Field(decimal_places=2, max_digits=10)
    stock: int = Field(default=0, ge=0) 
    is_available: bool = Field(default=True)
    order_items: List["OrderItem"] = Relationship(back_populates="product")
    cart_items: List["CartItem"] = Relationship(back_populates="product")

class ProductCreate(SQLModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    stock: Optional[int] = 0
    is_available: Optional[bool] = True
    type: str
    preview_image: Optional[str] = None
    images: Optional[str] = None

class ProductRead(SQLModel):
    id: int
    name: str
    description: Optional[str]
    price: Decimal
    stock: int
    is_available: bool
    type: str
    preview_image: Optional[str] = None
    images: Optional[str] = None

class ProductUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[int] = None
    is_available: Optional[bool] = None
    type: str
    preview_image: Optional[str] = None
    images: Optional[str] = None