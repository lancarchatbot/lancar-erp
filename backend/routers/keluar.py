from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from pydantic import BaseModel
from database import get_db
from models import LogPengeluaran, MasterBahan

router = APIRouter(prefix="/api/keluar", tags=["keluar"])

class KeluarCreate(BaseModel):
    tanggal: date
    bahan_kode: Optional[str] = None
    bahan_nama: Optional[str] = None
    jumlah: float
    satuan: Optional[str] = None
    tujuan: Optional[str] = None
    no_batch_produksi: Optional[str] = None
    catatan: Optional[str] = None

@router.get("")
def get_all(db: Session = Depends(get_db)):
    return db.query(LogPengeluaran).order_by(LogPengeluaran.tanggal.desc()).all()

@router.post("")
def create(data: KeluarCreate, db: Session = Depends(get_db)):
    item = LogPengeluaran(**data.model_dump())
    db.add(item)
    if data.bahan_kode:
        bahan = db.query(MasterBahan).filter(MasterBahan.kode == data.bahan_kode).first()
        if bahan:
            bahan.stok -= data.jumlah
    db.commit()
    db.refresh(item)
    return item

@router.delete("/{id}")
def delete(id: int, db: Session = Depends(get_db)):
    item = db.query(LogPengeluaran).filter(LogPengeluaran.id == id).first()
    if not item:
        raise HTTPException(status_code=404)
    if item.bahan_kode:
        bahan = db.query(MasterBahan).filter(MasterBahan.kode == item.bahan_kode).first()
        if bahan:
            bahan.stok += item.jumlah
    db.delete(item)
    db.commit()
    return {"ok": True}
