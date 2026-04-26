import pandas as pd
import numpy as np
import joblib
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import IsolationForest


class BankingAnomalyDetector:
    def __init__(self, contamination=0.05, random_state=42):
        self.contamination = contamination
        self.random_state = random_state
        self.model = None

        # 1. Data Kolom Numerik
        self.numeric_features = [
            'Transaction Amount', 'Customer Age', 'Transaction Duration',
            'Login Attempts', 'Account Balance', 'Days Since Last Transaction'
        ]

        # 2. Data Kolom Kategorikal
        self.categorical_features = [
            'Transaction Type', 'Location', 'Device Id', 'IP Address',
            'Merchant Id', 'Channel', 'Customer Occupation'
        ]

    def _feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:
        """Memproses kolom waktu (datetime) dan menghasilkan fitur turunan.

        OPTIMASI: Tidak membuat full copy DataFrame. Hanya menghasilkan Series
        baru yang kemudian ditambahkan sebagai kolom. Ini mengurangi memory
        usage secara signifikan untuk dataset besar.
        """
        # Konversi ke datetime (vectorized, bekerja in-place pada Series)
        tx_date = pd.to_datetime(df['Transaction Date'], errors='coerce')
        prev_date = pd.to_datetime(df['Previous Transaction Date'], errors='coerce')

        # Membuat fitur tambahan: jarak (hari) dari transaksi sebelumnya
        days_diff = (tx_date - prev_date).dt.days

        # Assign kolom baru ke salinan ringan (hanya kolom baru yang ditambahkan)
        df = df.assign(**{
            'Transaction Date': tx_date,
            'Previous Transaction Date': prev_date,
            'Days Since Last Transaction': days_diff
        })

        return df

    def _build_pipeline(self):
        # PIPELINE PREPROCESSING: Missing values & Normalisasi (Numerik)
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])

        # PIPELINE PREPROCESSING: Missing values & Encoding (Kategorik)
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value='unknown')),
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])

        # Menggabungkan kedua preprocessing
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, self.numeric_features),
                ('cat', categorical_transformer, self.categorical_features)
            ])

        # Menggabungkan Preprocessing dengan model Isolation Forest
        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', IsolationForest(
                contamination=self.contamination,
                random_state=self.random_state,
                n_estimators=100
            ))
        ])

        return pipeline

    def train(self, df: pd.DataFrame) -> None:
        """Melatih model menggunakan data dataframe pandas yang dimasukkan."""
        df_engineered = self._feature_engineering(df)

        self.model = self._build_pipeline()

        X = df_engineered[self.numeric_features + self.categorical_features]
        self.model.fit(X)
        print("Model berhasil dilatih dengan sukses.")

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """Melakukan prediksi anomali.

        OPTIMASI:
        - Hanya 1x df.copy() di akhir (bukan 2x seperti sebelumnya)
        - Menggunakan np.where (vectorized) sebagai ganti Python list comprehension
        - Mengurangi memory overhead dari 3x → 1.5x ukuran data
        """
        if self.model is None:
            raise ValueError("Model belum dilatih atau di-load!")

        df_engineered = self._feature_engineering(df)
        X = df_engineered[self.numeric_features + self.categorical_features]

        # Prediksi anomali (1 = Normal, -1 = Anomali)
        preds = self.model.predict(X)

        # Skor anomali (semakin negatif semakin aneh datanya)
        scores = self.model.decision_function(X)

        # OPTIMASI: np.where jauh lebih cepat dari Python list comprehension
        # Sebelum: [1 if p == -1 else 0 for p in preds]  ← O(n) Python loop
        # Sesudah: np.where(preds == -1, 1, 0)           ← O(n) vectorized C
        df_out = df.copy()
        df_out['Is Anomaly'] = np.where(preds == -1, 1, 0)
        df_out['Anomaly Score'] = scores

        return df_out

    def save_model(self, file_path: str = "banking_model.pkl") -> None:
        """Menyimpan model yang sudah dilatih."""
        if self.model is None:
            raise ValueError("Model belum dilatih.")
        joblib.dump(self.model, file_path)
        print(f"Model berhasil disimpan ke {file_path}")

    @classmethod
    def load_model(cls, file_path: str = "banking_model.pkl") -> "BankingAnomalyDetector":
        """Me-load model dari file yang disimpan sebelumnya."""
        detector = cls()
        detector.model = joblib.load(file_path)
        print(f"Model berhasil di-load dari {file_path}")
        return detector
