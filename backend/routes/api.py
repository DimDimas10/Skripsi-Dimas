from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.prediction_service import process_and_predict

router = APIRouter()

@router.post("/predict", summary="Upload CSV file and predict anomalies")
async def predict_anomalies(file: UploadFile = File(...)):
    """
    Endpoint untuk menerima file CSV berisikan transaksi perbankan.
    Mengembalikan data transaksi yang telah ditandai jika ada anomali atau tidak.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Hanya file berekstensi .csv yang diizinkan.")
        
    try:
        # Membaca isi file secara asynchronous
        contents = await file.read()
        
        # Lempar ke lapisan Service
        result_json = process_and_predict(contents)
        return result_json
        
    except Exception as e:
        # Kembalikan HTTP 500 bila terjadi error pada Python / Pandas
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan saat pemrosesan: {str(e)}")
