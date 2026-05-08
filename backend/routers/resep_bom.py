from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from database import get_db
from models import ResepBOM, MasterBahan

router = APIRouter(prefix="/api/resep-bom", tags=["resep-bom"])

class BOMCreate(BaseModel):
    produk_kode: str
    produk_nama: Optional[str] = None
    bahan_kode: Optional[str] = None
    bahan_nama: Optional[str] = None
    jumlah_per_pcs: float = 0
    satuan: Optional[str] = None
    catatan: Optional[str] = None

@router.get("")
def get_all(produk_kode: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(ResepBOM)
    if produk_kode:
        q = q.filter(ResepBOM.produk_kode == produk_kode)
    items = q.order_by(ResepBOM.produk_kode, ResepBOM.id).all()
    result = []
    for item in items:
        bahan = db.query(MasterBahan).filter(MasterBahan.kode == item.bahan_kode).first()
        harga = bahan.harga_satuan if bahan else 0
        result.append({
            "id": item.id,
            "produk_kode": item.produk_kode,
            "produk_nama": item.produk_nama,
            "bahan_kode": item.bahan_kode,
            "bahan_nama": item.bahan_nama,
            "jumlah_per_pcs": item.jumlah_per_pcs,
            "satuan": item.satuan,
            "harga_satuan": harga,
            "subtotal": item.jumlah_per_pcs * harga,
            "catatan": item.catatan,
        })
    return result

@router.post("")
def create(data: BOMCreate, db: Session = Depends(get_db)):
    item = ResepBOM(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.put("/{id}")
def update(id: int, data: BOMCreate, db: Session = Depends(get_db)):
    item = db.query(ResepBOM).filter(ResepBOM.id == id).first()
    if not item:
        raise HTTPException(status_code=404)
    for k, v in data.model_dump().items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/{id}")
def delete(id: int, db: Session = Depends(get_db)):
    item = db.query(ResepBOM).filter(ResepBOM.id == id).first()
    if not item:
        raise HTTPException(status_code=404)
    db.delete(item)
    db.commit()
    return {"ok": True}
