from pydantic import BaseModel, EmailStr, Field, validator
from typing import Annotated, List, Optional 




class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
    scopes: list[str] = []

# Define a Pydantic model for updating user details
class UserUpdate(BaseModel):
    disabled: Optional[bool]
    scopes: Optional[List[str]] = Field(..., max_length=10)  # Add max_length=10 to scopes

    @validator('scopes')
    def validate_scopes(cls, value):
        allowed_scopes = ["admin", "write", "read"]
        if value is not None and any(scope not in allowed_scopes for scope in value):
            raise ValueError("Invalid scope. Allowed scopes are 'admin', 'write', and 'read'.")
        return value

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
    scopes: list[str] = []

class UserInDB(User):
    hashed_password: str
    scopes: list[str] = []

class UserRegister(BaseModel):
    username: str = Field(..., max_length=50)
    email: EmailStr = Field(..., max_length=50)  # Combining max_length and EmailStr
    full_name: str = Field(..., max_length=50)
    password: str = Field(..., max_length=50)


