"""
Routes pour la gestion de l'oracle et du consensus
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

from src.api.main import get_oracle_manager
from src.core.oracle_manager import OracleManager

router = APIRouter(tags=["Oracle"])

class ConsensusStatus(BaseModel):
    active_nodes: int
    consensus_threshold: float
    success_rate: float
    last_consensus: int
    pending_submissions: int

class NodeInfo(BaseModel):
    node_id: str
    status: str
    reputation: float
    stake_amount: int
    last_seen: int

@router.get("/oracle/consensus/status", response_model=ConsensusStatus)
async def get_consensus_status(
    oracle_manager: OracleManager = Depends(get_oracle_manager)
):
    """Récupère le statut du consensus"""
    try:
        status = await oracle_manager.get_consensus_status()
        
        return ConsensusStatus(
            active_nodes=status.get("active_nodes", 0),
            consensus_threshold=status.get("threshold", 0.8),
            success_rate=status.get("success_rate", 0.0),
            last_consensus=status.get("last_consensus", 0),
            pending_submissions=status.get("pending", 0)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération du statut: {str(e)}"
        )

@router.get("/oracle/nodes", response_model=List[NodeInfo])
async def get_network_nodes(
    oracle_manager: OracleManager = Depends(get_oracle_manager)
):
    """Liste tous les nœuds du réseau"""
    try:
        nodes = await oracle_manager.get_network_nodes()
        
        return [
            NodeInfo(
                node_id=node.get("id", "unknown"),
                status=node.get("status", "unknown"),
                reputation=node.get("reputation", 0.0),
                stake_amount=node.get("stake", 0),
                last_seen=node.get("last_seen", 0)
            )
            for node in nodes
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des nœuds: {str(e)}"
        )

@router.get("/oracle/metrics")
async def get_oracle_metrics(
    oracle_manager: OracleManager = Depends(get_oracle_manager)
):
    """Récupère les métriques détaillées de l'oracle"""
    try:
        metrics = await oracle_manager.get_detailed_metrics()
        
        return {
            "timestamp": int(datetime.now().timestamp()),
            "metrics": metrics
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des métriques: {str(e)}"
        )

@router.post("/oracle/consensus/trigger")
async def trigger_consensus(
    sensor_id: str,
    oracle_manager: OracleManager = Depends(get_oracle_manager)
):
    """Déclenche manuellement un consensus pour un capteur"""
    try:
        result = await oracle_manager.trigger_manual_consensus(sensor_id)
        
        return {
            "success": result.get("success", False),
            "message": result.get("message", "Consensus déclenché"),
            "consensus_value": result.get("value"),
            "participating_nodes": result.get("nodes", 0),
            "timestamp": int(datetime.now().timestamp())
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du déclenchement du consensus: {str(e)}"
        )