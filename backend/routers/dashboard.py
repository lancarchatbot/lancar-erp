from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import date
from database import get_db
from models import MasterBahan, LogPenerimaan, LogProduksi, LogPenjualan, PengeluaranUmum

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("")
def dashboard(db: Session = Depends(get_db)):
    now = date.today()

    total_stok_nilai = db.query(
        func.sum(MasterBahan.stok * MasterBahan.harga_satuan)
    ).scalar() or 0

    total_produk_jadi = db.query(func.count(LogProduksi.id)).scalar() or 0

    bahan_kritis = db.query(MasterBahan).filter(
        MasterBahan.stok <= MasterBahan.stok_min
    ).count()

    batch_bulan_ini = db.query(func.count(LogProduksi.id)).filter(
        extract('month', LogProduksi.tanggal) == now.month,
        extract('year',  LogProduksi.tanggal) == now.year,
    ).scalar() or 0

    penjualan_bulan = db.query(func.sum(LogPenjualan.total)).filter(
        extract('month', LogPenjualan.tanggal) == now.month,
        extract('year',  LogPenjualan.tanggal) == now.year,
    ).scalar() or 0

    pengeluaran_bulan = db.query(func.sum(PengeluaranUmum.jumlah)).filter(
        extract('month', PengeluaranUmum.tanggal) == now.month,
        extract('year',  PengeluaranUmum.tanggal) == now.year,
    ).scalar() or 0

    transaksi_terakhir = []
    penjualan_recent = db.query(LogPenjualan).order_by(LogPenjualan.tanggal.desc()).limit(5).all()
    for p in penjualan_recent:
        transaksi_terakhir.append({"tipe": "masuk", "keterangan": p.channel + " — " + (p.produk_nama or ""), "jumlah": p.total, "tanggal": str(p.tanggal)})
    keluar_recent = db.query(PengeluaranUmum).order_by(PengeluaranUmum.tanggal.desc()).limit(5).all()
    for k in keluar_recent:
        transaksi_terakhir.append({"tipe": "keluar", "kode": k.kode_kategori, "keterangan": k.keterangan, "jumlah": k.jumlah, "tanggal": str(k.tanggal)})
    transaksi_terakhir.sort(key=lambda x: x["tanggal"], reverse=True)

    return {
        "total_stok_nilai": total_stok_nilai,
        "total_produk_jadi": total_produk_jadi,
        "bahan_kritis": bahan_kritis,
        "batch_bulan_ini": batch_bulan_ini,
        "penjualan_bulan": penjualan_bulan,
        "pengeluaran_bulan": pengeluaran_bulan,
        "laba_bersih_bulan": penjualan_bulan - pengeluaran_bulan,
        "transaksi_terakhir": transaksi_terakhir[:7],
    }
