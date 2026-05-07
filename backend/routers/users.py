from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from database import get_db
from models import User
from auth import hash_password, require_role, ROLE_ACCESS

router = APIRouter(prefix="/api/users", tags=["users"])

class UserCreate(BaseModel):
    nama: str
    username: str
    password: str
    role: str

class UserUpdate(BaseModel):
    nama: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    aktif: Optional[bool] = None

VALID_ROLES = ["owner", "admin", "admin-keuangan", "produksi"]

@router.get("")
def get_all(db: Session = Depends(get_db), _=Depends(require_role("owner"))):
    users = db.query(User).order_by(User.id).all()
    return [{"id": u.id, "nama": u.nama, "username": u.username,
             "role": u.role, "aktif": u.aktif, "created_at": str(u.created_at)} for u in users]

@router.post("")
def create(data: UserCreate, db: Session = Depends(get_db), _=Depends(require_role("owner"))):
    if data.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail="Role tidak valid")
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username sudah dipakai")
    user = User(
        nama=data.nama,
        username=data.username,
        password=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "nama": user.nama, "username": user.username, "role": user.role}

@router.put("/{id}")
def update(id: int, data: UserUpdate, db: Session = Depends(get_db), _=Depends(require_role("owner"))):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404)
    if data.nama: user.nama = data.nama
    if data.password: user.password = hash_password(data.password)
    if data.role:
        if data.role not in VALID_ROLES:
            raise HTTPException(status_code=400, detail="Role tidak valid")
        user.role = data.role
    if data.aktif is not None: user.aktif = data.aktif
    db.commit()
    return {"ok": True}

@router.delete("/{id}")
def delete(id: int, db: Session = Depends(get_db), current=Depends(require_role("owner"))):
    if id == current.id:
        raise HTTPException(status_code=400, detail="Tidak bisa hapus akun sendiri")
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404)
    db.delete(user)
    db.commit()
    return {"ok": True}

@router.get("/roles")
def get_roles(_=Depends(require_role("owner"))):
    return [
        {"value": "owner",          "label": "Owner — Akses penuh"},
        {"value": "admin",          "label": "Admin — Stok & Produksi"},
        {"value": "admin-keuangan", "label": "Admin Keuangan — Keuangan & Log"},
        {"value": "produksi",       "label": "Produksi — Log Produksi & Pengeluaran"},
    ]
