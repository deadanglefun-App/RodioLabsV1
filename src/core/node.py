import asyncio
import json
import logging
import time
from typing import List, Dict, Any
from src.core.aggregator import DataAggregator, SensorReading
from src.blockchain.web3_client import Web3Client
from src.blockchain.contract_handler import AsyncContractHandler
from src.security.staking import StakingManager
from src.adapters.temperature_adapter import TemperatureAdapter
from src.adapters.humidity_adapter import HumidityAdapter
from src.adapters.gps_adapter import GPSAdapter

class RodioNode:
    """Nœud RODIO principal avec architecture Chainlink-style"""
    
    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        self.node_id = self.config['node_id']
        
        # Initialisation des composants
        self.web3_client = Web3Client(self.config['network'])
        self.aggregator = DataAggregator(self.config['consensus'])
        self.staking_manager = StakingManager(self.web3_client, self.config['staking'])
        self.contract_handler = AsyncContractHandler(self.web3_client)
        
        # Registre des nœuds pairs pour l'agrégation
        self.peer_nodes = self.config.get('peer_nodes', [])
        
        # Adapters de capteurs
        self.sensor_adapters = self.initialize_adapters()
        
        # Métriques
        self.metrics = {
            'readings_count': 0,
            'successful_submissions': 0,
            'consensus_failures': 0,
            'uptime_start': time.time()
        }
        
    def load_config(self, config_path: str) -> Dict:
        """Charge la configuration depuis le fichier JSON"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f"❌ Fichier de configuration non trouvé: {config_path}")
            raise
        except json.JSONDecodeError as e:
            logging.error(f"❌ Erreur de parsing JSON: {e}")
            raise
    
    def initialize_adapters(self) -> Dict:
        """Initialise les adapters de capteurs"""
        adapters = {}
        
        for sensor_name, sensor_config in self.config['sensors'].items():
            adapter_class = sensor_config['adapter']
            
            if adapter_class == 'TemperatureAdapter':
                adapters[sensor_name] = TemperatureAdapter(sensor_config)
            elif adapter_class == 'HumidityAdapter':
                adapters[sensor_name] = HumidityAdapter(sensor_config)
            elif adapter_class == 'GPSAdapter':
                adapters[sensor_name] = GPSAdapter(sensor_config)
            else:
                logging.warning(f"⚠️ Adapter inconnu: {adapter_class}")
        
        logging.info(f"✅ {len(adapters)} adapters initialisés")
        return adapters
    
    async def start(self):
        """Démarre le nœud avec tous les services"""
        logging.info(f"🔄 Démarrage du nœud {self.node_id}...")
        
        # Vérification du stake
        if not await self.staking_manager.check_stake():
            raise Exception("❌ Stake insuffisant pour opérer")
        
        logging.info("✅ Stake vérifié - Nœud autorisé à opérer")
        
        # Démarrage des services
        tasks = [
            self.start_sensor_polling(),
            self.start_peer_communication(),
            self.monitor_network_health()
        ]
        
        await asyncio.gather(*tasks)
    
    async def start_sensor_polling(self):
        """Démarre la lecture périodique des capteurs"""
        logging.info("📡 Démarrage du polling des capteurs...")
        
        while True:
            try:
                for sensor_name, adapter in self.sensor_adapters.items():
                    await self.process_sensor_reading(sensor_name, adapter)
                    
                await asyncio.sleep(30)  # Polling toutes les 30 secondes
                
            except Exception as e:
                logging.error(f"❌ Erreur dans le polling: {e}")
                await asyncio.sleep(5)  # Retry après 5 secondes
    
    async def process_sensor_reading(self, sensor_name: str, adapter):
        """Traite une lecture de capteur"""
        try:
            # Lecture des données
            raw_data = await adapter.read_data()
            
            if not adapter.validate_data(raw_data):
                logging.warning(f"⚠️ Données invalides pour {sensor_name}")
                return
            
            # Transformation des données
            processed_data = adapter.transform_data(raw_data)
            self.metrics['readings_count'] += 1
            
            logging.info(f"📊 {sensor_name}: {processed_data['value']} {processed_data.get('unit', '')}")
            
            # Collecte des données des pairs pour consensus
            peer_readings = await self.collect_peer_readings(sensor_name)
            
            # Ajout de notre lecture
            our_reading = SensorReading(
                value=processed_data['value'],
                timestamp=processed_data['timestamp'],
                node_id=self.node_id,
                signature=self.sign_data(processed_data)
            )
            peer_readings.append(our_reading)
            
            # Agrégation avec consensus
            if len(peer_readings) >= self.config['consensus']['min_nodes']:
                await self.process_consensus(sensor_name, peer_readings)
            else:
                logging.warning(f"⚠️ Pas assez de nœuds pour consensus ({len(peer_readings)}/{self.config['consensus']['min_nodes']})")
                
        except Exception as e:
            logging.error(f"❌ Erreur traitement {sensor_name}: {e}")
    
    async def collect_peer_readings(self, sensor_name: str) -> List[SensorReading]:
        """Collecte les lectures des nœuds pairs"""
        peer_readings = []
        
        for peer_url in self.peer_nodes:
            try:
                # Simulation d'appel HTTP aux pairs
                # En réalité, on ferait un appel HTTP/gRPC
                import random
                simulated_value = 23.0 + random.uniform(-2, 2)  # Simulation
                
                reading = SensorReading(
                    value=simulated_value,
                    timestamp=int(time.time()),
                    node_id=f"peer_{peer_url.split(':')[-1]}",
                    signature="simulated_signature"
                )
                peer_readings.append(reading)
                
            except Exception as e:
                logging.warning(f"⚠️ Impossible de contacter le pair {peer_url}: {e}")
        
        return peer_readings
    
    async def process_consensus(self, sensor_name: str, readings: List[SensorReading]):
        """Traite le consensus et soumet à la blockchain"""
        try:
            # Agrégation avec consensus
            aggregated_data = await self.aggregator.aggregate_readings(readings)
            
            logging.info(f"✅ Consensus atteint pour {sensor_name}: {aggregated_data['value']} (Confidence: {aggregated_data['confidence']:.1%})")
            
            # Soumission à la blockchain
            tx_hash = await self.contract_handler.submit_data_async(
                sensor_id=sensor_name,
                value=aggregated_data['value'],
                timestamp=aggregated_data['timestamp']
            )
            
            self.metrics['successful_submissions'] += 1
            logging.info(f"🔗 Données soumises à la blockchain: {tx_hash}")
            
        except Exception as e:
            self.metrics['consensus_failures'] += 1
            logging.error(f"❌ Échec du consensus pour {sensor_name}: {e}")
    
    def sign_data(self, data: Dict) -> str:
        """Signe cryptographiquement les données"""
        # Implémentation simplifiée - en réalité utiliser ECDSA
        import hashlib
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(f"{self.node_id}:{data_str}".encode()).hexdigest()
    
    async def start_peer_communication(self):
        """Gère la communication avec les pairs"""
        logging.info("🌐 Démarrage de la communication inter-nœuds...")
        
        while True:
            try:
                # Heartbeat avec les pairs
                await self.send_heartbeat_to_peers()
                await asyncio.sleep(60)  # Heartbeat toutes les minutes
                
            except Exception as e:
                logging.error(f"❌ Erreur communication pairs: {e}")
                await asyncio.sleep(10)
    
    async def send_heartbeat_to_peers(self):
        """Envoie un heartbeat aux nœuds pairs"""
        heartbeat_data = {
            'node_id': self.node_id,
            'timestamp': int(time.time()),
            'status': 'healthy',
            'metrics': self.metrics
        }
        
        for peer_url in self.peer_nodes:
            try:
                # Simulation d'envoi heartbeat
                logging.debug(f"💓 Heartbeat envoyé à {peer_url}")
            except Exception as e:
                logging.warning(f"⚠️ Heartbeat échoué pour {peer_url}: {e}")
    
    async def monitor_network_health(self):
        """Surveille la santé du réseau"""
        logging.info("🔍 Démarrage du monitoring réseau...")
        
        while True:
            try:
                # Vérification de la connectivité blockchain
                latest_block = await self.web3_client.get_latest_block()
                
                # Vérification du stake
                stake_ok = await self.staking_manager.check_stake()
                
                if not stake_ok:
                    logging.error("❌ Stake insuffisant détecté!")
                
                # Log des métriques
                uptime = time.time() - self.metrics['uptime_start']
                logging.info(f"📈 Métriques - Uptime: {uptime:.0f}s, Lectures: {self.metrics['readings_count']}, Soumissions: {self.metrics['successful_submissions']}")
                
                await asyncio.sleep(300)  # Check toutes les 5 minutes
                
            except Exception as e:
                logging.error(f"❌ Erreur monitoring: {e}")
                await asyncio.sleep(30)