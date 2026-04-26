"""
train.py — Script Pelatihan Model
==================================
Generate dummy data, latih Isolation Forest, dan simpan model ke ml/models/.

Cara menjalankan:
    python -m ml.train
"""

import os
import pandas as pd
import numpy as np
from .anomaly_detector import BankingAnomalyDetector

# Direktori file ini
_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(_DIR, 'data')
_MODELS_DIR = os.path.join(_DIR, 'models')


def generate_dummy_data(n=1000):
    """Fungsi bantu untuk men-generate data sampel sesuai atribut baru."""
    np.random.seed(42)
    
    # 1. Atribut Waktu
    dates = pd.date_range(start='2025-01-01', periods=n, freq='10h')
    prev_dates = dates - pd.to_timedelta(np.random.randint(1, 10, size=n), unit='D')
    
    data = {
        'Transaction ID': [f"TRX{i:05d}" for i in range(1, n+1)],
        'Account Id': [f"ACC{np.random.randint(1, 100):03d}" for _ in range(n)],
        'Transaction Amount': np.random.lognormal(mean=5, sigma=1.5, size=n),
        'Transaction Date': dates,
        'Transaction Type': np.random.choice(['Transfer', 'Payment', 'Withdrawal', 'Deposit'], size=n),
        'Location': np.random.choice(['Jakarta', 'Surabaya', 'Bandung', 'Medan', 'Bali'], size=n),
        'Device Id': np.random.choice(['DEV1', 'DEV2', 'DEV3', 'DEV4'], size=n),
        'IP Address': np.random.choice(['192.168.1.1', '10.0.0.1', '172.16.0.1'], size=n),
        'Merchant Id': np.random.choice(['M001', 'M002', 'M003', 'M004'], size=n),
        'Channel': np.random.choice(['Mobile Banking', 'Internet Banking', 'ATM'], size=n),
        'Customer Age': np.random.randint(18, 70, size=n),
        'Customer Occupation': np.random.choice(['Wiraswasta', 'PNS', 'Karyawan Swasta', 'Pelajar'], size=n),
        'Transaction Duration': np.random.randint(10, 300, size=n), # in seconds
        'Login Attempts': np.random.randint(1, 5, size=n),
        'Account Balance': np.random.uniform(100000, 50000000, size=n),
        'Previous Transaction Date': prev_dates
    }
    
    df = pd.DataFrame(data)
    
    # Sengaja sisipkan missing values untuk ditangani oleh Preprocessing
    df.loc[10:20, 'Transaction Amount'] = np.nan
    df.loc[50:60, 'Location'] = np.nan
    
    return df

if __name__ == "__main__":
    print("1. Menyiapkan Dataset CSV...")
    df_train = generate_dummy_data()
    csv_path = os.path.join(_DATA_DIR, 'transactions_train.csv')
    df_train.to_csv(csv_path, index=False)
    
    print("\n2. Membaca Data dari CSV...")
    df = pd.read_csv(csv_path)
    
    print("\n3. Inisialisasi Modul Anomaly Detector...")
    detector = BankingAnomalyDetector(contamination=0.03) # 3% anomali
    
    print("\n4. Melatih Model...")
    detector.train(df)
    
    print("\n5. Menyimpan Model ke File (.pkl)...")
    model_path = os.path.join(_MODELS_DIR, 'banking_model.pkl')
    detector.save_model(model_path)
    print(f"   Tersimpan di: {model_path}")
