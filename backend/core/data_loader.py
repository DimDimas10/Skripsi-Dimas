"""
data_loader.py
==============
Modul untuk mapping dan validasi kolom dataset CSV.

OPTIMASI UTAMA:
1. Mapping dictionary di-build sekali sebagai konstanta module-level (bukan per-call)
2. @lru_cache pada fungsi validasi yang deterministik → tidak hitung ulang
3. Set lookup O(1) untuk cek kolom yang diperlukan
"""

from __future__ import annotations
from functools import lru_cache
from typing import FrozenSet
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# OPTIMASI: Mapping menggunakan key yang sudah dinormalisasi (lowercase, no space/underscore)
# ---------------------------------------------------------------------------
_COLUMN_MAPPING: dict[str, str] = {
    # Transaction identifiers
    'transactionid': 'Transaction ID',
    'trxid': 'Transaction ID',
    'idtransaksi': 'Transaction ID',
    'idtrx': 'Transaction ID',
    # Account
    'accountid': 'Account Id',
    'accid': 'Account Id',
    'nomorrekening': 'Account Id',
    'norek': 'Account Id',
    # Amount
    'transactionamount': 'Transaction Amount',
    'amount': 'Transaction Amount',
    'trxamount': 'Transaction Amount',
    'nominal': 'Transaction Amount',
    'jumlah': 'Transaction Amount',
    # Date
    'transactiondate': 'Transaction Date',
    'date': 'Transaction Date',
    'trxdate': 'Transaction Date',
    'tanggal': 'Transaction Date',
    'tanggaltransaksi': 'Transaction Date',
    'waktu': 'Transaction Date',
    'waktutransaksi': 'Transaction Date',
    'tgl': 'Transaction Date',
    'timestamp': 'Transaction Date',
    # Type
    'transactiontype': 'Transaction Type',
    'type': 'Transaction Type',
    'trxtype': 'Transaction Type',
    'jenistransaksi': 'Transaction Type',
    'tipetransaksi': 'Transaction Type',
    # Location
    'location': 'Location',
    'lokasi': 'Location',
    'city': 'Location',
    'kota': 'Location',
    # Device
    'deviceid': 'Device Id',
    'device': 'Device Id',
    'perangkat': 'Device Id',
    'idperangkat': 'Device Id',
    # IP
    'ipaddress': 'IP Address',
    'ip': 'IP Address',
    'alamatip': 'IP Address',
    # Merchant
    'merchantid': 'Merchant Id',
    'merchant': 'Merchant Id',
    'idmerchant': 'Merchant Id',
    'toko': 'Merchant Id',
    # Channel
    'channel': 'Channel',
    'kanal': 'Channel',
    'saluran': 'Channel',
    # Customer
    'customerage': 'Customer Age',
    'age': 'Customer Age',
    'umur': 'Customer Age',
    'usia': 'Customer Age',
    'customeroccupation': 'Customer Occupation',
    'occupation': 'Customer Occupation',
    'occupationid': 'Customer Occupation',
    'pekerjaan': 'Customer Occupation',
    # Duration & Attempts
    'transactionduration': 'Transaction Duration',
    'duration': 'Transaction Duration',
    'trxduration': 'Transaction Duration',
    'durasi': 'Transaction Duration',
    'durasitransaksi': 'Transaction Duration',
    'loginattempts': 'Login Attempts',
    'jumlahlogin': 'Login Attempts',
    'percobaanlogin': 'Login Attempts',
    # Balance
    'accountbalance': 'Account Balance',
    'balance': 'Account Balance',
    'saldo': 'Account Balance',
    'saldorekening': 'Account Balance',
    # Previous date
    'previoustransactiondate': 'Previous Transaction Date',
    'prevtransactiondate': 'Previous Transaction Date',
    'prevdate': 'Previous Transaction Date',
    'tanggalsebelumnya': 'Previous Transaction Date',
    'transaksiterakhir': 'Previous Transaction Date',
}


def map_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rename kolom DataFrame dengan normalisasi tingkat tinggi.
    Mendukung berbagai variasi case, spasi, dan underscore.
    """
    # 1. Bersihkan nama kolom dari spasi liar di awal/akhir
    df.columns = [str(col).strip() for col in df.columns]

    # Pre-calculate targets untuk pencocokan case-insensitive langsung
    valid_targets = set(_COLUMN_MAPPING.values())
    valid_targets_lower = {t.lower(): t for t in valid_targets}

    # 2. Buat mapping
    rename_dict = {}
    for col in df.columns:
        col_lower = col.lower()
        
        # Prioritas 1: Cocok persis dengan target (tapi mungkin beda case)
        if col_lower in valid_targets_lower:
            target_name = valid_targets_lower[col_lower]
            if col != target_name:
                rename_dict[col] = target_name
            continue
            
        # Prioritas 2: Normalisasi (hapus spasi & underscore) lalu cek mapping
        col_norm = col_lower.replace(' ', '').replace('_', '')
        if col_norm in _COLUMN_MAPPING:
            target_name = _COLUMN_MAPPING[col_norm]
            if col != target_name:
                rename_dict[col] = target_name

    return df.rename(columns=rename_dict)


@lru_cache(maxsize=32)
def get_required_features(
    numeric_features: tuple[str, ...],
    categorical_features: tuple[str, ...],
    computed_features: tuple[str, ...]
) -> FrozenSet[str]:
    """
    Kembalikan set kolom yang wajib ada dalam CSV upload.

    @lru_cache: hasil di-cache berdasarkan argumen. Karena numeric_features,
    categorical_features, dan computed_features tidak berubah selama runtime,
    fungsi ini hanya dihitung sekali dan hasilnya dipakai ulang.

    Parameter berupa tuple (bukan list) agar hashable dan dapat di-cache.
    """
    all_required = set(numeric_features) | set(categorical_features)
    # Tambahkan kolom datetime yang diperlukan untuk feature engineering
    all_required.update(['Transaction Date'])
    # Hapus kolom yang di-generate otomatis (tidak perlu ada di CSV upload)
    all_required -= set(computed_features)
    return frozenset(all_required)


def validate_columns(df: pd.DataFrame, required: FrozenSet[str]) -> list[str]:
    """
    Cek kolom yang kurang dari DataFrame.

    Menggunakan set lookup O(1) — jauh lebih cepat dari list comprehension
    untuk dataset dengan banyak kolom.
    """
    existing = set(df.columns)
    missing = [col for col in required if col not in existing]
    return missing
