from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from pydantic import BaseModel
from database import get_db
from models import LogPenerimaan, MasterBahan, PengeluaranUmum
import os, shutil, uuid

router = APIRouter(prefix="/api/penerimaan", tags=["penerimaan"])
UPLOAD_DIR = "/app/uploads"

class PenerimaanCreate(BaseModel):
    tanggal: date
    bahan_kode: str
    bahan_nama: Optional[str] = None
    pemasok: Optional[str] = None
    jumlah: float
    satuan: Optional[str] = None
    harga_satuan: Optional[float] = None
    no_batch: Optional[str] = None
    tgl_kadaluarsa: Optional[date] = None
    no_pirt: Optional[str] = None
    no_bpom_md: Optional[str] = None
    no_bpom_ml: Optional[str] = None
    metode_bayar: Optional[str] = None

class QCUpdate(BaseModel):
    status_qc: str
    catatan_qc: Optional[str] = None
    tindakan_koreksi: Optional[str] = None

class BayarUpdate(BaseModel):
    status_bayar: str
    metode_bayar: Optional[str] = None

@router.get("")
def get_all(db: Session = Depends(get_db)):
    return db.query(LogPenerimaan).order_by(LogPenerimaan.tanggal.desc()).all()

@router.post("")
def create(data: PenerimaanCreate, db: Session = Depends(get_db)):
    total = (data.harga_satuan or 0) * data.jumlah
    item = LogPenerimaan(**data.model_dump(), total_harga=total)
    db.add(item)

    # Update stok bahan
    bahan = db.query(MasterBahan).filter(MasterBahan.kode == data.bahan_kode).first()
    if bahan:
        bahan.stok += data.jumlah

    # Auto-create pengeluaran keuangan (KODE: BUY)
    if total > 0:
        pu = PengeluaranUmum(
            tanggal=data.tanggal,
            kode_kategori="BUY",
            keterangan=f"Beli {data.bahan_nama or data.bahan_kode} {data.jumlah} {data.satuan or ''} — {data.pemasok or ''}",
            jumlah=total,
            metode=data.metode_bayar,
            sumber="auto",
        )
        db.add(pu)

    db.commit()
    db.refresh(item)
    return item

@router.patch("/{id}/qc")
def update_qc(id: int, data: QCUpdate, db: Session = Depends(get_db)):
    item = db.query(LogPenerimaan).filter(LogPenerimaan.id == id).first()
    if not item:
        raise HTTPException(status_code=404)
    item.status_qc = data.status_qc
    item.catatan_qc = data.catatan_qc
    item.tindakan_koreksi = data.tindakan_koreksi
    db.commit()
    return item

@router.patch("/{id}/bayar")
def update_bayar(id: int, data: BayarUpdate, db: Session = Depends(get_db)):
    item = db.query(LogPenerimaan).filter(LogPenerimaan.id == id).first()
    if not item:
        raise HTTPException(status_code=404)
    item.status_bayar = data.status_bayar
    item.metode_bayar = data.metode_bayar
    db.commit()
    return item

@router.post("/{id}/upload-bukti")
def upload_bukti(id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    item = db.query(LogPenerimaan).filter(LogPenerimaan.id == id).first()
    if not item:
        raise HTTPException(status_code=404)
    ext = os.path.splitext(file.filename)[1]
    fname = f"penerimaan_{id}_{uuid.uuid4().hex[:8]}{ext}"
    fpath = os.path.join(UPLOAD_DIR, fname)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(fpath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    item.bukti_file = fname
    db.commit()
    return {"filename": fname}

@router.post("/bulk")
def bulk_import(rows: list[PenerimaanCreate], db: Session = Depends(get_db)):
    ok, errors = 0, []
    for i, data in enumerate(rows):
        try:
            item = LogPenerimaan(**data.model_dump())
            db.add(item)
            bahan = db.query(MasterBahan).filter(MasterBahan.kode == data.bahan_kode).first()
            if bahan:
                bahan.stok += data.jumlah
            ok += 1
        except Exception as e:
            errors.append({"baris": i + 2, "error": str(e)})
    db.commit()
    return {"berhasil": ok, "gagal": len(errors), "errors": errors}

@router.delete("/{id}")
def delete(id: int, db: Session = Depends(get_db)):
    item = db.query(LogPenerimaan).filter(LogPenerimaan.id == id).first()
    if not item:
        raise HTTPException(status_code=404)
    bahan = db.query(MasterBahan).filter(MasterBahan.kode == item.bahan_kode).first()
    if bahan:
        bahan.stok -= item.jumlah
    db.delete(item)
    db.commit()
    return {"ok": True}
