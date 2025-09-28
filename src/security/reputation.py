import time
import logging
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class ReputationEvent:
    """Événement affectant la réputation d'un nœud"""
    node_id: str
    event_type: str  # 'consensus_success', 'consensus_failure', 'data_quality', etc.
    impact: float    # Impact sur la réputation (-1.0 à +1.0)
    timestamp: int
    details: Dict[str, Any]

class ReputationSystem:
    """Système de réputation pour les nœuds du réseau"""
    
    def __init__(self):
        self.node_reputations = {}  # node_id -> score (0.0 à 1.0)
        self.reputation_events = []
        self.reputation_weights = {
            'consensus_success': 0.05,
            'consensus_failure': -0.1,
            'data_quality_high': 0.03,
            'data_quality_low': -0.05,
            'uptime_good': 0.02,
            'uptime_poor': -0.08,
            'malicious_behavior': -0.5,
            'stake_increase': 0.1,
            'stake_slash': -0.3
        }
        
        # Paramètres du système
        self.min_reputation = 0.0
        self.max_reputation = 1.0
        self.default_reputation = 0.8  # Nouveaux nœuds commencent à 80%
        self.decay_rate = 0.001  # Décroissance naturelle par jour
        
        logging.info("📊 Système de réputation initialisé")
    
    def get_reputation(self, node_id: str) -> float:
        """Récupère la réputation actuelle d'un nœud"""
        if node_id not in self.node_reputations:
            self.node_reputations[node_id] = self.default_reputation
            logging.info(f"🆕 Nouveau nœud {node_id} - Réputation initiale: {self.default_reputation}")
        
        return self.node_reputations[node_id]
    
    def update_reputation(self, node_id: str, event_type: str, details: Dict[str, Any] = None):
        """Met à jour la réputation d'un nœud suite à un événement"""
        if event_type not in self.reputation_weights:
            logging.warning(f"⚠️ Type d'événement inconnu: {event_type}")
            return
        
        current_reputation = self.get_reputation(node_id)
        impact = self.reputation_weights[event_type]
        
        # Calcul de la nouvelle réputation
        new_reputation = current_reputation + impact
        new_reputation = max(self.min_reputation, min(self.max_reputation, new_reputation))
        
        # Enregistrement de l'événement
        event = ReputationEvent(
            node_id=node_id,
            event_type=event_type,
            impact=impact,
            timestamp=int(time.time()),
            details=details or {}
        )
        self.reputation_events.append(event)
        
        # Mise à jour de la réputation
        old_reputation = self.node_reputations[node_id]
        self.node_reputations[node_id] = new_reputation
        
        logging.info(f"📈 Réputation {node_id}: {old_reputation:.3f} → {new_reputation:.3f} ({event_type})")
    
    def apply_time_decay(self):
        """Applique une décroissance naturelle des réputations"""
        current_time = int(time.time())
        
        for node_id in self.node_reputations:
            current_rep = self.node_reputations[node_id]
            
            # Décroissance vers la moyenne (0.5)
            target = 0.5
            decay_amount = self.decay_rate * (current_rep - target)
            new_reputation = current_rep - decay_amount
            
            self.node_reputations[node_id] = max(
                self.min_reputation, 
                min(self.max_reputation, new_reputation)
            )
    
    def get_trusted_nodes(self, min_reputation: float = 0.7) -> List[str]:
        """Retourne la liste des nœuds de confiance"""
        trusted = [
            node_id for node_id, reputation in self.node_reputations.items()
            if reputation >= min_reputation
        ]
        
        logging.info(f"🤝 {len(trusted)} nœuds de confiance (seuil: {min_reputation})")
        return trusted
    
    def get_suspicious_nodes(self, max_reputation: float = 0.3) -> List[str]:
        """Retourne la liste des nœuds suspects"""
        suspicious = [
            node_id for node_id, reputation in self.node_reputations.items()
            if reputation <= max_reputation
        ]
        
        if suspicious:
            logging.warning(f"🚨 {len(suspicious)} nœuds suspects détectés")
        
        return suspicious
    
    def calculate_consensus_weight(self, node_id: str) -> float:
        """Calcule le poids d'un nœud dans le consensus basé sur sa réputation"""
        reputation = self.get_reputation(node_id)
        
        # Fonction de pondération non-linéaire
        # Les nœuds avec une bonne réputation ont plus de poids
        if reputation >= 0.8:
            weight = 1.0
        elif reputation >= 0.6:
            weight = 0.8
        elif reputation >= 0.4:
            weight = 0.5
        elif reputation >= 0.2:
            weight = 0.2
        else:
            weight = 0.1  # Poids minimal pour éviter l'exclusion totale
        
        return weight
    
    def get_reputation_history(self, node_id: str, days: int = 7) -> List[ReputationEvent]:
        """Récupère l'historique de réputation d'un nœud"""
        cutoff_time = int(time.time()) - (days * 24 * 3600)
        
        history = [
            event for event in self.reputation_events
            if event.node_id == node_id and event.timestamp >= cutoff_time
        ]
        
        return sorted(history, key=lambda x: x.timestamp, reverse=True)
    
    def generate_reputation_report(self) -> Dict[str, Any]:
        """Génère un rapport complet sur les réputations"""
        if not self.node_reputations:
            return {"message": "Aucune donnée de réputation disponible"}
        
        reputations = list(self.node_reputations.values())
        
        report = {
            'total_nodes': len(self.node_reputations),
            'average_reputation': sum(reputations) / len(reputations),
            'min_reputation': min(reputations),
            'max_reputation': max(reputations),
            'trusted_nodes_count': len(self.get_trusted_nodes()),
            'suspicious_nodes_count': len(self.get_suspicious_nodes()),
            'total_events': len(self.reputation_events),
            'reputation_distribution': {
                'excellent': len([r for r in reputations if r >= 0.9]),
                'good': len([r for r in reputations if 0.7 <= r < 0.9]),
                'average': len([r for r in reputations if 0.5 <= r < 0.7]),
                'poor': len([r for r in reputations if 0.3 <= r < 0.5]),
                'very_poor': len([r for r in reputations if r < 0.3])
            },
            'top_nodes': sorted(
                [(node_id, rep) for node_id, rep in self.node_reputations.items()],
                key=lambda x: x[1],
                reverse=True
            )[:5],
            'bottom_nodes': sorted(
                [(node_id, rep) for node_id, rep in self.node_reputations.items()],
                key=lambda x: x[1]
            )[:5]
        }
        
        return report
    
    def cleanup_old_events(self, days_to_keep: int = 30):
        """Nettoie les anciens événements de réputation"""
        cutoff_time = int(time.time()) - (days_to_keep * 24 * 3600)
        
        old_count = len(self.reputation_events)
        self.reputation_events = [
            event for event in self.reputation_events
            if event.timestamp >= cutoff_time
        ]
        
        cleaned_count = old_count - len(self.reputation_events)
        if cleaned_count > 0:
            logging.info(f"🧹 {cleaned_count} anciens événements de réputation supprimés")
    
    def export_reputation_data(self) -> Dict[str, Any]:
        """Exporte toutes les données de réputation"""
        return {
            'node_reputations': self.node_reputations.copy(),
            'reputation_events': [
                {
                    'node_id': event.node_id,
                    'event_type': event.event_type,
                    'impact': event.impact,
                    'timestamp': event.timestamp,
                    'details': event.details
                }
                for event in self.reputation_events
            ],
            'system_config': {
                'reputation_weights': self.reputation_weights,
                'min_reputation': self.min_reputation,
                'max_reputation': self.max_reputation,
                'default_reputation': self.default_reputation,
                'decay_rate': self.decay_rate
            }
        }