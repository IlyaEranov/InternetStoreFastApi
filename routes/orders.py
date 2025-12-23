from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from decimal import Decimal

from database.connection import get_session
from models.orders import Order, OrderItem, OrderCreateFromCart, OrderStatusUpdate
from models.cart import Cart, CartItem
from models.products import Product

orders_router = APIRouter(tags=["orders"])

@orders_router.post("/")
def create_order(
    data: OrderCreateFromCart,
    session: Session = Depends(get_session)
):
    user_id = data.user_id
    cart = session.exec(select(Cart).where(Cart.user_id == user_id)).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Корзина пуста или не найдена")
    selected_items = []
    total = Decimal("0")

    for product_id in data.product_ids:
        cart_item = next((ci for ci in cart.items if ci.product_id == product_id), None)
        if not cart_item:
            raise HTTPException(
                status_code=404,
                detail=f"Товар с id {product_id} не найден в корзине пользователя {user_id}"
            )

        product = session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Товар с id {product_id} не существует")

        if product.stock < cart_item.quantity:
            raise HTTPException(status_code=400, detail=f"Недостаточно товара {product.name} на складе")

        product.stock -= cart_item.quantity
        if product.stock <= 0:
            product.is_available = False
        session.add(product)

        subtotal = product.price * cart_item.quantity
        total += subtotal

        selected_items.append({
            "product_id": product_id,
            "quantity": cart_item.quantity,
            "price_at_purchase": product.price
        })

    if not selected_items:
        raise HTTPException(status_code=400, detail="Не выбрано ни одного товара")

    order = Order(user_id=user_id, total_amount=total, status="new")
    session.add(order)
    session.commit()
    session.refresh(order)

    for item in selected_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item["product_id"],
            quantity=item["quantity"],
            price_at_purchase=item["price_at_purchase"]
        )
        session.add(order_item)

    for product_id in data.product_ids:
        cart_item = next(ci for ci in cart.items if ci.product_id == product_id)
        session.delete(cart_item)

    session.commit()

    return {"message": "Заказ создан", "order_id": order.id, "total": total}


@orders_router.get("/{user_id}", response_model=List[Order])
def get_user_orders(user_id: int, session: Session = Depends(get_session)):
    orders = session.exec(select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())).all()
    return orders


@orders_router.get("/", response_model=List[Order])
def get_all_orders(session: Session = Depends(get_session)):
    orders = session.exec(select(Order).order_by(Order.created_at.desc())).all()
    return orders


@orders_router.patch("/{order_id}/status")
def update_order_status(
    order_id: int,
    update: OrderStatusUpdate,
    session: Session = Depends(get_session)
):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    allowed_statuses = {"new", "packing", "shipped", "delivered", "cancelled"}
    if update.status not in allowed_statuses:
        raise HTTPException(status_code=400, detail=f"Недопустимый статус. Доступны: {allowed_statuses}")

    order.status = update.status
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@orders_router.delete("/{order_id}")
def delete_order(order_id: int, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    for item in order.items:
        session.delete(item)

    session.delete(order)
    session.commit()
    return {"message": "Заказ удалён"}