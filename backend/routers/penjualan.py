from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from pydantic import BaseModel
from database import get_db
from models import LogPenjualan

router = APIRouter(prefix="/api/penjualan", tags=["penjualan"])

class PenjualanCreate(BaseModel):
    tanggal: date
    channel: str
    produk_kode: Optional[str] = None
    produk_nama: Optional[str] = None
    qty: int
    harga_satuan: float
    metode: Optional[str] = None
    status: str = "pending"
    catatan: Optional[str] = None

class StatusUpdate(BaseModel):
    status: str

@router.get("")
def get_all(db: Session = Depends(get_db)):
    return db.query(LogPenjualan).order_by(LogPenjualan.tanggal.desc()).all()

@router.post("")
def create(data: PenjualanCreate, db: Session = Depends(get_db)):
    total = data.harga_satuan * data.qty
    item = LogPenjualan(**data.model_dump(), total=total)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.patch("/{id}/status")
def update_status(id: int, data: StatusUpdate, db: Session = Depends(get_db)):
    item = db.query(LogPenjualan).filter(LogPenjualan.id == id).first()
    if not item:
        raise HTTPException(status_code=404)
    item.status = data.status
    db.commit()
    return item

@router.post("/bulk")
def bulk_import(rows: list[PenjualanCreate], db: Session = Depends(get_db)):
    ok, errors = 0, []
    for i, data in enumerate(rows):
        try:
            total = data.harga_satuan * data.qty
            item = LogPenjualan(**data.model_dump(), total=total)
            db.add(item)
            ok += 1
        except Exception as e:
            errors.append({"baris": i + 2, "error": str(e)})
    db.commit()
    return {"berhasil": ok, "gagal": len(errors), "errors": errors}

@router.delete("/{id}")
def delete(id: int, db: Session = Depends(get_db)):
    item = db.query(LogPenjualan).filter(LogPenjualan.id == id).first()
    if not item:
        raise HTTPException(status_code=404)
    db.delete(item)
    db.commit()
    return {"ok": True}
