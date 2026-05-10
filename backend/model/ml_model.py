"""
ml_model.py (Compatibility Layer)
==================================
Dipertahankan agar tidak ada breaking change pada kode lama yang
meng-import ModelStore. Delegasi penuh ke backend.core.model_loader.

Jika Anda membangun kode baru, import langsung dari:
    from backend.core.model_loader import ModelLoader
"""

import os
import sys
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backend.core.model_loader import ModelLoader
from ml.anomaly_detector import BankingAnomalyDetector

logger = logging.getLogger(__name__)


class ModelStore:
    """
    Compatibility shim — mendelegasikan ke ModelLoader.

    Kode lama yang memanggil ModelStore.get_model() tetap bekerja
    tanpa perubahan apapun.
    """

    @classmethod
    def get_model(cls) -> BankingAnomalyDetector:
        """Delegasi ke ModelLoader.get() yang thread-safe."""
        return ModelLoader.get()
