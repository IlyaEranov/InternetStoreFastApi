from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from decimal import Decimal

from database.connection import get_session
from models.orders import Order, OrderItem, OrderCreate, OrderReadWithDetails, OrderRead
from models.users import User
from models.products import Product, ProductUpdate

orders_router = APIRouter(tags=["orders"])


@orders_router.post("/", response_model=OrderReadWithDetails, status_code=201)
def create_order(order_create: OrderCreate, session: Session = Depends(get_session)):
    if not order_create.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item")

    total_amount = Decimal("0.0")
    order_items = []

    # Создаём заказ без итоговой суммы сначала
    db_order = Order(user_id=order_create.user_id, total_amount=total_amount)
    session.add(db_order)
    session.commit()
    session.refresh(db_order)

    for item in order_create.items:
        # Проверяем существование продукта
        product = session.get(Product, item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with id {item.product_id} not found")

        if not product.is_available:
            raise HTTPException(status_code=400, detail=f"Product '{product.name}' is not available")

        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for product '{product.name}'. Available: {product.stock}, requested: {item.quantity}"
            )

        # Фиксируем цену на момент покупки
        price_at_purchase = product.price
        subtotal = price_at_purchase * item.quantity
        total_amount += subtotal

        # Создаём элемент заказа
        order_item = OrderItem(
            order_id=db_order.id,
            product_id=product.id,
            quantity=item.quantity,
            price_at_purchase=price_at_purchase
        )
        order_items.append(order_item)
        session.add(order_item)

        # Уменьшаем количество на складе
        product.stock -= item.quantity
        if product.stock == 0:
            product.is_available = False
        session.add(product)

    # Обновляем общую сумму заказа
    db_order.total_amount = total_amount
    session.add(db_order)

    session.commit()
    session.refresh(db_order)

    # Возвращаем заказ с деталями (элементами)
    return db_order


@orders_router.get("/", response_model=List[OrderRead])
def read_orders(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    orders = session.exec(select(Order).offset(skip).limit(limit)).all()
    return orders


@orders_router.get("/{order_id}", response_model=OrderReadWithDetails)
def read_order(order_id: int, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@orders_router.get("/user/{user_id}", response_model=List[OrderReadWithDetails])
def read_orders_by_user(user_id: int, session: Session = Depends(get_session)):
    orders = session.exec(select(Order).where(Order.user_id == user_id)).all()
    return orders


@orders_router.patch("/{order_id}/status", response_model=OrderRead)
def update_order_status(
    order_id: int,
    status_update: dict,  # {"status": "paid" | "shipped" | "delivered" | "cancelled"}
    session: Session = Depends(get_session)
):
    allowed_statuses = {"pending", "paid", "shipped", "delivered", "cancelled"}
    new_status = status_update.get("status")
    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Allowed: {allowed_statuses}"
        )

    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Можно добавить логику: если cancelled — вернуть товары на склад
    if new_status == "cancelled" and order.status != "cancelled":
        # Возвращаем товары на склад
        for item in order.items:
            product = session.get(Product, item.product_id)
            if product:
                product.stock += item.quantity
                product.is_available = True
                session.add(product)

    order.status = new_status
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@orders_router.delete("/{order_id}", status_code=204)
def delete_order(order_id: int, session: Session = Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status in {"paid", "shipped", "delivered"}:
        raise HTTPException(status_code=400, detail="Cannot delete order with this status")

    session.delete(order)
    session.commit()
    return None