from pydantic import EmailStr
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    email: EmailStr
    password: str
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Example",
                "email": "example@email.com",
                "password": "example123_1"
            }
        }
    }
