from typing import List, Optional
from sqlmodel import JSON, SQLModel, Field, Column
from typing import Optional, List

class Product(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    image: str
    image: str 
    description: str
    tags: List[str]
    tags: List[str] = Field(sa_column=Column(JSON))
    location: str
    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Product",
                "image": "https://linktomyimage.com/image.png",
                "description": "Product description",
                "price": 0,
                "tags": ["python", "fastapi", "book", "launch"],
                "location": "Google Meet"
            }
        }
    }

class ProductUpdate(SQLModel): 
    title: Optional[str] 
    image: Optional[str]
    description: Optional[str]
    price: Optional[int]
    tags: Optional[List[str]]
    location: Optional[str]
    model_config = {
        "json_schema_extra": {
            "example": {
              "title": "Product",
              "image": "https://linktomyimage.com/image.png",
              "description": "Product description",
              "price": 0,
              "tags": ["python", "fastapi", "book", "launch"],
              "location": "Google Meet"
            }
        }
    }