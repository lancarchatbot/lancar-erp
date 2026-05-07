from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models import User
import os

SECRET_KEY = os.getenv("SECRET_KEY", "lancar-erp-secret-key-2026-herbal")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 12

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)

ROLE_ACCESS = {
    "owner": [
        "dashboard","master-bahan","log-penerimaan","log-pengeluaran",
        "master-produk","log-produksi","resep-bom","kalkulasi-hpp",
        "sisa-stok","log-penjualan","pengeluaran-umum","laporan-keuangan",
        "manajemen-user"
    ],
    "admin": [
        "dashboard","master-bahan","log-penerimaan","log-pengeluaran",
        "master-produk","log-produksi","resep-bom","kalkulasi-hpp","sisa-stok"
    ],
    "admin-keuangan": [
        "dashboard","log-penerimaan","log-pengeluaran","log-produksi",
        "kalkulasi-hpp","sisa-stok","log-penjualan","pengeluaran-umum",
        "laporan-keuangan"
    ],
    "produksi": [
        "dashboard","log-produksi","log-pengeluaran"
    ],
}

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="Belum login")
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token tidak valid")
    user = db.query(User).filter(User.id == int(user_id), User.aktif == True).first()
    if not user:
        raise HTTPException(status_code=401, detail="Akun tidak ditemukan")
    return user

def require_role(*roles):
    def checker(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Akses ditolak")
        return user
    return checker

def seed_owner(db: Session):
    if not db.query(User).filter(User.role == "owner").first():
        db.add(User(
            nama="Owner",
            username="owner",
            password=hash_password("herbal2026"),
            role="owner",
            aktif=True,
        ))
        db.commit()
