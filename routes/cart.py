from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from decimal import Decimal

from database.connection import get_session
from models.cart import Cart, CartItem, CartRead, CartItemUpdate
from models.products import Product
from models.users import User

cart_router = APIRouter(tags=["cart"])


def get_or_create_cart(user_id: int, session: Session) -> Cart:
    cart = session.exec(select(Cart).where(Cart.user_id == user_id)).first()
    if not cart:
        cart = Cart(user_id=user_id)
        session.add(cart)
        session.commit()
        session.refresh(cart)
    return cart


@cart_router.get("/", response_model=CartRead)
def get_my_cart(
    user_id: int = 1,
    session: Session = Depends(get_session)
):
    cart = get_or_create_cart(user_id, session)

    items_read = []
    total_amount = Decimal("0.0")
    items_count = 0

    for item in cart.items:
        product = session.get(Product, item.product_id)
        if not product:
            continue

        item_total = product.price * item.quantity
        items_read.append({
            "product_id": product.id,
            "quantity": item.quantity,
            "name": product.name,
            "price": product.price,
            "total": item_total
        })
        total_amount += item_total
        items_count += item.quantity

    return CartRead(
        id=cart.id,
        user_id=cart.user_id,
        items=items_read,
        total_amount=total_amount,
        items_count=items_count
    )


@cart_router.post("/{product_id}")
def add_to_cart(
    product_id: int,
    quantity: int = 1,
    user_id: int = 1,
    session: Session = Depends(get_session)
):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    if not product.is_available or product.stock < quantity:
        raise HTTPException(status_code=400, detail="Не хватает товара на складе")

    cart = get_or_create_cart(user_id, session)

    existing_item = None
    for item in cart.items:
        if item.product_id == product_id:
            existing_item = item
            break

    if existing_item:
        existing_item.quantity += quantity
        if existing_item.quantity > product.stock:
            raise HTTPException(status_code=400, detail="Не хватает товара на складе")
        session.add(existing_item)
    else:
        new_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        session.add(new_item)

    session.commit()
    return {"message": "Товар добавлен в корзину"}


@cart_router.put("/{product_id}")
def update_cart_item(
    product_id: int,
    update: CartItemUpdate,
    user_id: int = 1,
    session: Session = Depends(get_session)
):
    cart = get_or_create_cart(user_id, session)

    item = None
    for ci in cart.items:
        if ci.product_id == product_id:
            item = ci
            break

    if not item:
        raise HTTPException(status_code=404, detail="Товар не в корзине")

    product = session.get(Product, product_id)
    if update.quantity > 0 and (not product or product.stock < update.quantity):
        raise HTTPException(status_code=400, detail="Не хватает товара на складе")

    if update.quantity <= 0:
        session.delete(item)
    else:
        item.quantity = update.quantity
        session.add(item)

    session.commit()
    return {"message": "Корзина обновлена"}


@cart_router.delete("/clear")
def clear_cart(
    user_id: int = 1,
    session: Session = Depends(get_session)
):
    cart = session.exec(select(Cart).where(Cart.user_id == user_id)).first()
    if cart:
        for item in cart.items:
            session.delete(item)
        session.commit()
    return {"message": "Корзина очищена"}