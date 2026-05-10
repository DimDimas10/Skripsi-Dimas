"""
main.py
=======
Entry point FastAPI — Banking Anomaly Detection REST API.

OPTIMASI vs versi lama:
1. FastAPI lifespan event (startup/shutdown) menggantikan @app.on_event deprecated
2. Model di-warmup saat STARTUP → request pertama tidak cold
3. Middleware X-Process-Time untuk monitoring latency setiap endpoint
4. Logging terstruktur untuk debugging produksi
"""

import logging
import os
import sys
import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Tambahkan root directory ke sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from backend.core.model_loader import ModelLoader
from backend.routes.api import router as api_router

# ── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Lifespan (startup + shutdown) ────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Dijalankan saat server START dan STOP.

    WARMUP MODEL: Model di-load ke RAM sebelum request pertama masuk.
    Ini mengeliminasi cold-start latency yang sebelumnya terjadi pada
    request pertama ke endpoint /predict.
    """
    logger.info("=" * 60)
    logger.info("  Banking Anomaly Detection API — Starting Up")
    logger.info("=" * 60)

    # ── Warmup model ───────────────────────────────────────────────────────
    try:
        t0 = time.perf_counter()
        ModelLoader.warmup()
        elapsed = round((time.perf_counter() - t0) * 1000, 1)
        logger.info(f"  Model ready in memory ({elapsed}ms) ✓")
    except FileNotFoundError as exc:
        logger.error(f"  GAGAL load model: {exc}")
        logger.error("  Jalankan train.py terlebih dahulu!")
        # Server tetap jalan tapi endpoint predict akan error

    logger.info("  Server siap menerima request ✓")
    logger.info("=" * 60)

    yield  # ← Server berjalan di sini

    # ── Shutdown ────────────────────────────────────────────────────────────
    logger.info("Banking Anomaly Detection API — Shutting Down")


# ── Inisialisasi Aplikasi FastAPI ────────────────────────────────────────────
app = FastAPI(
    title="Banking Anomaly Detection REST API",
    description=(
        "Backend Machine Learning untuk Deteksi Anomali Transaksi Perbankan. "
        "Menggunakan algoritma Isolation Forest dengan preprocessing pipeline "
        "terintegrasi."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# ── CORS Middleware ──────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Middleware: X-Process-Time ────────────────────────────────────────────────
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Tambahkan header X-Process-Time ke setiap response.
    Berguna untuk monitoring dan debugging latency endpoint.
    """
    t_start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = round((time.perf_counter() - t_start) * 1000, 2)
    response.headers["X-Process-Time"] = f"{elapsed_ms}ms"
    return response


# ── Routes ───────────────────────────────────────────────────────────────────
app.include_router(api_router, prefix="/api/v1")


# ── Root endpoint ─────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Banking Anomaly Detection API is running.",
        "version": "2.0.0",
        "model_loaded": ModelLoader.is_loaded(),
        "docs_url": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Endpoint health check untuk monitoring (load balancer, k8s probe, dll)."""
    model_ready = ModelLoader.is_loaded()
    return JSONResponse(
        status_code=200 if model_ready else 503,
        content={
            "status": "healthy" if model_ready else "degraded",
            "model_loaded": model_ready,
        }
    )


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Memulai Server Backend. Pastikan port 8000 kosong...")
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
