from typing import Optional, List
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class OrderItem(SQLModel, table=True):
    order_id: Optional[int] = Field(default=None, foreign_key="order.id", primary_key=True)
    product_id: Optional[int] = Field(default=None, foreign_key="product.id", primary_key=True)
    quantity: int = Field(ge=1)
    price_at_purchase: Decimal = Field(decimal_places=2, max_digits=10)
    order: Optional["Order"] = Relationship(back_populates="items")
    product: Optional["Product"] = Relationship()

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="pending")  # pending, paid, shipped, delivered, cancelled
    total_amount: Decimal = Field(default=0.0, decimal_places=2, max_digits=12)
    user: Optional["User"] = Relationship(back_populates="orders")
    items: List["OrderItem"] = Relationship(back_populates="order")

class OrderRead(SQLModel):
    id: int
    user_id: int
    created_at: datetime
    status: str
    total_amount: Decimal

class OrderItemRead(SQLModel):
    product_id: int
    quantity: int
    price_at_purchase: Decimal

class OrderReadWithDetails(OrderRead):
    items: List[OrderItemRead] = []

class OrderItemCreate(SQLModel):
    product_id: int
    quantity: int

class OrderCreate(SQLModel):
    items: List[OrderItemCreate]