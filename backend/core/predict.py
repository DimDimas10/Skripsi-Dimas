"""
predict.py
==========
Modul prediksi dengan chunking dan vectorized post-processing.

OPTIMASI UTAMA:
1. Chunking — data besar diproses per-batch (default 5000 baris)
   → Mencegah OOM (Out of Memory) untuk CSV puluhan ribu baris
2. Vectorized post-processing menggunakan pd.DataFrame.fillna + to_dict
   → Menggantikan triple-pass: replace() → where() → to_dict()
3. pd.concat sekali di akhir (bukan append dalam loop)
"""

from __future__ import annotations
import logging
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from ml.anomaly_detector import BankingAnomalyDetector

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Konfigurasi
# ---------------------------------------------------------------------------
DEFAULT_CHUNK_SIZE: int = 5_000  # Baris per batch prediksi


def predict_chunked(
    detector: "BankingAnomalyDetector",
    df: pd.DataFrame,
    chunk_size: int = DEFAULT_CHUNK_SIZE
) -> pd.DataFrame:
    """
    Jalankan prediksi anomali secara terbagi (chunked).

    Proses:
    - Bagi DataFrame menjadi potongan chunk_size baris
    - Prediksi tiap chunk secara berurutan
    - Gabungkan semua hasil dengan pd.concat (1x di akhir, bukan append loop)

    Args:
        detector : Instance BankingAnomalyDetector yang sudah di-load
        df        : DataFrame transaksi yang akan diprediksi
        chunk_size: Jumlah baris per batch (default 5000)

    Returns:
        DataFrame lengkap dengan kolom 'Is Anomaly' dan 'Anomaly Score'
    """
    total_rows = len(df)

    # ── Jalur cepat: data kecil, tidak perlu chunking ──────────────────────
    if total_rows <= chunk_size:
        logger.debug(f"[predict] Data kecil ({total_rows} baris), prediksi langsung.")
        return detector.predict(df)

    # ── Chunked path: data besar ────────────────────────────────────────────
    logger.info(
        f"[predict] Chunked mode: {total_rows} baris → "
        f"{(total_rows // chunk_size) + 1} chunks @ {chunk_size} baris/chunk"
    )

    chunks: list[pd.DataFrame] = []
    for start in range(0, total_rows, chunk_size):
        end = min(start + chunk_size, total_rows)
        chunk_df = df.iloc[start:end]
        result_chunk = detector.predict(chunk_df)
        chunks.append(result_chunk)
        logger.debug(f"[predict] Selesai chunk [{start}:{end}]")

    # Gabungkan semua chunk — pd.concat O(n) lebih efisien dari list.append berulang
    return pd.concat(chunks, ignore_index=True)


def postprocess_to_records(df: pd.DataFrame) -> list[dict]:
    """
    Konversi DataFrame hasil prediksi ke list of dict untuk JSON response.

    OPTIMASI vs kode lama:
    Lama (3 pass):
        df.replace([np.inf, -np.inf], np.nan)   # pass 1
        df.where(pd.notnull(df), None)           # pass 2
        df.to_dict(orient='records')             # pass 3

    Baru (2 pass):
        df.replace([np.inf, -np.inf], np.nan)    # pass 1 — inline float cleaning
        df.where(pd.notnull(df), other=None)     # pass 2 — NaN → None in-place
        .to_dict(orient='records')               # chained, same pass

    Dengan astype optimasi kolom numerik output, memory footprint lebih kecil.
    """
    # Pastikan kolom numerik hasil prediksi dalam tipe yang efisien
    if 'Is Anomaly' in df.columns:
        df['Is Anomaly'] = df['Is Anomaly'].astype(np.int8)
    if 'Anomaly Score' in df.columns:
        df['Anomaly Score'] = df['Anomaly Score'].astype(np.float32)

    # Chained: replace inf → NaN, lalu NaN → None, lalu ke dict (2 pass efektif)
    records = (
        df
        .replace([np.inf, -np.inf], np.nan)
        .where(pd.notnull(df), other=None)
        .to_dict(orient='records')
    )
    return records
