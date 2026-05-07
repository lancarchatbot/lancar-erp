from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import Optional
from datetime import date
from pydantic import BaseModel
from database import get_db
from models import PengeluaranUmum, KategoriKustom, LogPenjualan
import os, shutil, uuid

router = APIRouter(prefix="/api/keuangan", tags=["keuangan"])
UPLOAD_DIR = "/app/uploads"

class PengeluaranCreate(BaseModel):
    tanggal: date
    kode_kategori: str
    keterangan: str
    jumlah: float
    metode: Optional[str] = None

class KategoriCreate(BaseModel):
    kode: str
    nama: str

@router.get("/pengeluaran")
def get_pengeluaran(db: Session = Depends(get_db)):
    return db.query(PengeluaranUmum).order_by(PengeluaranUmum.tanggal.desc()).all()

@router.post("/pengeluaran")
def create_pengeluaran(data: PengeluaranCreate, db: Session = Depends(get_db)):
    item = PengeluaranUmum(**data.model_dump(), sumber="manual")
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.post("/pengeluaran/{id}/upload-bukti")
def upload_bukti(id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    item = db.query(PengeluaranUmum).filter(PengeluaranUmum.id == id).first()
    if not item:
        raise HTTPException(status_code=404)
    ext = os.path.splitext(file.filename)[1]
    fname = f"keluar_{id}_{uuid.uuid4().hex[:8]}{ext}"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(os.path.join(UPLOAD_DIR, fname), "wb") as f:
        shutil.copyfileobj(file.file, f)
    item.bukti_file = fname
    db.commit()
    return {"filename": fname}

@router.delete("/pengeluaran/{id}")
def delete_pengeluaran(id: int, db: Session = Depends(get_db)):
    item = db.query(PengeluaranUmum).filter(PengeluaranUmum.id == id).first()
    if not item:
        raise HTTPException(status_code=404)
    db.delete(item)
    db.commit()
    return {"ok": True}

@router.get("/kategori")
def get_kategori(db: Session = Depends(get_db)):
    return db.query(KategoriKustom).order_by(KategoriKustom.kode).all()

@router.post("/kategori")
def create_kategori(data: KategoriCreate, db: Session = Depends(get_db)):
    if db.query(KategoriKustom).filter(KategoriKustom.kode == data.kode).first():
        raise HTTPException(status_code=400, detail="Kode sudah ada")
    item = KategoriKustom(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/kategori/{kode}")
def delete_kategori(kode: str, db: Session = Depends(get_db)):
    item = db.query(KategoriKustom).filter(KategoriKustom.kode == kode).first()
    if not item:
        raise HTTPException(status_code=404)
    db.delete(item)
    db.commit()
    return {"ok": True}

@router.get("/ringkasan")
def ringkasan(bulan: int = None, tahun: int = None, db: Session = Depends(get_db)):
    q_keluar = db.query(func.sum(PengeluaranUmum.jumlah))
    q_masuk  = db.query(func.sum(LogPenjualan.total))
    if bulan:
        q_keluar = q_keluar.filter(extract('month', PengeluaranUmum.tanggal) == bulan)
        q_masuk  = q_masuk.filter(extract('month', LogPenjualan.tanggal) == bulan)
    if tahun:
        q_keluar = q_keluar.filter(extract('year', PengeluaranUmum.tanggal) == tahun)
        q_masuk  = q_masuk.filter(extract('year', LogPenjualan.tanggal) == tahun)

    total_keluar = q_keluar.scalar() or 0
    total_masuk  = q_masuk.scalar() or 0

    # Breakdown per kategori
    breakdown = db.query(
        PengeluaranUmum.kode_kategori,
        func.sum(PengeluaranUmum.jumlah).label("total")
    ).group_by(PengeluaranUmum.kode_kategori).all()

    return {
        "total_penerimaan": total_masuk,
        "total_pengeluaran": total_keluar,
        "laba_bersih": total_masuk - total_keluar,
        "margin": round((total_masuk - total_keluar) / total_masuk * 100, 1) if total_masuk > 0 else 0,
        "breakdown_kategori": [{"kode": r.kode_kategori, "total": r.total} for r in breakdown],
    }
