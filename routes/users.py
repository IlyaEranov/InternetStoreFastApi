from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from models.users import User, UserCreate, UserRead, UserUpdate
from database.connection import get_session

user_router = APIRouter(tags=["users"])

@user_router.post("/", response_model=UserRead, status_code=201)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    db_user = User.from_orm(user) 
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@user_router.get("/", response_model=List[UserRead])
def read_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users

@user_router.get("/{user_id}", response_model=UserRead)
def read_user(user_id: int, session: Session = Depends(get_session)):
    print(user_id)
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@user_router.put("/{user_id}", response_model=UserRead)
def update_user(user_id: int, user_update: UserUpdate, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@user_router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return None