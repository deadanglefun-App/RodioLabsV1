from abc import ABC, abstractmethod
from typing import Dict, Any
import time

class SensorAdapter(ABC):
    """Interface commune pour tous les adapters de capteurs"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.sensor_type = self.__class__.__name__.replace('Adapter', '').lower()
        self.last_reading_time = 0
        self.reading_count = 0
    
    @abstractmethod
    async def read_data(self) -> Dict[str, Any]:
        """Lit les données brutes du capteur"""
        pass
    
    @abstractmethod
    def validate_data(self, data: Dict) -> bool:
        """Valide les données lues"""
        pass
    
    @abstractmethod
    def transform_data(self, raw_data: Dict) -> Dict[str, Any]:
        """Transforme les données brutes en format standardisé"""
        pass
    
    def get_polling_interval(self) -> int:
        """Retourne l'intervalle de polling en secondes"""
        return self.config.get('polling_interval', 60)
    
    def should_poll(self) -> bool:
        """Détermine s'il faut faire une nouvelle lecture"""
        current_time = time.time()
        return (current_time - self.last_reading_time) >= self.get_polling_interval()
    
    def update_reading_stats(self):
        """Met à jour les statistiques de lecture"""
        self.last_reading_time = time.time()
        self.reading_count += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de l'adapter"""
        return {
            'sensor_type': self.sensor_type,
            'reading_count': self.reading_count,
            'last_reading_time': self.last_reading_time,
            'polling_interval': self.get_polling_interval()
        }