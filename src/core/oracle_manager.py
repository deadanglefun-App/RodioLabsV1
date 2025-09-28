"""
Gestionnaire principal de l'Oracle RODIO
Orchestration des composants et logique métier
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.config.settings import Settings
from src.blockchain.web3_client import Web3Client
from src.core.aggregator import DataAggregator
from src.security.staking import StakingManager

logger = logging.getLogger(__name__)

class OracleManager:
    """Gestionnaire principal de l'Oracle RODIO"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.web3_client = None
        self.aggregator = None
        self.staking_manager = None
        self.is_initialized = False
        
        # Métriques
        self.metrics = {
            "total_submissions": 0,
            "successful_consensus": 0,
            "failed_consensus": 0,
            "active_sensors": set(),
            "start_time": datetime.now().timestamp()
        }
    
    async def initialize(self):
        """Initialise tous les composants de l'oracle"""
        try:
            logger.info("🔄 Initialisation de l'Oracle Manager...")
            
            # Initialisation du client Web3
            self.web3_client = Web3Client(self.settings)
            await self.web3_client.connect()
            
            # Initialisation de l'agrégateur
            self.aggregator = DataAggregator()
            
            # Initialisation du gestionnaire de staking
            self.staking_manager = StakingManager(self.web3_client, self.settings)
            
            # Vérification du stake
            if not await self.staking_manager.check_stake():
                raise Exception("Stake insuffisant pour opérer")
            
            self.is_initialized = True
            logger.info("✅ Oracle Manager initialisé avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation: {e}")
            raise
    
    async def submit_sensor_data(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Soumet des données de capteur pour consensus"""
        if not self.is_initialized:
            raise Exception("Oracle Manager non initialisé")
        
        try:
            sensor_id = sensor_data["sensor_id"]
            self.metrics["active_sensors"].add(sensor_id)
            self.metrics["total_submissions"] += 1
            
            logger.info(f"📊 Soumission données capteur: {sensor_id}")
            
            # Simulation du processus de consensus
            # En réalité, ceci impliquerait la communication avec d'autres nœuds
            consensus_result = await self._simulate_consensus(sensor_data)
            
            if consensus_result["success"]:
                # Soumission à la blockchain
                tx_hash = await self.web3_client.submit_to_blockchain(
                    sensor_id,
                    consensus_result["value"],
                    sensor_data["timestamp"]
                )
                
                self.metrics["successful_consensus"] += 1
                
                return {
                    "success": True,
                    "tx_hash": tx_hash,
                    "consensus_value": consensus_result["value"],
                    "confidence": consensus_result["confidence"]
                }
            else:
                self.metrics["failed_consensus"] += 1
                raise Exception("Consensus non atteint")
                
        except Exception as e:
            logger.error(f"❌ Erreur soumission capteur {sensor_data.get('sensor_id')}: {e}")
            raise
    
    async def _simulate_consensus(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simule le processus de consensus (à remplacer par la vraie logique)"""
        # Simulation simple - en réalité, ceci impliquerait:
        # 1. Communication avec les nœuds pairs
        # 2. Collecte des lectures
        # 3. Agrégation avec l'algorithme de consensus
        
        await asyncio.sleep(0.1)  # Simulation latence réseau
        
        # Simulation d'un consensus réussi dans 95% des cas
        import random
        success = random.random() > 0.05
        
        if success:
            # Petite variation autour de la valeur originale
            original_value = sensor_data["value"]
            consensus_value = original_value + random.uniform(-0.1, 0.1)
            
            return {
                "success": True,
                "value": round(consensus_value, 2),
                "confidence": random.uniform(0.85, 0.99),
                "participating_nodes": random.randint(3, 7)
            }
        else:
            return {
                "success": False,
                "reason": "Pas assez de nœuds d'accord"
            }
    
    async def get_latest_sensor_data(self, sensor_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les dernières données d'un capteur"""
        if not self.is_initialized:
            raise Exception("Oracle Manager non initialisé")
        
        # Simulation - en réalité, récupération depuis la blockchain ou cache
        return {
            "sensor_id": sensor_id,
            "value": 23.5,
            "timestamp": int(datetime.now().timestamp()) - 300,
            "block_number": 18500000,
            "confidence": 0.95
        }
    
    async def get_sensor_history(self, sensor_id: str, limit: int) -> List[Dict[str, Any]]:
        """Récupère l'historique d'un capteur"""
        if not self.is_initialized:
            raise Exception("Oracle Manager non initialisé")
        
        # Simulation d'historique
        history = []
        base_time = int(datetime.now().timestamp())
        
        for i in range(min(limit, 10)):  # Simulation de 10 entrées max
            history.append({
                "sensor_id": sensor_id,
                "value": 23.0 + (i * 0.1),
                "timestamp": base_time - (i * 300),  # Toutes les 5 minutes
                "block_number": 18500000 - i,
                "confidence": 0.95
            })
        
        return history
    
    async def get_active_sensors(self) -> List[Dict[str, Any]]:
        """Liste tous les capteurs actifs"""
        sensors = []
        for sensor_id in self.metrics["active_sensors"]:
            sensors.append({
                "sensor_id": sensor_id,
                "status": "active",
                "last_reading": int(datetime.now().timestamp()) - 60,
                "total_readings": 100  # Simulation
            })
        
        return sensors
    
    async def get_consensus_status(self) -> Dict[str, Any]:
        """Récupère le statut du consensus"""
        total_attempts = self.metrics["successful_consensus"] + self.metrics["failed_consensus"]
        success_rate = (
            self.metrics["successful_consensus"] / max(1, total_attempts)
        )
        
        return {
            "active_nodes": 3,  # Simulation
            "threshold": 0.8,
            "success_rate": success_rate,
            "last_consensus": int(datetime.now().timestamp()) - 30,
            "pending": 0
        }
    
    async def get_network_nodes(self) -> List[Dict[str, Any]]:
        """Liste tous les nœuds du réseau"""
        # Simulation de nœuds
        return [
            {
                "id": "RODIO_NODE_001",
                "status": "active",
                "reputation": 0.95,
                "stake": 1000,
                "last_seen": int(datetime.now().timestamp()) - 30
            },
            {
                "id": "RODIO_NODE_002", 
                "status": "active",
                "reputation": 0.88,
                "stake": 1500,
                "last_seen": int(datetime.now().timestamp()) - 45
            }
        ]
    
    async def get_detailed_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques détaillées"""
        uptime = datetime.now().timestamp() - self.metrics["start_time"]
        
        return {
            "uptime_seconds": int(uptime),
            "total_submissions": self.metrics["total_submissions"],
            "successful_consensus": self.metrics["successful_consensus"],
            "failed_consensus": self.metrics["failed_consensus"],
            "active_sensors_count": len(self.metrics["active_sensors"]),
            "success_rate": (
                self.metrics["successful_consensus"] / 
                max(1, self.metrics["total_submissions"])
            )
        }
    
    async def trigger_manual_consensus(self, sensor_id: str) -> Dict[str, Any]:
        """Déclenche manuellement un consensus"""
        # Simulation
        return {
            "success": True,
            "message": f"Consensus déclenché pour {sensor_id}",
            "value": 23.5,
            "nodes": 3
        }
    
    async def shutdown(self):
        """Arrêt propre de l'Oracle Manager"""
        logger.info("🛑 Arrêt de l'Oracle Manager...")
        
        if self.web3_client:
            await self.web3_client.disconnect()
        
        self.is_initialized = False
        logger.info("✅ Oracle Manager arrêté")