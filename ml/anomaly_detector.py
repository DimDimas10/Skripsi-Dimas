import pandas as pd
import numpy as np
import joblib
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import IsolationForest


class BankingAnomalyDetector:
    def __init__(self, contamination=0.20, random_state=42):
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
        
        # Cek apakah kolom Previous Transaction Date ada, jika tidak fallback ke Transaction Date
        if 'Previous Transaction Date' in df.columns:
            prev_date = pd.to_datetime(df['Previous Transaction Date'], errors='coerce')
        else:
            prev_date = tx_date

        # Membuat fitur tambahan: jarak (hari) dari transaksi sebelumnya
        # Jika data kosong (NaT), isi dengan 0
        days_diff = (tx_date - prev_date).dt.days.fillna(0)

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
        """Melakukan prediksi anomali."""
        if self.model is None:
            raise ValueError("Model belum dilatih atau di-load!")

        df_engineered = self._feature_engineering(df)

        # ROBUSTNESS: Pastikan kolom numerik benar-benar bertipe numerik
        for col in self.numeric_features:
            if col in df_engineered.columns:
                df_engineered[col] = pd.to_numeric(df_engineered[col], errors='coerce').astype(float)

        X = df_engineered[self.numeric_features + self.categorical_features]

        try:
            # Prediksi anomali (1 = Normal, -1 = Anomali)
            preds = self.model.predict(X)
            # Skor anomali (semakin negatif semakin aneh datanya)
            scores = self.model.decision_function(X)
        except ValueError as e:
            err_msg = str(e)
            if "could not convert string to float" in err_msg:
                # Cari tahu kolom mana yang bermasalah
                for col in X.columns:
                    try:
                        X[col].astype(float)
                    except:
                        # Temukan baris pertama yang bermasalah
                        for val in X[col].dropna().unique():
                            try:
                                float(val)
                            except:
                                raise ValueError(
                                    f"Kolom '{col}' mengandung nilai non-angka: '{val}'. "
                                    f"Pastikan kolom ini masuk ke categorical_features atau bersihkan datanya."
                                ) from e
            raise

        df_out = df.copy()
        df_out['Is Anomaly'] = np.where(preds == -1, 1, 0)
        df_out['Anomaly Score'] = scores

        return df_out

    def save_model(self, file_path: str = "banking_model.pkl") -> None:
        """Menyimpan model yang sudah dilatih dalam format bundle dictionary."""
        if self.model is None:
            raise ValueError("Model belum dilatih.")
        
        # Simpan dalam format bundle sesuai instruksi user
        bundle = {
            'model': self.model,
            'contamination': self.contamination,
            'numeric_features': self.numeric_features,
            'categorical_features': self.categorical_features
        }
        joblib.dump(bundle, file_path)
        print(f"Model berhasil disimpan ke {file_path}")

    @classmethod
    def load_model(cls, file_path: str = "banking_model.pkl") -> "BankingAnomalyDetector":
        """Me-load model dari file yang disimpan sebelumnya."""
        detector = cls()
        bundle = joblib.load(file_path)
        
        # Cek apakah formatnya bundle dictionary atau model langsung
        if isinstance(bundle, dict) and 'model' in bundle:
            detector.model = bundle['model']
            detector.contamination = bundle.get('contamination', detector.contamination)
            
            # Load feature lists jika ada di bundle
            if 'numeric_features' in bundle:
                detector.numeric_features = bundle['numeric_features']
            if 'categorical_features' in bundle:
                detector.categorical_features = bundle['categorical_features']
            
            # Jika feature lists TIDAK ada di bundle, coba ekstrak dari Pipeline
            elif hasattr(detector.model, 'named_steps'):
                preprocessor = detector.model.named_steps.get('preprocessor')
                if preprocessor and hasattr(preprocessor, 'transformers_'):
                    # Ekstrak kolom dari ColumnTransformer
                    for name, transformer, cols in preprocessor.transformers_:
                        if name == 'num':
                            detector.numeric_features = list(cols)
                        elif name == 'cat':
                            detector.categorical_features = list(cols)
        else:
            detector.model = bundle
            
        print(f"Model berhasil di-load dari {file_path}")
        return detector
