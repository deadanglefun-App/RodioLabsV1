import asyncio
import logging
import time
from typing import Dict, Any, List
from src.blockchain.web3_client import Web3Client

class StakingManager:
    """Gestionnaire de staking pour la sécurité du réseau"""
    
    def __init__(self, web3_client: Web3Client, staking_config: Dict[str, Any]):
        self.web3 = web3_client
        self.min_stake = int(staking_config.get('min_stake', '1000000000000000000000'))  # 1000 tokens
        self.staking_contract = staking_config.get('staking_contract')
        
        # Métriques de sécurité
        self.slash_events = []
        self.reputation_scores = {}
        self.stake_history = []
        
        logging.info(f"🛡️ StakingManager initialisé - Stake minimum: {self.min_stake / 1e18} tokens")
    
    async def check_stake(self) -> bool:
        """Vérifie si le nœud a assez de stake"""
        try:
            account_address = self.web3.get_account_address()
            current_stake = await self.get_node_stake(account_address)
            
            is_sufficient = current_stake >= self.min_stake
            
            if is_sufficient:
                logging.info(f"✅ Stake suffisant: {current_stake / 1e18:.2f} tokens")
            else:
                logging.error(f"❌ Stake insuffisant: {current_stake / 1e18:.2f} < {self.min_stake / 1e18} tokens")
            
            return is_sufficient
            
        except Exception as e:
            logging.error(f"❌ Erreur vérification stake: {e}")
            return False
    
    async def get_node_stake(self, node_address: str) -> int:
        """Récupère le stake d'un nœud"""
        try:
            # Simulation d'appel au contrat de staking
            await asyncio.sleep(0.1)
            
            # Simulation de stake basé sur l'adresse
            import hashlib
            address_hash = int(hashlib.sha256(node_address.encode()).hexdigest()[:8], 16)
            simulated_stake = (address_hash % 5000 + 1000) * int(1e18)  # Entre 1000 et 6000 tokens
            
            return simulated_stake
            
        except Exception as e:
            logging.error(f"❌ Erreur récupération stake pour {node_address}: {e}")
            return 0
    
    async def slash_node(self, malicious_node: str, amount: int, reason: str) -> bool:
        """Pénalise un nœud malhonnête"""
        try:
            # Vérification du consensus pour le slashing
            consensus_reached = await self.is_consensus_slashing(malicious_node, reason)
            
            if not consensus_reached:
                logging.warning(f"⚠️ Pas de consensus pour pénaliser {malicious_node}")
                return False
            
            # Vérification que le nœud a assez de stake à perdre
            current_stake = await self.get_node_stake(malicious_node)
            if current_stake < amount:
                amount = current_stake  # Slash tout le stake disponible
            
            # Exécution du slashing
            transaction_data = {
                'function': 'slashStake',
                'contract': 'StakingContract',
                'parameters': {
                    'nodeAddress': malicious_node,
                    'amount': amount,
                    'reason': reason
                }
            }
            
            tx_hash = await self.web3.send_transaction(transaction_data)
            
            # Enregistrement de l'événement
            slash_event = {
                'node_address': malicious_node,
                'amount': amount,
                'reason': reason,
                'timestamp': int(time.time()),
                'tx_hash': tx_hash
            }
            self.slash_events.append(slash_event)
            
            # Mise à jour du score de réputation
            self.update_reputation_score(malicious_node, -0.2)
            
            logging.warning(f"⚡ Nœud {malicious_node} pénalisé: -{amount / 1e18:.2f} tokens ({reason})")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erreur slashing {malicious_node}: {e}")
            return False
    
    async def is_consensus_slashing(self, target_node: str, reason: str) -> bool:
        """Vérifie si il y a consensus pour pénaliser un nœud"""
        try:
            # Simulation de vote des autres nœuds
            # En réalité, ceci impliquerait une communication avec les autres nœuds
            
            # Critères pour le consensus automatique
            auto_slash_reasons = [
                'data_manipulation',
                'double_spending',
                'malicious_consensus',
                'stake_below_minimum'
            ]
            
            if reason in auto_slash_reasons:
                logging.info(f"✅ Consensus automatique pour slashing: {reason}")
                return True
            
            # Pour d'autres raisons, simulation de vote
            import random
            votes_for = random.randint(3, 7)  # Votes pour le slashing
            votes_against = random.randint(0, 2)  # Votes contre
            
            consensus_threshold = 0.75  # 75% des votes requis
            consensus_ratio = votes_for / (votes_for + votes_against)
            
            consensus_reached = consensus_ratio >= consensus_threshold
            
            logging.info(f"🗳️ Vote slashing {target_node}: {votes_for}/{votes_for + votes_against} ({consensus_ratio:.1%})")
            
            return consensus_reached
            
        except Exception as e:
            logging.error(f"❌ Erreur consensus slashing: {e}")
            return False
    
    def update_reputation_score(self, node_address: str, delta: float):
        """Met à jour le score de réputation d'un nœud"""
        current_score = self.reputation_scores.get(node_address, 1.0)
        new_score = max(0.0, min(1.0, current_score + delta))
        
        self.reputation_scores[node_address] = new_score
        
        logging.info(f"📊 Réputation {node_address}: {new_score:.2f} ({delta:+.2f})")
    
    def get_reputation_score(self, node_address: str) -> float:
        """Récupère le score de réputation d'un nœud"""
        return self.reputation_scores.get(node_address, 1.0)
    
    async def increase_stake(self, amount: int) -> str:
        """Augmente le stake du nœud"""
        try:
            transaction_data = {
                'function': 'increaseStake',
                'contract': 'StakingContract',
                'parameters': {
                    'amount': amount
                }
            }
            
            tx_hash = await self.web3.send_transaction(transaction_data)
            
            # Enregistrement dans l'historique
            stake_event = {
                'action': 'increase',
                'amount': amount,
                'timestamp': int(time.time()),
                'tx_hash': tx_hash
            }
            self.stake_history.append(stake_event)
            
            logging.info(f"💰 Stake augmenté: +{amount / 1e18:.2f} tokens")
            return tx_hash
            
        except Exception as e:
            logging.error(f"❌ Erreur augmentation stake: {e}")
            raise
    
    async def withdraw_stake(self, amount: int) -> str:
        """Retire du stake (avec période de cooldown)"""
        try:
            # Vérification que le retrait ne descend pas sous le minimum
            current_stake = await self.get_node_stake(self.web3.get_account_address())
            
            if current_stake - amount < self.min_stake:
                raise ValueError(f"Retrait refusé: stake résiduel insuffisant")
            
            transaction_data = {
                'function': 'withdrawStake',
                'contract': 'StakingContract',
                'parameters': {
                    'amount': amount
                }
            }
            
            tx_hash = await self.web3.send_transaction(transaction_data)
            
            # Enregistrement dans l'historique
            stake_event = {
                'action': 'withdraw',
                'amount': amount,
                'timestamp': int(time.time()),
                'tx_hash': tx_hash
            }
            self.stake_history.append(stake_event)
            
            logging.info(f"💸 Stake retiré: -{amount / 1e18:.2f} tokens")
            return tx_hash
            
        except Exception as e:
            logging.error(f"❌ Erreur retrait stake: {e}")
            raise
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques de sécurité"""
        return {
            'min_stake_required': self.min_stake / 1e18,
            'slash_events_count': len(self.slash_events),
            'nodes_with_reputation': len(self.reputation_scores),
            'average_reputation': (
                sum(self.reputation_scores.values()) / len(self.reputation_scores)
                if self.reputation_scores else 1.0
            ),
            'stake_history_count': len(self.stake_history),
            'recent_slash_events': self.slash_events[-5:] if self.slash_events else []
        }
    
    async def monitor_network_security(self):
        """Surveille la sécurité du réseau en continu"""
        logging.info("🔍 Démarrage du monitoring sécurité...")
        
        while True:
            try:
                # Vérification périodique du stake
                stake_ok = await self.check_stake()
                
                if not stake_ok:
                    logging.error("🚨 ALERTE: Stake insuffisant détecté!")
                
                # Nettoyage des anciens événements (garde 1000 derniers)
                if len(self.slash_events) > 1000:
                    self.slash_events = self.slash_events[-1000:]
                
                if len(self.stake_history) > 1000:
                    self.stake_history = self.stake_history[-1000:]
                
                await asyncio.sleep(300)  # Check toutes les 5 minutes
                
            except Exception as e:
                logging.error(f"❌ Erreur monitoring sécurité: {e}")
                await asyncio.sleep(60)