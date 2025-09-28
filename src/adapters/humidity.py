import asyncio
import random
import time
from typing import Dict, Any
from src.adapters.base_adapter import SensorAdapter

class HumidityAdapter(SensorAdapter):
    """Adapter pour capteurs d'humidité"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.mqtt_topic = config.get('mqtt_topic', 'sensors/humidity')
        self.min_humidity = config.get('min_humidity', 0.0)
        self.max_humidity = config.get('max_humidity', 100.0)
    
    async def read_data(self) -> Dict[str, Any]:
        """Lit les données d'humidité"""
        await asyncio.sleep(0.1)  # Simulation latence
        
        # Génération d'une humidité réaliste
        base_humidity = 65.0  # Humidité de base
        variation = random.uniform(-15.0, 15.0)
        noise = random.uniform(-2.0, 2.0)
        
        humidity = max(0, min(100, base_humidity + variation + noise))
        
        # Simulation d'erreurs
        if random.random() < 0.03:  # 3% de chance d'erreur
            humidity = random.uniform(-10, 120)
        
        raw_data = {
            'raw_value': round(humidity, 1),
            'unit': 'percent',
            'sensor_id': f'hum_{hash(self.mqtt_topic) % 1000}',
            'mqtt_topic': self.mqtt_topic,
            'calibration_offset': random.uniform(-1.0, 1.0),
            'temperature_compensation': random.uniform(-0.5, 0.5)
        }
        
        self.update_reading_stats()
        return raw_data
    
    def validate_data(self, data: Dict) -> bool:
        """Valide les données d'humidité"""
        try:
            humidity_value = data.get('raw_value')
            
            if humidity_value is None or not isinstance(humidity_value, (int, float)):
                return False
            
            # Vérification des limites physiques
            if not (self.min_humidity <= humidity_value <= self.max_humidity):
                print(f"⚠️ Humidité hors limites: {humidity_value}%")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur validation humidité: {e}")
            return False
    
    def transform_data(self, raw_data: Dict) -> Dict[str, Any]:
        """Transforme les données d'humidité"""
        try:
            # Application de l'offset de calibration
            calibrated_value = raw_data['raw_value'] + raw_data.get('calibration_offset', 0)
            calibrated_value = max(0, min(100, calibrated_value))  # Clamp 0-100%
            
            transformed_data = {
                'sensor_type': 'humidity',
                'value': round(calibrated_value, 1),
                'unit': 'percent',
                'timestamp': int(time.time()),
                'sensor_id': raw_data.get('sensor_id'),
                'quality_score': 0.95,  # Humidité généralement stable
                'metadata': {
                    'raw_value': raw_data['raw_value'],
                    'calibration_offset': raw_data.get('calibration_offset'),
                    'temperature_compensation': raw_data.get('temperature_compensation'),
                    'mqtt_topic': raw_data.get('mqtt_topic')
                }
            }
            
            return transformed_data
            
        except Exception as e:
            print(f"❌ Erreur transformation humidité: {e}")
            raise