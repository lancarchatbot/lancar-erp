from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models import User
from auth import verify_password, create_token, get_current_user, ROLE_ACCESS

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username, User.aktif == True).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Username atau password salah")
    token = create_token({"sub": str(user.id), "role": user.role})
    return {
        "token": token,
        "user": {
            "id": user.id,
            "nama": user.nama,
            "username": user.username,
            "role": user.role,
        },
        "akses": ROLE_ACCESS.get(user.role, []),
    }

@router.get("/me")
def me(current: User = Depends(get_current_user)):
    return {
        "id": current.id,
        "nama": current.nama,
        "username": current.username,
        "role": current.role,
        "akses": ROLE_ACCESS.get(current.role, []),
    }
