import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional
from src.blockchain.web3_client import Web3Client

class AsyncContractHandler:
    """Gestionnaire de contrats intelligents avec support asynchrone"""
    
    def __init__(self, web3_client: Web3Client):
        self.web3 = web3_client
        self.contracts = self.load_contracts()
        
        # Cache pour optimiser les appels
        self.call_cache = {}
        self.cache_ttl = 60  # 1 minute
        
        logging.info("📋 ContractHandler initialisé")
    
    def load_contracts(self) -> Dict[str, Any]:
        """Charge les ABIs et adresses des contrats"""
        try:
            with open('config/contracts.json', 'r') as f:
                contracts_config = json.load(f)
            
            logging.info(f"✅ {len(contracts_config)} contrats chargés")
            return contracts_config
            
        except FileNotFoundError:
            logging.warning("⚠️ Fichier contracts.json non trouvé, utilisation de contrats par défaut")
            return self.get_default_contracts()
        except Exception as e:
            logging.error(f"❌ Erreur chargement contrats: {e}")
            return {}
    
    def get_default_contracts(self) -> Dict[str, Any]:
        """Retourne des contrats par défaut pour les tests"""
        return {
            "DataOracle": {
                "address": "0x1234567890123456789012345678901234567890",
                "abi": [
                    {
                        "inputs": [
                            {"name": "sensorId", "type": "string"},
                            {"name": "value", "type": "int256"},
                            {"name": "timestamp", "type": "uint256"}
                        ],
                        "name": "submitData",
                        "outputs": [],
                        "stateMutability": "nonpayable",
                        "type": "function"
                    }
                ]
            }
        }
    
    async def submit_data_async(self, sensor_id: str, value: float, timestamp: int) -> str:
        """Soumet les données au contrat de manière asynchrone"""
        try:
            # Préparation des données de transaction
            transaction_data = {
                'function': 'submitData',
                'contract': 'DataOracle',
                'parameters': {
                    'sensorId': sensor_id,
                    'value': int(value * 100),  # Precision fixe (2 décimales)
                    'timestamp': timestamp
                },
                'gas_limit': 200000
            }
            
            # Estimation du gas
            estimated_gas = await self.web3.estimate_gas(transaction_data)
            transaction_data['gas_limit'] = estimated_gas
            
            # Envoi de la transaction
            tx_hash = await self.web3.send_transaction(transaction_data)
            
            # Attente de confirmation en arrière-plan
            asyncio.create_task(self._wait_and_log_confirmation(tx_hash, sensor_id, value))
            
            return tx_hash
            
        except Exception as e:
            logging.error(f"❌ Erreur soumission données {sensor_id}: {e}")
            raise
    
    async def _wait_and_log_confirmation(self, tx_hash: str, sensor_id: str, value: float):
        """Attend la confirmation et log le résultat"""
        try:
            confirmed = await self.web3.wait_for_confirmation(tx_hash)
            
            if confirmed:
                logging.info(f"✅ Données confirmées sur blockchain - {sensor_id}: {value}")
            else:
                logging.error(f"❌ Échec confirmation - {sensor_id}: {value}")
                
        except Exception as e:
            logging.error(f"❌ Erreur confirmation {tx_hash}: {e}")
    
    async def get_latest_data_async(self, sensor_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les dernières données d'un capteur"""
        try:
            # Vérification du cache
            cache_key = f"latest_data_{sensor_id}"
            cached_result = self._get_from_cache(cache_key)
            
            if cached_result:
                return cached_result
            
            # Simulation d'appel de lecture de contrat
            await asyncio.sleep(0.1)
            
            # Données simulées
            import random
            simulated_data = {
                'value': round(random.uniform(20, 30), 2),
                'timestamp': int(time.time()) - random.randint(0, 300),
                'block_number': await self.web3.get_latest_block(),
                'sensor_id': sensor_id
            }
            
            # Mise en cache
            self._set_cache(cache_key, simulated_data)
            
            return simulated_data
            
        except Exception as e:
            logging.error(f"❌ Erreur lecture données {sensor_id}: {e}")
            return None
    
    async def batch_submit_data(self, data_batch: list) -> list:
        """Soumet plusieurs données en lot pour optimiser les coûts"""
        try:
            if not data_batch:
                return []
            
            logging.info(f"📦 Soumission en lot de {len(data_batch)} données")
            
            # Préparation de la transaction batch
            batch_transaction = {
                'function': 'batchSubmitData',
                'contract': 'DataOracle',
                'parameters': {
                    'sensorIds': [item['sensor_id'] for item in data_batch],
                    'values': [int(item['value'] * 100) for item in data_batch],
                    'timestamps': [item['timestamp'] for item in data_batch]
                },
                'gas_limit': 50000 * len(data_batch)  # Gas par item
            }
            
            tx_hash = await self.web3.send_transaction(batch_transaction)
            
            # Retour des hash pour chaque item
            return [tx_hash] * len(data_batch)
            
        except Exception as e:
            logging.error(f"❌ Erreur soumission batch: {e}")
            raise
    
    async def update_stake_async(self, amount: int) -> str:
        """Met à jour le stake du nœud"""
        try:
            transaction_data = {
                'function': 'updateStake',
                'contract': 'StakingContract',
                'parameters': {
                    'amount': amount
                },
                'gas_limit': 150000
            }
            
            tx_hash = await self.web3.send_transaction(transaction_data)
            logging.info(f"💰 Mise à jour stake: {amount} tokens")
            
            return tx_hash
            
        except Exception as e:
            logging.error(f"❌ Erreur mise à jour stake: {e}")
            raise
    
    async def slash_malicious_node_async(self, node_address: str, amount: int) -> str:
        """Pénalise un nœud malveillant"""
        try:
            transaction_data = {
                'function': 'slashStake',
                'contract': 'StakingContract',
                'parameters': {
                    'nodeAddress': node_address,
                    'amount': amount
                },
                'gas_limit': 200000
            }
            
            tx_hash = await self.web3.send_transaction(transaction_data)
            logging.warning(f"⚡ Nœud pénalisé: {node_address} (-{amount} tokens)")
            
            return tx_hash
            
        except Exception as e:
            logging.error(f"❌ Erreur pénalisation: {e}")
            raise
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache"""
        if key in self.call_cache:
            cached_item = self.call_cache[key]
            if time.time() - cached_item['timestamp'] < self.cache_ttl:
                return cached_item['data']
            else:
                del self.call_cache[key]
        return None
    
    def _set_cache(self, key: str, data: Any):
        """Met une valeur en cache"""
        self.call_cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def get_contract_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques des contrats"""
        return {
            'contracts_loaded': len(self.contracts),
            'cache_size': len(self.call_cache),
            'web3_stats': self.web3.get_stats()
        }