from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine, Base, SessionLocal
from routers import bahan, penerimaan, produksi, penjualan, keuangan, dashboard
from routers import auth as auth_router, users as users_router
from auth import seed_owner
import os

Base.metadata.create_all(bind=engine)

# Buat akun owner default jika belum ada
db = SessionLocal()
try:
    seed_owner(db)
finally:
    db.close()

app = FastAPI(title="Lancar ERP API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(dashboard.router)
app.include_router(bahan.router)
app.include_router(penerimaan.router)
app.include_router(produksi.router)
app.include_router(penjualan.router)
app.include_router(keuangan.router)

os.makedirs("/app/uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="/app/uploads"), name="uploads")

@app.get("/health")
def health():
    return {"status": "ok", "app": "Lancar ERP v2.0"}
