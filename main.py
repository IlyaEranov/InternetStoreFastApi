from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from database.connection import conn

from routes.users import user_router
from routes.products import products_router

import uvicorn

app = FastAPI()
app.include_router(user_router, prefix="/users")
app.include_router(products_router, prefix="/products")

@app.on_event("startup")
def on_startup():
    conn()
    
@app.get("/")
async def home():
    return RedirectResponse(url="/products/")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)