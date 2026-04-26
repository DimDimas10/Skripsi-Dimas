"""
ml — Machine Learning Module
=============================
Modul utama untuk deteksi anomali transaksi perbankan
menggunakan algoritma Isolation Forest (scikit-learn).

Submodul:
    - anomaly_detector : Kelas BankingAnomalyDetector
    - train            : Script pelatihan model
    - predict          : Script prediksi mandiri (CLI)
"""

from .anomaly_detector import BankingAnomalyDetector

__all__ = ["BankingAnomalyDetector"]
