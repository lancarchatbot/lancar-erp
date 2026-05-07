from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from pydantic import BaseModel
from database import get_db
from models import MasterBahan

router = APIRouter(prefix="/api/bahan", tags=["bahan"])

class BahanCreate(BaseModel):
    kode: str
    nama: str
    satuan: Optional[str] = None
    stok: float = 0
    stok_min: float = 0
    harga_satuan: float = 0
    kategori: Optional[str] = None
    keterangan: Optional[str] = None

@router.get("")
def get_all(db: Session = Depends(get_db)):
    return db.query(MasterBahan).order_by(MasterBahan.kode).all()

@router.get("/{kode}")
def get_one(kode: str, db: Session = Depends(get_db)):
    item = db.query(MasterBahan).filter(MasterBahan.kode == kode).first()
    if not item:
        raise HTTPException(status_code=404, detail="Bahan tidak ditemukan")
    return item

@router.post("")
def create(data: BahanCreate, db: Session = Depends(get_db)):
    if db.query(MasterBahan).filter(MasterBahan.kode == data.kode).first():
        raise HTTPException(status_code=400, detail="Kode bahan sudah ada")
    item = MasterBahan(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.put("/{id}")
def update(id: int, data: BahanCreate, db: Session = Depends(get_db)):
    item = db.query(MasterBahan).filter(MasterBahan.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Bahan tidak ditemukan")
    for k, v in data.model_dump().items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/{id}")
def delete(id: int, db: Session = Depends(get_db)):
    item = db.query(MasterBahan).filter(MasterBahan.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Bahan tidak ditemukan")
    db.delete(item)
    db.commit()
    return {"ok": True}
