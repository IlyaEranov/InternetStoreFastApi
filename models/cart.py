from typing import Optional, List
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship

class CartItem(SQLModel, table=True):
    cart_id: Optional[int] = Field(default=None, foreign_key="cart.id", primary_key=True)
    product_id: Optional[int] = Field(default=None, foreign_key="product.id", primary_key=True)
    quantity: int = Field(default=1, ge=1)
    cart: Optional["Cart"] = Relationship(back_populates="items")
    product: Optional["Product"] = Relationship(back_populates="cart_items")

class Cart(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    user: Optional["User"] = Relationship(back_populates="cart")
    items: List["CartItem"] = Relationship(back_populates="cart")

class CartItemRead(SQLModel):
    product_id: int
    quantity: int
    name: str            
    price: Decimal       
    total: Decimal       

class CartRead(SQLModel):
    id: int
    user_id: int
    items: List[CartItemRead] = []
    total_amount: Decimal = Decimal("0.0")
    items_count: int = 0

class CartItemUpdate(SQLModel):
    quantity: int