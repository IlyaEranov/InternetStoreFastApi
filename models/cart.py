from typing import Optional, List
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship


# Элемент корзины (товар в корзине)
class CartItem(SQLModel, table=True):
    cart_id: Optional[int] = Field(default=None, foreign_key="cart.id", primary_key=True)
    product_id: Optional[int] = Field(default=None, foreign_key="product.id", primary_key=True)
    quantity: int = Field(default=1, ge=1)

    # Связи
    cart: Optional["Cart"] = Relationship(back_populates="items")
    product: Optional["Product"] = Relationship(back_populates="cart_items")


# Основная модель корзины
class Cart(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)  # Один пользователь — одна корзина

    # Связи
    user: Optional["User"] = Relationship(back_populates="cart")
    items: List["CartItem"] = Relationship(back_populates="cart")

# Для чтения элемента корзины
class CartItemRead(SQLModel):
    product_id: int
    quantity: int
    name: str            # из продукта
    price: Decimal       # текущая цена продукта
    total: Decimal       # quantity * price


# Для чтения полной корзины
class CartRead(SQLModel):
    id: int
    user_id: int
    items: List[CartItemRead] = []
    total_amount: Decimal = Decimal("0.0")
    items_count: int = 0


# Для добавления/обновления товара в корзине
class CartItemUpdate(SQLModel):
    quantity: int