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
# OPTIMASI: Konstanta module-level — tidak perlu rebuild tiap pemanggilan fungsi
# ---------------------------------------------------------------------------
_COLUMN_MAPPING: dict[str, str] = {
    # Transaction identifiers
    'TransactionID': 'Transaction ID',
    'transactionid': 'Transaction ID',
    'transaction_id': 'Transaction ID',
    # Account
    'AccountID': 'Account Id',
    'accountid': 'Account Id',
    'account_id': 'Account Id',
    # Amount
    'TransactionAmount': 'Transaction Amount',
    'Amount': 'Transaction Amount',
    'amount': 'Transaction Amount',
    'transaction_amount': 'Transaction Amount',
    # Date
    'TransactionDate': 'Transaction Date',
    'Date': 'Transaction Date',
    'date': 'Transaction Date',
    'transaction_date': 'Transaction Date',
    # Type
    'TransactionType': 'Transaction Type',
    'Type': 'Transaction Type',
    'type': 'Transaction Type',
    'transaction_type': 'Transaction Type',
    # Location
    'location': 'Location',
    # Device
    'DeviceID': 'Device Id',
    'Device': 'Device Id',
    'device': 'Device Id',
    'device_id': 'Device Id',
    # IP
    'IPAddress': 'IP Address',
    'IP': 'IP Address',
    'ip': 'IP Address',
    'ip_address': 'IP Address',
    # Merchant
    'MerchantID': 'Merchant Id',
    'merchant_id': 'Merchant Id',
    # Channel
    'channel': 'Channel',
    # Customer
    'CustomerAge': 'Customer Age',
    'Age': 'Customer Age',
    'age': 'Customer Age',
    'customer_age': 'Customer Age',
    'CustomerOccupation': 'Customer Occupation',
    'Occupation': 'Customer Occupation',
    'occupation': 'Customer Occupation',
    'customer_occupation': 'Customer Occupation',
    # Duration & Attempts
    'TransactionDuration': 'Transaction Duration',
    'Duration': 'Transaction Duration',
    'duration': 'Transaction Duration',
    'transaction_duration': 'Transaction Duration',
    'LoginAttempts': 'Login Attempts',
    'login_attempts': 'Login Attempts',
    # Balance
    'AccountBalance': 'Account Balance',
    'Balance': 'Account Balance',
    'balance': 'Account Balance',
    'account_balance': 'Account Balance',
    # Previous date
    'PreviousTransactionDate': 'Previous Transaction Date',
    'previous_transaction_date': 'Previous Transaction Date',
}


def map_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rename kolom DataFrame sesuai mapping referensi.

    Menggunakan konstanta module-level (_COLUMN_MAPPING) yang hanya
    di-build sekali saat module di-import, bukan tiap kali fungsi dipanggil.
    """
    return df.rename(columns=_COLUMN_MAPPING)


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
    all_required.update(['Transaction Date', 'Previous Transaction Date'])
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
