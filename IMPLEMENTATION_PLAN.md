# 🏦 Banking Anomaly Detection — Implementation Plan

> Dokumen ini menjelaskan secara menyeluruh tech stack, arsitektur, dan komponen
> yang digunakan pada setiap lapisan sistem: **Frontend**, **Backend**, dan **Machine Learning**.

---

## 📁 Struktur Proyek

```
banking_anomaly_ml/
├── anomaly_detector.py         ← ML: Kelas utama detektor anomali
├── train.py                    ← ML: Script pelatihan model
├── predict.py                  ← ML: Script prediksi mandiri (CLI)
├── banking_model.pkl           ← ML: Model terlatih (binary)
├── transactions_train.csv      ← ML: Dataset training
├── requirements.txt            ← Backend: Dependensi Python
│
├── backend/                    ← BACKEND: FastAPI REST API
│   ├── main.py                 ← Entry point server
│   ├── core/
│   │   └── model_loader.py     ← Singleton loader model
│   ├── routes/
│   │   └── api.py              ← Definisi endpoint API
│   └── services/
│       └── prediction_service.py ← Logika bisnis prediksi
│
└── frontend/                   ← FRONTEND: React + Vite
    ├── index.html
    ├── vite.config.js
    └── src/
        ├── main.jsx            ← Entry point React
        ├── App.jsx             ← Root component & routing
        ├── AppContext.jsx      ← Global state (tema, bahasa)
        ├── i18n.js             ← Konfigurasi internasionalisasi
        ├── index.css           ← Global styles & design tokens
        └── components/
            ├── Navbar.jsx
            ├── Dashboard.jsx
            ├── UploadComponent.jsx
            ├── ChartComponent.jsx
            └── TableComponent.jsx
```

---

## 🤖 Machine Learning

### Algoritma Inti
| Komponen          | Teknologi / Library              | Fungsi                                       |
|-------------------|----------------------------------|----------------------------------------------|
| **Algoritma**     | `scikit-learn` — Isolation Forest | Deteksi anomali berbasis isolasi pohon keputusan (unsupervised) |
| **Pipeline ML**   | `sklearn.pipeline.Pipeline`      | Menggabungkan preprocessing + model dalam satu objek |
| **Preprocessing** | `ColumnTransformer`              | Apply transformer berbeda ke kolom numerik & kategorikal |
| **Imputer**       | `SimpleImputer`                  | Mengisi nilai kosong (median untuk numerik, `'unknown'` untuk kategorikal) |
| **Scaler**        | `StandardScaler`                 | Normalisasi fitur numerik (mean=0, std=1) |
| **Encoder**       | `OneHotEncoder`                  | Encoding fitur kategorikal ke format biner |
| **Model Save/Load** | `joblib`                       | Serialisasi model ke file `.pkl` |
| **Manipulasi Data** | `pandas`, `numpy`              | Feature engineering, manipulasi DataFrame |

### Fitur yang Digunakan Model
**Numerik (6 fitur):**
- `Transaction Amount` — Nominal transaksi
- `Customer Age` — Usia nasabah
- `Transaction Duration` — Durasi dalam detik
- `Login Attempts` — Jumlah percobaan login
- `Account Balance` — Saldo rekening
- `Days Since Last Transaction` *(derived feature)* — Selisih hari ke transaksi sebelumnya

**Kategorikal (7 fitur):**
- `Transaction Type`, `Location`, `Device Id`, `IP Address`, `Merchant Id`, `Channel`, `Customer Occupation`

### Alur Kerja ML
```
Raw CSV Data
    │
    ▼
Feature Engineering (datetime → Days Since Last Transaction)
    │
    ▼
ColumnTransformer
  ├── Numerik  → SimpleImputer(median) → StandardScaler
  └── Kategorikal → SimpleImputer(constant='unknown') → OneHotEncoder
    │
    ▼
Isolation Forest (contamination=3%, n_estimators=100)
    │
    ▼
Output: Is Anomaly (0/1) + Anomaly Score (float)
```

### File Utama ML
| File | Peran |
|------|-------|
| [`anomaly_detector.py`](./anomaly_detector.py) | Kelas `BankingAnomalyDetector` — encapsulate training, prediksi, save/load |
| [`train.py`](./train.py) | Script training: generate data, latih model, simpan `.pkl` |
| [`predict.py`](./predict.py) | CLI script untuk prediksi dari CSV baru |
| `banking_model.pkl` | Model terlatih — di-load oleh backend saat startup |

---

## ⚙️ Backend

### Tech Stack
| Komponen            | Teknologi                      | Versi    | Fungsi                                        |
|---------------------|--------------------------------|----------|-----------------------------------------------|
| **Framework**       | `FastAPI`                      | Latest   | REST API async berkinerja tinggi              |
| **Server ASGI**     | `Uvicorn`                      | `[standard]` | Menjalankan FastAPI di atas ASGI         |
| **Model Serving**   | `joblib` + Singleton Pattern   | —        | Load model 1x di startup, tanpa cold-start    |
| **Data Handling**   | `pandas`                       | Latest   | Parsing CSV, validasi kolom, transformasi data |
| **Parsing File**    | `python-multipart`             | Latest   | Menerima file upload CSV dari frontend        |
| **CORS**            | `FastAPI CORSMiddleware`       | Built-in | Izinkan request dari localhost frontend       |
| **Logging**         | `logging` (stdlib Python)      | Built-in | Structured log untuk monitoring & debugging   |
| **Monitoring**      | Custom Middleware (`X-Process-Time`) | — | Mengukur latency tiap request (ms)         |

### Arsitektur Backend
```
HTTP Request (multipart/form-data)
    │
    ▼
FastAPI Router (/api/v1/predict)
    │
    ▼
prediction_service.py
  ├── Baca CSV → pandas DataFrame
  ├── Validasi kolom wajib
  ├── Ambil model dari ModelLoader (Singleton)
  ├── detector.predict(df) → DataFrame hasil
  └── Konversi ke JSON response
    │
    ▼
JSON Response { predictions: [...], summary: {...} }
```

### Endpoints API
| Method | Path               | Fungsi                                  |
|--------|--------------------|-----------------------------------------|
| `GET`  | `/`                | Health check + status model             |
| `GET`  | `/health`          | Health probe (200 healthy / 503 degraded) |
| `POST` | `/api/v1/predict`  | Upload CSV → return hasil deteksi anomali |
| `GET`  | `/docs`            | Swagger UI (auto-generated oleh FastAPI) |

### Pola Desain Kunci
- **Singleton** (`ModelLoader`) — Model hanya di-load 1x ke RAM, tidak di-reload per-request
- **Lifespan Event** — Warmup model saat startup dengan `@asynccontextmanager lifespan`
- **Middleware** — Monitoring latency via header `X-Process-Time`
- **Error Handling** — Response 400 jika kolom CSV tidak sesuai, 503 jika model belum siap

### File Utama Backend
| File | Peran |
|------|-------|
| [`backend/main.py`](./backend/main.py) | Entry point FastAPI, CORS, middleware, lifespan |
| [`backend/routes/api.py`](./backend/routes/api.py) | Definisi router dan endpoint `/predict` |
| [`backend/services/prediction_service.py`](./backend/services/prediction_service.py) | Logika bisnis: parse CSV, validasi, jalankan prediksi |
| [`backend/core/model_loader.py`](./backend/core/model_loader.py) | Singleton untuk load dan cache model `.pkl` |

---

## 🎨 Frontend

### Tech Stack
| Komponen              | Teknologi              | Versi    | Fungsi                                          |
|-----------------------|------------------------|----------|-------------------------------------------------|
| **Framework UI**      | `React`                | v19      | Komponen berbasis UI, reaktif                   |
| **Build Tool**        | `Vite`                 | v8       | Dev server cepat, HMR, bundling produksi        |
| **HTTP Client**       | `Axios`                | v1.14    | Kirim file CSV ke backend API                   |
| **Charting**          | `Recharts`             | v3.8     | Grafik interaktif (Bar, Pie, Line Chart)         |
| **Icon Library**      | `Lucide React`         | v1.7     | Icon SVG modular dan konsisten                  |
| **Styling**           | Vanilla CSS            | —        | Custom design system, dark/light mode, animasi  |
| **Internasionalisasi**| Custom `i18n.js`       | —        | Dukungan multi-bahasa (ID 🇮🇩 / EN 🇬🇧)           |
| **State Management**  | React Context API      | Built-in | State global: tema, bahasa, data hasil prediksi |
| **Linter**            | `ESLint`               | v9       | Code quality enforcement                        |

### Komponen UI
| Komponen | File | Fungsi |
|----------|------|--------|
| **Navbar** | `Navbar.jsx` | Navigasi atas, toggle tema 🌙/☀️, toggle bahasa |
| **Dashboard** | `Dashboard.jsx` | Halaman utama, ringkasan statistik anomali |
| **Upload** | `UploadComponent.jsx` | Drag-and-drop CSV upload, progress indikator |
| **Chart** | `ChartComponent.jsx` | Visualisasi distribusi anomali (Bar + Pie chart) |
| **Table** | `TableComponent.jsx` | Tabel hasil transaksi, highlight baris anomali, filter & sort |

### Alur Data Frontend
```
User Upload CSV
    │
    ▼
UploadComponent.jsx
  └── axios.post('/api/v1/predict', formData)
    │
    ▼
AppContext.jsx (Global State)
  └── setPredictionData(response.data)
    │
    ├──▶ Dashboard.jsx    (ringkasan: total, anomali, normal)
    ├──▶ ChartComponent.jsx (grafik distribusi)
    └──▶ TableComponent.jsx (tabel detail + highlight merah)
```

### Fitur UI Kunci
- **Dark / Light Mode** — Toggle real-time, tersimpan di Context
- **Multi-bahasa (i18n)** — Bahasa Indonesia & Inggris, semua label diambil dari `i18n.js`
- **Animasi performa tinggi** — CSS transition dinonaktifkan saat tema/bahasa bertukar (class `.no-transition`) untuk menghindari lag
- **Memoization** — Komponen berat di-wrap `React.memo` untuk mencegah re-render berlebih
- **Responsive** — Layout fleksibel dengan CSS Grid & Flexbox

---

## 🔗 Integrasi Antar Layer

```
┌─────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                    │
│  Upload CSV → Axios POST → tampilkan hasil              │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP REST (JSON / multipart)
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI)                     │
│  Terima file → Parsing CSV → Validasi → Prediksi       │
└────────────────────────┬────────────────────────────────┘
                         │ Python API call (in-process)
                         ▼
┌─────────────────────────────────────────────────────────┐
│              MACHINE LEARNING (scikit-learn)            │
│  Pipeline → Preprocessing → Isolation Forest → Output  │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 Dependensi Lengkap

### Python (Backend + ML)
```txt
pandas          ← Manipulasi data & CSV
scikit-learn    ← Pipeline ML, Isolation Forest, Preprocessing
joblib          ← Serialisasi model .pkl
numpy           ← Komputasi numerik
fastapi         ← REST API framework
uvicorn[standard] ← ASGI server
python-multipart ← File upload handling
```

### JavaScript (Frontend)
```json
"dependencies": {
  "react": "^19.2.4",
  "react-dom": "^19.2.4",
  "axios": "^1.14.0",
  "recharts": "^3.8.1",
  "lucide-react": "^1.7.0"
},
"devDependencies": {
  "vite": "^8.0.4",
  "@vitejs/plugin-react": "^6.0.1",
  "eslint": "^9.39.4"
}
```

---

## 🚀 Cara Menjalankan

### 1. Latih Model (sekali saja)
```bash
cd banking_anomaly_ml
python train.py
```

### 2. Jalankan Backend
```bash
python -m backend.main
# Server berjalan di: http://localhost:8000
# Swagger UI: http://localhost:8000/docs
```

### 3. Jalankan Frontend
```bash
cd frontend
npm install
npm run dev
# UI berjalan di: http://localhost:5173
```

---

*Dokumen dibuat: 2026-04-26 | Versi sistem: 2.0.0*
