# 📂 Struktur File — Banking Anomaly Detection System

> Panduan lengkap organisasi file yang dikelompokkan berdasarkan
> **Machine Learning**, **Backend**, dan **Frontend**.

---

## 🗂️ Struktur Lengkap

```
banking_anomaly_ml/
│
│── IMPLEMENTATION_PLAN.md          📋 Dokumen perencanaan sistem
│── STRUKTUR_FILE.md                📋 Dokumen ini
│── requirements.txt                📦 Dependensi Python (Backend + ML)
│
│
│── ─────────────────────────────────────────────────────────
│── 🤖 MACHINE LEARNING
│── ─────────────────────────────────────────────────────────
│
├── ml/                             🤖 Package Machine Learning
│   │── __init__.py                 📦 Package marker (export BankingAnomalyDetector)
│   │── anomaly_detector.py         🧠 Kelas utama BankingAnomalyDetector
│   │                                  ├─ Feature engineering (datetime → days)
│   │                                  ├─ Build sklearn Pipeline
│   │                                  ├─ train(), predict()
│   │                                  └─ save_model(), load_model()
│   │
│   │── train.py                    🏋️ Script pelatihan model
│   │                                  ├─ Generate dummy data (1000 rows)
│   │                                  ├─ Latih Isolation Forest
│   │                                  └─ Simpan ke ml/models/banking_model.pkl
│   │
│   │── predict.py                  🔮 Script prediksi mandiri (CLI)
│   │                                  ├─ Load model .pkl
│   │                                  ├─ Baca CSV baru
│   │                                  └─ Output: ml/data/prediction_results.csv
│   │
│   ├── models/                     💾 Folder model terlatih
│   │   │── banking_model.pkl       💾 Model utama (~2MB)
│   │   │── banking_anomaly_model.pkl 💾 Model alternatif
│   │   └── isolation_forest_model.pkl 💾 Model versi lama
│   │
│   └── data/                       📊 Folder dataset & output
│       │── transactions_train.csv  📊 Dataset training (1000 transaksi)
│       └── prediction_results.csv  📊 Hasil prediksi terakhir
│
│
│── ─────────────────────────────────────────────────────────
│── ⚙️ BACKEND (FastAPI)
│── ─────────────────────────────────────────────────────────
│
├── backend/
│   │── __init__.py                 📦 Package marker
│   │── main.py                     🚀 Entry point server FastAPI
│   │                                  ├─ Inisialisasi app
│   │                                  ├─ CORS middleware
│   │                                  ├─ Lifespan (warmup model)
│   │                                  ├─ X-Process-Time middleware
│   │                                  └─ Health check endpoints
│   │
│   ├── core/                       🔧 Modul inti / utilitas
│   │   │── __init__.py
│   │   │── model_loader.py         📥 Singleton: load & cache model dari ml/models/
│   │   │── data_loader.py          📥 Parsing & validasi file CSV
│   │   └── predict.py              🔮 Fungsi prediksi (wrapper ML)
│   │
│   ├── model/                      📐 Schema / definisi data
│   │   │── __init__.py
│   │   └── ml_model.py             📐 Compatibility layer (ModelStore → ModelLoader)
│   │
│   ├── routes/                     🛣️ Definisi endpoint API
│   │   │── __init__.py
│   │   └── api.py                  🛣️ Router: POST /api/v1/predict
│   │
│   └── services/                   💼 Logika bisnis
│       │── __init__.py
│       └── prediction_service.py   💼 Orkestrasi: parse CSV → validasi
│                                      → predict → format response
│
│
│── ─────────────────────────────────────────────────────────
│── 🎨 FRONTEND (React + Vite)
│── ─────────────────────────────────────────────────────────
│
└── frontend/
    │── index.html                  🌐 HTML entry point
    │── vite.config.js              ⚡ Konfigurasi Vite (dev server, build)
    │── package.json                📦 Dependensi npm (React, Axios, dll)
    │── package-lock.json           🔒 Lock file dependensi
    │── eslint.config.js            🔍 Konfigurasi ESLint
    │── .gitignore                  🚫 File yang diabaikan Git
    │
    ├── public/                     📁 Aset statis (favicon, dll)
    │
    └── src/                        📁 Source code React
        │── main.jsx                🚀 Entry point React (ReactDOM.render)
        │── App.jsx                 🏠 Root component & layout utama
        │── App.css                 🎨 Styling khusus App component
        │── AppContext.jsx          🌐 Global state (Context API)
        │                              ├─ Theme (dark/light)
        │                              ├─ Language (id/en)
        │                              └─ Prediction data
        │── i18n.js                 🌍 Kamus multi-bahasa (ID 🇮🇩 / EN 🇬🇧)
        │── index.css               🎨 Global CSS & design tokens
        │                              ├─ CSS variables (warna, font)
        │                              ├─ Dark/light mode
        │                              └─ Animasi & utilitas
        │
        ├── assets/                 🖼️ Gambar, ikon, media
        │
        └── components/             🧩 Komponen UI React
            │── Navbar.jsx          🧭 Navigasi atas
            │                          ├─ Logo & judul
            │                          ├─ Toggle tema 🌙/☀️
            │                          └─ Toggle bahasa ID/EN
            │
            │── Dashboard.jsx       📊 Halaman utama dashboard
            │                          ├─ Kartu statistik ringkasan
            │                          ├─ Total transaksi
            │                          ├─ Jumlah anomali
            │                          └─ Jumlah normal
            │
            │── UploadComponent.jsx 📤 Upload file CSV
            │                          ├─ Drag & drop zone
            │                          ├─ File validation
            │                          ├─ Progress indicator
            │                          └─ axios.post → backend
            │
            │── ChartComponent.jsx  📈 Grafik visualisasi
            │                          ├─ Bar chart distribusi
            │                          ├─ Pie chart proporsi
            │                          └─ Recharts library
            │
            └── TableComponent.jsx  📋 Tabel hasil deteksi
                                       ├─ Daftar semua transaksi
                                       ├─ Highlight baris anomali (merah)
                                       ├─ Sorting & filtering
                                       └─ Anomaly score display
```

---

## 🔄 Alur Koneksi Antar Layer

```
 ┌──────────────────────────────┐
 │        🎨 FRONTEND           │
 │     (React + Vite)           │
 │                              │
 │  User upload CSV             │
 │  └─► UploadComponent.jsx     │
 │       └─► axios.post()  ─────┼──── HTTP POST /api/v1/predict
 │                              │     (multipart/form-data)
 │  Hasil ditampilkan:          │
 │  ├─► Dashboard.jsx           │
 │  ├─► ChartComponent.jsx      │◄─── JSON Response
 │  └─► TableComponent.jsx      │
 └──────────────────────────────┘
              │ ▲
              ▼ │
 ┌──────────────────────────────┐
 │        ⚙️ BACKEND            │
 │       (FastAPI)              │
 │                              │
 │  routes/api.py               │
 │  └─► services/               │
 │       prediction_service.py  │
 │       ├─ Parse CSV (pandas)  │
 │       ├─ Validasi kolom      │
 │       └─► core/              │
 │            model_loader.py   │
 │            (→ ml/models/*.pkl)│
 └──────────────────────────────┘
              │ ▲
              ▼ │
 ┌──────────────────────────────┐
 │     🤖 MACHINE LEARNING      │
 │         (ml/)                │
 │                              │
 │  ml/anomaly_detector.py      │
 │  ├─ Feature Engineering      │
 │  ├─ Pipeline Preprocessing   │
 │  ├─ Isolation Forest         │
 │  └─ Output: anomaly + score  │
 │                              │
 │  ml/models/banking_model.pkl │
 │  ml/data/*.csv               │
 └──────────────────────────────┘
```

---

## 📌 Cara Menjalankan

| Perintah | Dari folder | Fungsi |
|----------|-------------|--------|
| `python -m ml.train` | `banking_anomaly_ml/` | Latih ulang model |
| `python -m ml.predict` | `banking_anomaly_ml/` | Prediksi dari CLI |
| `python -m backend.main` | `banking_anomaly_ml/` | Jalankan backend API |
| `npm run dev` | `banking_anomaly_ml/frontend/` | Jalankan frontend dev server |

| Port | Service |
|------|---------|
| `http://localhost:8000` | Backend API |
| `http://localhost:8000/docs` | Swagger UI |
| `http://localhost:5173` | Frontend React |

---

*File diperbarui: 2026-04-26*
