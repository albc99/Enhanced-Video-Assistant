from fastapi import APIRouter, HTTPException,Depends
from fastapi.params import Body
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from starlette.status import HTTP_400_BAD_REQUEST
from pydantic import BaseModel
from ..database.connect_to_azure_blob import BLOB
import jwt
from typing import Optional
from ..utils.schemas import User
from starlette.requests import Request
from ..database.database import get_db_connection
from sqlalchemy.orm import Session
from sqlalchemy import text

"""
File: auth.py
Description: This file contains the functions that handle the authentication of the users.
Functionality: This file is used to handle the login and registration of the users.
"""


SECRET_KEY = "EVAisAwesome"  # replace 
ALGORITHM = "HS256"  

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class RegisterBody(BaseModel):
    username: str
    password: str
    email: str

blob_database = BLOB()

# Dependency to get the session
def get_session(request: Request):
    return request.session
def decode_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("user_id")
    except jwt.PyJWTError:
        return None

def verify_token(token: str = Depends(oauth2_scheme)):
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid token")
    return user_id

def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependency to get the current user
def get_current_user(user_id: int = Depends(verify_token),db: Session = Depends(get_db_connection)):
    print(user_id)
    user_record = db.execute("SELECT * FROM dbo.users_table WHERE user_id=:user_id", {"user_id": user_id}).fetchone()
    if not user_record:
        print("user not found")
        raise HTTPException(status_code=400, detail="User not found")
    # Create a User object from the user_record
    user = User(user_id=user_record[0], email=user_record[3],current_project=None)
    print(user)
    return user



def get_user(user_id: int, db: Session = Depends(get_db_connection) ):
    query = text("SELECT * FROM dbo.users_table WHERE user_id=:user_id")
    user_record = db.execute(query, {"user_id": user_id}).fetchone()
    if not user_record:
        raise HTTPException(status_code=400, detail="User not found")
    # Create a User object from the user_record
    user = User(id=user_record[0], email=user_record[3],current_project=None)
    return user

@router.post("/login/")
async def login(request: Request,username: str = Body(...), password: str = Body(...), db: Session = Depends(get_db_connection)):

    user_record = None

    try:
        query = text("SELECT * FROM dbo.users_table WHERE username=:username AND password=:password")
        user_record = db.execute(query, {"username": username, "password": password}).fetchone()
    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail="Login failed: " + str(e))
    
    if user_record is None:
            raise HTTPException(status_code=400, detail="Incorrect username or password")
    

    access_token = create_access_token(data={"sub": user_record[0]})
    user = get_user(user_record[0], db)
    # Save user object in session
    session =  get_session(request)
    session["user"] = user.dict()
    return JSONResponse(content={
        "message": "Login successful",
        "user_id":user_record[0],
        "user_name":user_record[1],
        "access_token": access_token,
        "token_type": "bearer"
    })


@router.post("/register/")
async def register(registrationInfo : RegisterBody, db: Session = Depends(get_db_connection)):
    try:
        username = registrationInfo.username
        password = registrationInfo.password
        email = registrationInfo.email

        registerQuery = text("""
                        INSERT INTO dbo.users_table (username, password, email)
                        VALUES (:username, :password, :email)
                    """)
        db.execute(registerQuery, {"username": username, "password": password, "email": email})
        db.commit()

        return {"username": username, "email": email, "message": "User created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

