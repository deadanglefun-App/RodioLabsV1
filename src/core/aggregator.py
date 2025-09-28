import statistics
import time
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class SensorReading:
    """Représente une lecture de capteur avec métadonnées"""
    value: float
    timestamp: int
    node_id: str
    signature: str  # Preuve cryptographique

class ConsensusError(Exception):
    """Exception levée quand le consensus n'est pas atteint"""
    pass

class DataAggregator:
    """Agrégateur de données avec consensus Chainlink-style"""
    
    def __init__(self, consensus_config: Dict):
        self.consensus_threshold = consensus_config.get('consensus_threshold', 0.8)
        self.outlier_tolerance = consensus_config.get('outlier_tolerance', 0.05)
        self.min_nodes = consensus_config.get('min_nodes', 3)
    
    async def aggregate_readings(self, readings: List[SensorReading]) -> Dict[str, Any]:
        """Agrège les données de multiples nœuds avec consensus"""
        if len(readings) < self.min_nodes:
            raise ValueError(f"Minimum {self.min_nodes} nœuds requis pour l'agrégation")
        
        # 1. Validation des signatures (simplifié)
        validated_readings = self.validate_signatures(readings)
        
        # 2. Filtrage des outliers statistiques
        values = [r.value for r in validated_readings]
        filtered_values = self.remove_outliers(values)
        
        if len(filtered_values) < self.min_nodes:
            raise ConsensusError("Trop d'outliers détectés - consensus impossible")
        
        # 3. Vérification du consensus
        if not self.check_consensus(filtered_values):
            raise ConsensusError("Pas de consensus atteint entre les nœuds")
        
        # 4. Calcul de la valeur finale (médiane pour robustesse)
        final_value = statistics.median(filtered_values)
        confidence = self.calculate_confidence(filtered_values)
        
        return {
            "value": final_value,
            "timestamp": max(r.timestamp for r in validated_readings),
            "confidence": confidence,
            "nodes_participated": len(validated_readings),
            "outliers_removed": len(values) - len(filtered_values),
            "consensus_method": "median_with_iqr_filtering"
        }
    
    def validate_signatures(self, readings: List[SensorReading]) -> List[SensorReading]:
        """Valide les signatures cryptographiques des lectures"""
        validated = []
        
        for reading in readings:
            # Validation simplifiée - en production utiliser ECDSA
            if len(reading.signature) == 64:  # SHA256 hex length
                validated.append(reading)
            else:
                print(f"⚠️ Signature invalide pour nœud {reading.node_id}")
        
        return validated
    
    def remove_outliers(self, values: List[float]) -> List[float]:
        """Filtre les outliers avec la méthode IQR (Interquartile Range)"""
        if len(values) < 4:
            return values  # Pas assez de données pour filtrer
        
        try:
            # Calcul des quartiles
            sorted_values = sorted(values)
            n = len(sorted_values)
            
            q1_idx = n // 4
            q3_idx = 3 * n // 4
            
            q1 = sorted_values[q1_idx]
            q3 = sorted_values[q3_idx]
            
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            # Filtrage des outliers
            filtered = [v for v in values if lower_bound <= v <= upper_bound]
            
            if len(filtered) < len(values):
                print(f"🔍 {len(values) - len(filtered)} outliers supprimés (bounds: {lower_bound:.2f} - {upper_bound:.2f})")
            
            return filtered if filtered else values  # Fallback si tous sont outliers
            
        except Exception as e:
            print(f"⚠️ Erreur filtrage outliers: {e}")
            return values  # Fallback en cas d'erreur
    
    def check_consensus(self, values: List[float]) -> bool:
        """Vérifie si les valeurs sont dans la tolérance de consensus"""
        if not values:
            return False
        
        if len(values) == 1:
            return True
        
        try:
            median = statistics.median(values)
            
            # Tolérance basée sur la valeur médiane
            if median == 0:
                threshold = 0.1  # Tolérance absolue pour valeurs proches de zéro
            else:
                threshold = abs(median * self.outlier_tolerance)
            
            # Compte les valeurs dans la tolérance
            within_threshold = [
                v for v in values 
                if abs(v - median) <= threshold
            ]
            
            consensus_ratio = len(within_threshold) / len(values)
            
            print(f"📊 Consensus check: {len(within_threshold)}/{len(values)} nœuds d'accord ({consensus_ratio:.1%})")
            
            return consensus_ratio >= self.consensus_threshold
            
        except Exception as e:
            print(f"⚠️ Erreur vérification consensus: {e}")
            return False
    
    def calculate_confidence(self, values: List[float]) -> float:
        """Calcule le niveau de confiance basé sur la variance"""
        if len(values) <= 1:
            return 1.0
        
        try:
            # Calcul de la variance normalisée
            mean_val = statistics.mean(values)
            variance = statistics.variance(values)
            
            if mean_val == 0:
                cv = 0  # Coefficient de variation
            else:
                cv = (variance ** 0.5) / abs(mean_val)  # Coefficient de variation
            
            # Conversion en score de confiance (0-1)
            # Plus la variance est faible, plus la confiance est élevée
            confidence = max(0.0, min(1.0, 1.0 - cv))
            
            return confidence
            
        except Exception as e:
            print(f"⚠️ Erreur calcul confiance: {e}")
            return 0.5  # Confiance moyenne par défaut
    
    def detect_malicious_nodes(self, readings: List[SensorReading]) -> List[str]:
        """Détecte les nœuds potentiellement malveillants"""
        if len(readings) < 3:
            return []
        
        values = [r.value for r in readings]
        median = statistics.median(values)
        
        # Seuil pour détecter les valeurs suspectes (plus strict que outliers)
        threshold = abs(median * 0.1)  # 10% de tolérance
        
        malicious_nodes = []
        for reading in readings:
            if abs(reading.value - median) > threshold:
                malicious_nodes.append(reading.node_id)
        
        if malicious_nodes:
            print(f"🚨 Nœuds suspects détectés: {malicious_nodes}")
        
        return malicious_nodes