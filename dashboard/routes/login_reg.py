from datetime import datetime, timedelta, timezone
from typing import Annotated, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Security, status, APIRouter, Body, Response, Request, Query
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from passlib.context import CryptContext
from pymongo import MongoClient
from bson.objectid import ObjectId
from pydantic import BaseModel, ValidationError
from models.user import User, UserInDB, UserRegister, UserUpdate, Token, TokenData
from config.db import db, Assets_collection, Findings_collection, users_collection

# # MongoDB connection settings
# MONGO_URI = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.1"
# client = MongoClient(MONGO_URI)

# # MongoDB collections
# db = client["mantis"]
# Assets_collection = db["assets_collection"]
# Findings_collection = db["findings_collection"]
# users_collection = db["users_collection"]

SECRET_KEY = "ef11175f00bb259e4cc3bf58754d539ef9e224e56420775bbc5625086372d178"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 4320


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token"
)

router = APIRouter(tags=["login/registration"])

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(username: str):
    user_data = users_collection.find_one({"username": username})
    if user_data:
        return UserInDB(**user_data)

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    user = get_user(data["sub"])  # Fetch user from DB
    to_encode.update({"exp": expire, "scopes": user.scopes})  # Use user's scopes from DB
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    request: Request,
    security_scopes: SecurityScopes,
) -> User:
    token_cookie = request.cookies.get("access_token")
    if token_cookie is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization cookie not provided",
        )

    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        payload = jwt.decode(token_cookie, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError):
        raise credentials_exception

    user = get_user(token_data.username)
    if user is None:
        raise credentials_exception

    if not any(x in security_scopes.scopes for x in token_data.scopes):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
            headers={"WWW-Authenticate": authenticate_value},
        )
    return token_data

# async def get_current_user(
#     security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]
# ):
#     if security_scopes.scopes:
#         authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
#     else:
#         authenticate_value = "Bearer"
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": authenticate_value},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_scopes = payload.get("scopes", [])
#         token_data = TokenData(scopes=token_scopes, username=username)
#     except (JWTError, ValidationError):
#         raise credentials_exception
#     user = get_user(token_data.username)
#     if user is None:
#         raise credentials_exception
#     for scope in security_scopes.scopes:
#         if scope not in token_data.scopes:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Not enough permissions",
#                 headers={"WWW-Authenticate": authenticate_value},
#             )
#     return user

async def get_current_active_user(
    current_user: Annotated[User, Security(get_current_user, scopes=["read"])]):
    print(current_user.disabled)
    status = bool(current_user.disabled)
    print(status, type(status))

    if status:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# @router.post("/token")
# async def login_for_access_token(
#     form_data: OAuth2PasswordRequestForm = Depends(),
# ) -> Token:
#     user = authenticate_user(form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
    
#     # Check if the user is active
#     active_user = await get_current_active_user(current_user=user)
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.username},
#         expires_delta=access_token_expires,
#     )
#     return Token(access_token=access_token, token_type="bearer")

@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # Check if the user is active
    active_user = await get_current_active_user(current_user=user)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )

    response = Token(access_token=access_token, token_type="bearer")
    response_obj = Response(content=response.json())
    response_obj.set_cookie(key="access_token", value=access_token, httponly=True)
    return response_obj

@router.post("/register/", response_model=User)
async def register_user(user_data: UserRegister = Body(...)):
    # Check if username already exists in MongoDB
    existing_user = users_collection.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Hash the password using bcrypt
    hashed_password = get_password_hash(user_data.password)
    
    # Create the user entry
    first_user = users_collection.count_documents({}) == 0
    
    # Determine account status and scopes
    disabled = False if first_user else True  # Enable account if it's the first user
    scopes = ["admin"] if first_user else ["read"]  # Add admin scope if it's the first user
    
    # Create the user entry
    new_user = {
        "username": user_data.username,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "hashed_password": hashed_password,
        "disabled": disabled,
        "scopes": scopes,
    }
    
    # Insert the new user into MongoDB
    result = users_collection.insert_one(new_user)
    new_user["_id"] = str(result.inserted_id)  # Convert ObjectId to str
    
    return new_user
    # new_user = {
    #     "username": user_data.username,
    #     "email": user_data.email,
    #     "full_name": user_data.full_name,
    #     "hashed_password": hashed_password,
    #     "disabled": True,
    #     "scopes": ["read"],  # Default scope to "read"
    # }
    
    # # Insert the new user into MongoDB
    # result = users_collection.insert_one(new_user)
    # new_user["_id"] = str(result.inserted_id)  # Convert ObjectId to str
    
    # return new_user

@router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Security(get_current_active_user, scopes=["read"])],
):
    return current_user

@router.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Security(get_current_active_user, scopes=["read"])],
):
    return [{"item_id": "Foo", "owner": current_user.username}]

@router.get("/status/")
async def read_system_status(current_user: Annotated[User, Depends(get_current_user)]):
    return {"status": "ok"}

@router.get("/users/", response_model=dict)
async def read_all_users(
    current_user: Annotated[User, Security(get_current_user, scopes=["admin"])] ,
    page: int = Query(1, gt=0),
    page_size: int = Query(10, gt=0, le=100)
):
    # Calculate the skip value based on the page number and page size
    skip = (page - 1) * page_size
    
    # Fetch users with pagination applied
    all_users = users_collection.find().skip(skip).limit(page_size)
    
    # Convert MongoDB documents to User objects and include scopes
    users_with_scopes = [
        User(
            username=user['username'],
            email=user['email'],
            full_name=user['full_name'],
            disabled=user['disabled'],
            scopes=user.get('scopes', [])
        )
        for user in all_users
    ]
    
    # Count total number of users
    total_records = users_collection.count_documents({})
    
    # Return the total number of records and paginated data in the specified format
    return {"total_records": total_records, "data": users_with_scopes}

# Endpoint to update user details by username
@router.put("/users/{username}", response_model=User)
async def update_user_details(
    username: str,
    user_data: UserUpdate = Body(...),
    current_user: User = Security(get_current_user, scopes=["admin"]),
):
    # Check if the user exists
    existing_user = users_collection.find_one({"username": username})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update the user's details if provided in the request
    update_data = {}
    if user_data.disabled is not None:
        update_data["disabled"] = user_data.disabled
    if user_data.scopes is not None:
        update_data["scopes"] = user_data.scopes

    # Update the user in the database
    update_result = users_collection.update_one(
        {"username": username},
        {"$set": update_data}
    )

    # Check if the update was successful
    if update_result.modified_count == 1:
        # Fetch the updated user from the database
        updated_user = users_collection.find_one({"username": username})
        
        # Return the updated user as a dictionary
        return {
            "username": updated_user['username'],
            "email": updated_user['email'],
            "full_name": updated_user['full_name'],
            "disabled": updated_user['disabled'],
            "scopes": updated_user.get('scopes', [])
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to update user")

# Add this new route to your main FastAPI app
