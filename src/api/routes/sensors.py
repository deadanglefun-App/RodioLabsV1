"""
Routes pour la gestion des capteurs
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.api.main import get_oracle_manager
from src.core.oracle_manager import OracleManager

router = APIRouter(tags=["Sensors"])

class SensorReading(BaseModel):
    sensor_id: str
    sensor_type: str
    value: float
    unit: str
    timestamp: int
    quality_score: float
    metadata: Optional[Dict[str, Any]] = None

class SensorSubmissionResponse(BaseModel):
    success: bool
    transaction_hash: Optional[str] = None
    message: str
    timestamp: int

@router.post("/sensors/submit", response_model=SensorSubmissionResponse)
async def submit_sensor_data(
    reading: SensorReading,
    oracle_manager: OracleManager = Depends(get_oracle_manager)
):
    """Soumet des données de capteur pour consensus"""
    try:
        # Validation des données
        if reading.quality_score < 0.5:
            raise HTTPException(
                status_code=400,
                detail="Qualité des données insuffisante"
            )
        
        # Soumission via l'Oracle Manager
        result = await oracle_manager.submit_sensor_data(reading.dict())
        
        return SensorSubmissionResponse(
            success=True,
            transaction_hash=result.get("tx_hash"),
            message="Données soumises avec succès",
            timestamp=int(datetime.now().timestamp())
        )
        
    except Exception as e:
        return SensorSubmissionResponse(
            success=False,
            message=f"Erreur lors de la soumission: {str(e)}",
            timestamp=int(datetime.now().timestamp())
        )

@router.get("/sensors/latest/{sensor_id}")
async def get_latest_sensor_data(
    sensor_id: str,
    oracle_manager: OracleManager = Depends(get_oracle_manager)
):
    """Récupère les dernières données d'un capteur"""
    try:
        data = await oracle_manager.get_latest_sensor_data(sensor_id)
        
        if not data:
            raise HTTPException(
                status_code=404,
                detail=f"Aucune donnée trouvée pour le capteur {sensor_id}"
            )
        
        return data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération: {str(e)}"
        )

@router.get("/sensors/history/{sensor_id}")
async def get_sensor_history(
    sensor_id: str,
    limit: int = 100,
    oracle_manager: OracleManager = Depends(get_oracle_manager)
):
    """Récupère l'historique d'un capteur"""
    try:
        if limit > 1000:
            raise HTTPException(
                status_code=400,
                detail="Limite maximale: 1000 enregistrements"
            )
        
        history = await oracle_manager.get_sensor_history(sensor_id, limit)
        
        return {
            "sensor_id": sensor_id,
            "count": len(history),
            "data": history
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération: {str(e)}"
        )

@router.get("/sensors/active")
async def get_active_sensors(
    oracle_manager: OracleManager = Depends(get_oracle_manager)
):
    """Liste tous les capteurs actifs"""
    try:
        sensors = await oracle_manager.get_active_sensors()
        
        return {
            "count": len(sensors),
            "sensors": sensors
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération: {str(e)}"
        )