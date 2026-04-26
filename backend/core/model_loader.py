"""
model_loader.py
===============
Singleton thread-safe untuk loading model Isolation Forest sekali saja ke memory.

OPTIMASI UTAMA:
1. Model di-load SEKALI saat server startup (bukan lazy per-request)
2. Thread-safe menggunakan threading.Lock → aman untuk concurrent requests
3. Warmup function dipanggil oleh FastAPI startup event
"""

import os
import sys
import threading
import logging

# Menambahkan path root agar bisa import ml package dari root project
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from ml.anomaly_detector import BankingAnomalyDetector

logger = logging.getLogger(__name__)

# Lokasi default model (relatif dari root project)
_DEFAULT_MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../ml/models/banking_model.pkl')
)


class ModelLoader:
    """
    Singleton thread-safe untuk menyimpan instance BankingAnomalyDetector.

    Keunggulan vs ModelStore lama:
    - threading.Lock mencegah race condition saat concurrent request pertama
    - Warmup eksplisit memastikan model sudah ada di RAM sebelum request masuk
    - Logging memudahkan monitoring waktu load
    """
    _instance: BankingAnomalyDetector | None = None
    _lock: threading.Lock = threading.Lock()
    _model_path: str = _DEFAULT_MODEL_PATH

    @classmethod
    def configure(cls, model_path: str) -> None:
        """Atur path model sebelum warmup. Harus dipanggil sebelum warmup()."""
        cls._model_path = model_path

    @classmethod
    def warmup(cls) -> None:
        """
        Load model ke RAM sekarang (blocking).
        Dipanggil saat FastAPI startup event — sebelum request pertama masuk.
        """
        with cls._lock:
            if cls._instance is None:
                if not os.path.exists(cls._model_path):
                    raise FileNotFoundError(
                        f"[ModelLoader] File model tidak ditemukan: {cls._model_path}\n"
                        "Jalankan train.py terlebih dahulu untuk menghasilkan file .pkl."
                    )
                logger.info(f"[ModelLoader] Loading model dari: {cls._model_path}")
                cls._instance = BankingAnomalyDetector.load_model(cls._model_path)
                logger.info("[ModelLoader] Model berhasil di-load dan siap digunakan.")
            else:
                logger.info("[ModelLoader] Model sudah ada di memory, skip reload.")

    @classmethod
    def get(cls) -> BankingAnomalyDetector:
        """
        Ambil instance model yang sudah ada di RAM.
        Jika belum diload (misal warmup belum dipanggil), load sekarang (lazy fallback).
        """
        if cls._instance is None:
            logger.warning("[ModelLoader] Model belum di-warmup, melakukan lazy load...")
            cls.warmup()
        return cls._instance

    @classmethod
    def is_loaded(cls) -> bool:
        """Cek apakah model sudah ada di memory."""
        return cls._instance is not None

    @classmethod
    def reload(cls) -> None:
        """Force reload model (berguna saat model di-update tanpa restart server)."""
        with cls._lock:
            cls._instance = None
        logger.info("[ModelLoader] Model di-reset, akan di-load ulang pada request berikutnya.")
        cls.warmup()
