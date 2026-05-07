from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from pydantic import BaseModel
from database import get_db
from models import LogProduksi, MasterProduk
import os, shutil, uuid

router = APIRouter(prefix="/api/produksi", tags=["produksi"])
UPLOAD_DIR = "/app/uploads"

class ProduksiCreate(BaseModel):
    kode_produksi: str
    tanggal: date
    produk_kode: Optional[str] = None
    produk_nama: Optional[str] = None
    jumlah: int
    no_batch: Optional[str] = None
    tgl_kadaluarsa: Optional[date] = None
    operator: Optional[str] = None
    catatan: Optional[str] = None

class QCUpdate(BaseModel):
    status_qc: str
    catatan_qc: Optional[str] = None
    tindakan_koreksi: Optional[str] = None

class BayarUpdate(BaseModel):
    status_bayar: str
    nominal_bayar: Optional[float] = None
    tgl_bayar: Optional[date] = None

@router.get("")
def get_all(db: Session = Depends(get_db)):
    return db.query(LogProduksi).order_by(LogProduksi.tanggal.desc()).all()

@router.post("")
def create(data: ProduksiCreate, db: Session = Depends(get_db)):
    if db.query(LogProduksi).filter(LogProduksi.kode_produksi == data.kode_produksi).first():
        raise HTTPException(status_code=400, detail="Kode produksi sudah ada")
    item = LogProduksi(**data.model_dump())
    db.add(item)
    # Update stok produk
    if data.produk_kode:
        produk = db.query(MasterProduk).filter(MasterProduk.kode == data.produk_kode).first()
        if produk:
            produk.stok += data.jumlah
    db.commit()
    db.refresh(item)
    return item

@router.patch("/{id}/qc")
def update_qc(id: int, data: QCUpdate, db: Session = Depends(get_db)):
    item = db.query(LogProduksi).filter(LogProduksi.id == id).first()
    if not item:
        raise HTTPException(status_code=404)
    item.status_qc = data.status_qc
    item.catatan_qc = data.catatan_qc
    item.tindakan_koreksi = data.tindakan_koreksi
    db.commit()
    return item

@router.patch("/{id}/bayar")
def update_bayar(id: int, data: BayarUpdate, db: Session = Depends(get_db)):
    item = db.query(LogProduksi).filter(LogProduksi.id == id).first()
    if not item:
        raise HTTPException(status_code=404)
    item.status_bayar = data.status_bayar
    item.nominal_bayar = data.nominal_bayar
    item.tgl_bayar = data.tgl_bayar
    db.commit()
    return item

@router.delete("/{id}")
def delete(id: int, db: Session = Depends(get_db)):
    item = db.query(LogProduksi).filter(LogProduksi.id == id).first()
    if not item:
        raise HTTPException(status_code=404)
    if item.produk_kode:
        produk = db.query(MasterProduk).filter(MasterProduk.kode == item.produk_kode).first()
        if produk:
            produk.stok = max(0, produk.stok - item.jumlah)
    db.delete(item)
    db.commit()
    return {"ok": True}

@router.post("/{id}/upload-bukti-bayar")
def upload_bukti(id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    item = db.query(LogProduksi).filter(LogProduksi.id == id).first()
    if not item:
        raise HTTPException(status_code=404)
    ext = os.path.splitext(file.filename)[1]
    fname = f"produksi_{id}_{uuid.uuid4().hex[:8]}{ext}"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(os.path.join(UPLOAD_DIR, fname), "wb") as f:
        shutil.copyfileobj(file.file, f)
    item.bukti_bayar_file = fname
    db.commit()
    return {"filename": fname}
