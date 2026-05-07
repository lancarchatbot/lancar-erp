from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from database import get_db
from models import MasterProduk

router = APIRouter(prefix="/api/produk", tags=["produk"])

class ProdukCreate(BaseModel):
    kode: str
    nama: str
    satuan: Optional[str] = None
    stok: int = 0
    harga_jual: float = 0
    hpp: float = 0
    no_izin_edar: Optional[str] = None
    keterangan: Optional[str] = None

@router.get("")
def get_all(db: Session = Depends(get_db)):
    return db.query(MasterProduk).order_by(MasterProduk.kode).all()

@router.post("")
def create(data: ProdukCreate, db: Session = Depends(get_db)):
    if db.query(MasterProduk).filter(MasterProduk.kode == data.kode).first():
        raise HTTPException(status_code=400, detail="Kode produk sudah ada")
    item = MasterProduk(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.put("/{id}")
def update(id: int, data: ProdukCreate, db: Session = Depends(get_db)):
    item = db.query(MasterProduk).filter(MasterProduk.id == id).first()
    if not item:
        raise HTTPException(status_code=404)
    for k, v in data.model_dump().items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/{id}")
def delete(id: int, db: Session = Depends(get_db)):
    item = db.query(MasterProduk).filter(MasterProduk.id == id).first()
    if not item:
        raise HTTPException(status_code=404)
    db.delete(item)
    db.commit()
    return {"ok": True}
