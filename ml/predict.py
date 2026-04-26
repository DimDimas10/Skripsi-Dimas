"""
predict.py — Script Prediksi Mandiri (CLI)
===========================================
Load model terlatih dan jalankan prediksi pada data baru.

Cara menjalankan:
    python -m ml.predict
"""

import os
import pandas as pd
from .anomaly_detector import BankingAnomalyDetector
from .train import generate_dummy_data

# Direktori file ini
_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(_DIR, 'data')
_MODELS_DIR = os.path.join(_DIR, 'models')

if __name__ == "__main__":
    print("1. Meload Model dari File (.pkl)...")
    model_path = os.path.join(_MODELS_DIR, 'banking_model.pkl')
    detector = BankingAnomalyDetector.load_model(model_path)
    
    print("\n2. Menyiapkan Data Transaksi Baru (Streaming / Upload CSV)...")
    # Anggap ini adalah data transaksi yang baru masuk atau di-upload via Frontend
    df_new = generate_dummy_data(n=10) # 10 transaksi baru untuk contoh prediksi
    
    print("\n3. Melakukan Prediksi Anomali...")
    df_result = detector.predict(df_new)
    
    print("\n[HASIL PREDIKSI]")
    # Menampilkan hasil label (is_anomaly) dan skor
    columns_to_show = ['Transaction ID', 'Transaction Amount', 'Transaction Type', 'Is Anomaly', 'Anomaly Score']
    print(df_result[columns_to_show])
    
    # Deteksi jumlah anomali
    anomalies_found = df_result[df_result['Is Anomaly'] == 1].shape[0]
    print(f"\nDitemukan {anomalies_found} anomali dari {len(df_new)} transaksi baru.")
    
    # Simpan hasil prediksi
    result_path = os.path.join(_DATA_DIR, 'prediction_results.csv')
    df_result.to_csv(result_path, index=False)
    print(f"\nHasil lengkap disimpan di {result_path}")
