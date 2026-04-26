"""
prediction_service.py
=====================
Service layer: parsing CSV, validasi kolom, dan menjalankan prediksi.

OPTIMASI UTAMA vs versi lama:
1. CSV parsing 1x saja (lama: baca 2x jika deteksi semicolon)
   → Gunakan csv.Sniffer untuk deteksi separator tanpa re-read
2. Column mapping menggunakan konstanta module-level dari data_loader
   → Tidak rebuild dict 70 entry setiap request
3. Validasi kolom menggunakan @lru_cache (frozenset) dari data_loader
   → Tidak compute ulang set operasi setiap request
4. Prediksi dengan chunking dari core.predict
   → Aman untuk file besar (>10k baris), tidak OOM
5. Post-processing optimized (2-pass) dari core.predict
   → Gantikan triple-pass (replace + where + to_dict)
"""

import csv
import io
import logging
import time

import numpy as np
import pandas as pd

from backend.core.data_loader import map_columns, get_required_features, validate_columns
from backend.core.model_loader import ModelLoader
from backend.core.predict import predict_chunked, postprocess_to_records

logger = logging.getLogger(__name__)


def _parse_csv(file_bytes: bytes) -> pd.DataFrame:
    """
    Parse bytes CSV ke DataFrame dengan deteksi separator otomatis.

    OPTIMASI: Gunakan csv.Sniffer untuk membaca baris pertama saja
    dan mendeteksi delimiter — tidak perlu membaca seluruh file dua kali.

    Kode lama (2 read):
        df = pd.read_csv(BytesIO(file_bytes))
        if len(df.columns) == 1 and ';' in df.columns[0]:
            df = pd.read_csv(BytesIO(file_bytes), sep=';')  ← baca ulang!

    Kode baru (1 read):
        Sniff separator dari baris pertama, lalu baca sekali.
    """
    try:
        # Decode sebagian kecil untuk sniff (tidak perlu decode seluruh file)
        sample = file_bytes[:4096].decode('utf-8', errors='ignore')
        sniffer = csv.Sniffer()
        try:
            dialect = sniffer.sniff(sample, delimiters=',;\t|')
            separator = dialect.delimiter
        except csv.Error:
            separator = ','  # fallback ke koma

        df = pd.read_csv(io.BytesIO(file_bytes), sep=separator, low_memory=False)
        return df
    except Exception as exc:
        raise ValueError(f"Gagal memparsing isi CSV: {exc}") from exc


def process_and_predict(file_bytes: bytes) -> dict:
    """
    Terima bytes dari file CSV, jalankan prediksi anomali, kembalikan dict JSON.

    Flow:
    1. Parse CSV (1x read dengan sniff separator)
    2. Map nama kolom (konstanta module-level, tidak rebuild tiap call)
    3. Validasi kolom wajib (cached hasil frozenset)
    4. Prediksi chunked (aman untuk file besar)
    5. Post-processing optimized (2 pass)
    6. Return dict JSON-serializable
    """
    t_start = time.perf_counter()

    # ── 1. Parse CSV ─────────────────────────────────────────────────────────
    df = _parse_csv(file_bytes)
    logger.debug(f"[service] CSV parsed: {len(df)} baris, {len(df.columns)} kolom")

    # ── 2. Map kolom ─────────────────────────────────────────────────────────
    df = map_columns(df)

    # ── 3. Validasi kolom ────────────────────────────────────────────────────
    detector = ModelLoader.get()

    required = get_required_features(
        numeric_features=tuple(detector.numeric_features),
        categorical_features=tuple(detector.categorical_features),
        computed_features=('Days Since Last Transaction',)
    )
    missing_cols = validate_columns(df, required)
    if missing_cols:
        raise ValueError(
            f"Format dataset tidak valid. Kolom berikut wajib ada: {', '.join(sorted(missing_cols))}"
        )

    # ── 4. Prediksi (chunked) ────────────────────────────────────────────────
    try:
        results_df = predict_chunked(detector, df)
    except Exception as exc:
        raise ValueError(f"Terjadi kesalahan saat ML melakukan prediksi: {exc}") from exc

    # ── 5. Post-processing → records ─────────────────────────────────────────
    records = postprocess_to_records(results_df)

    anomalies_detected = int(
        results_df['Is Anomaly'].sum()
    ) if 'Is Anomaly' in results_df.columns else 0

    elapsed_ms = round((time.perf_counter() - t_start) * 1000, 2)
    logger.info(
        f"[service] Selesai: {len(records)} baris, {anomalies_detected} anomali, {elapsed_ms}ms"
    )

    return {
        "status": "success",
        "total_processed": len(records),
        "anomalies_detected": anomalies_detected,
        "processing_time_ms": elapsed_ms,
        "results": records
    }
