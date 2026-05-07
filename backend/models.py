from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, Boolean, Enum as SAEnum
from sqlalchemy.sql import func
from database import Base
import enum

class MetodeBayar(str, enum.Enum):
    tunai = "TUNAI"
    bank = "BANK"
    ewallet = "E-WALLET"

class StatusQC(str, enum.Enum):
    ms = "MS"
    tms = "TMS"
    pending = "PENDING"

class MasterBahan(Base):
    __tablename__ = "master_bahan"
    id          = Column(Integer, primary_key=True, index=True)
    kode        = Column(String(20), unique=True, nullable=False)
    nama        = Column(String(200), nullable=False)
    satuan      = Column(String(20))
    stok        = Column(Float, default=0)
    stok_min    = Column(Float, default=0)
    harga_satuan= Column(Float, default=0)
    kategori    = Column(String(50))
    keterangan  = Column(Text)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())

class LogPenerimaan(Base):
    __tablename__ = "log_penerimaan"
    id           = Column(Integer, primary_key=True, index=True)
    tanggal      = Column(Date, nullable=False)
    bahan_kode   = Column(String(20), nullable=False)
    bahan_nama   = Column(String(200))
    pemasok      = Column(String(200))
    jumlah       = Column(Float, nullable=False)
    satuan       = Column(String(20))
    harga_satuan = Column(Float)
    total_harga  = Column(Float)
    no_batch     = Column(String(50))
    tgl_kadaluarsa = Column(Date)
    no_pirt      = Column(String(100))
    no_bpom_md   = Column(String(100))
    no_bpom_ml   = Column(String(100))
    status_bayar = Column(String(20), default="belum")
    status_qc    = Column(String(10), default="PENDING")
    catatan_qc   = Column(Text)
    tindakan_koreksi = Column(Text)
    bukti_file   = Column(String(500))
    bukti_bayar_file = Column(String(500))
    metode_bayar = Column(String(20))
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

class LogPengeluaran(Base):
    __tablename__ = "log_pengeluaran"
    id           = Column(Integer, primary_key=True, index=True)
    tanggal      = Column(Date, nullable=False)
    bahan_kode   = Column(String(20))
    bahan_nama   = Column(String(200))
    jumlah       = Column(Float, nullable=False)
    satuan       = Column(String(20))
    tujuan       = Column(String(200))
    no_batch_produksi = Column(String(50))
    catatan      = Column(Text)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

class LogProduksi(Base):
    __tablename__ = "log_produksi"
    id           = Column(Integer, primary_key=True, index=True)
    kode_produksi= Column(String(50), unique=True)
    tanggal      = Column(Date, nullable=False)
    produk_kode  = Column(String(20))
    produk_nama  = Column(String(200))
    jumlah       = Column(Integer, nullable=False)
    no_batch     = Column(String(50))
    tgl_kadaluarsa = Column(Date)
    operator     = Column(String(100))
    status_qc    = Column(String(10), default="PENDING")
    catatan_qc   = Column(Text)
    tindakan_koreksi = Column(Text)
    status_bayar = Column(String(20), default="belum")
    nominal_bayar= Column(Float)
    tgl_bayar    = Column(Date)
    bukti_bayar_file = Column(String(500))
    catatan      = Column(Text)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

class LogPenjualan(Base):
    __tablename__ = "log_penjualan"
    id           = Column(Integer, primary_key=True, index=True)
    tanggal      = Column(Date, nullable=False)
    channel      = Column(String(50))
    produk_kode  = Column(String(20))
    produk_nama  = Column(String(200))
    qty          = Column(Integer)
    harga_satuan = Column(Float)
    total        = Column(Float)
    metode       = Column(String(20))
    status       = Column(String(20), default="pending")
    catatan      = Column(Text)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

class PengeluaranUmum(Base):
    __tablename__ = "pengeluaran_umum"
    id           = Column(Integer, primary_key=True, index=True)
    tanggal      = Column(Date, nullable=False)
    kode_kategori= Column(String(20), nullable=False)
    keterangan   = Column(String(500), nullable=False)
    jumlah       = Column(Float, nullable=False)
    metode       = Column(String(20))
    sumber       = Column(String(20), default="manual")
    ref_id       = Column(Integer)
    bukti_file   = Column(String(500))
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

class KategoriKustom(Base):
    __tablename__ = "kategori_kustom"
    id    = Column(Integer, primary_key=True, index=True)
    kode  = Column(String(20), unique=True, nullable=False)
    nama  = Column(String(200), nullable=False)

class MasterProduk(Base):
    __tablename__ = "master_produk"
    id           = Column(Integer, primary_key=True, index=True)
    kode         = Column(String(20), unique=True, nullable=False)
    nama         = Column(String(200), nullable=False)
    satuan       = Column(String(20))
    stok         = Column(Integer, default=0)
    harga_jual   = Column(Float, default=0)
    hpp          = Column(Float, default=0)
    no_izin_edar = Column(String(100))
    keterangan   = Column(Text)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
