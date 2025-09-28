import asyncio
import random
import time
from typing import Dict, Any
from src.adapters.base_adapter import SensorAdapter

class TemperatureAdapter(SensorAdapter):
    """Adapter pour capteurs de température"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.mqtt_topic = config.get('mqtt_topic', 'sensors/temperature')
        self.min_temp = config.get('min_temperature', -50.0)
        self.max_temp = config.get('max_temperature', 100.0)
        self.unit = config.get('unit', 'celsius')
    
    async def read_data(self) -> Dict[str, Any]:
        """Lit les données de température"""
        # Simulation d'une lecture MQTT/HTTP
        await asyncio.sleep(0.1)  # Simulation latence réseau
        
        # Génération d'une température réaliste avec variations
        base_temp = 23.0  # Température de base
        variation = random.uniform(-3.0, 3.0)  # Variation naturelle
        noise = random.uniform(-0.5, 0.5)  # Bruit du capteur
        
        temperature = base_temp + variation + noise
        
        # Simulation d'erreurs occasionnelles
        if random.random() < 0.05:  # 5% de chance d'erreur
            temperature = random.uniform(-100, 200)  # Valeur aberrante
        
        raw_data = {
            'raw_value': round(temperature, 2),
            'unit': self.unit,
            'sensor_id': f'temp_{hash(self.mqtt_topic) % 1000}',
            'mqtt_topic': self.mqtt_topic,
            'quality': random.choice(['good', 'fair', 'poor']),
            'battery_level': random.uniform(20, 100)
        }
        
        self.update_reading_stats()
        return raw_data
    
    def validate_data(self, data: Dict) -> bool:
        """Valide les données de température"""
        try:
            temp_value = data.get('raw_value')
            
            # Vérifications de base
            if temp_value is None:
                return False
            
            if not isinstance(temp_value, (int, float)):
                return False
            
            # Vérification des limites physiques
            if not (self.min_temp <= temp_value <= self.max_temp):
                print(f"⚠️ Température hors limites: {temp_value}°C")
                return False
            
            # Vérification de la qualité du signal
            quality = data.get('quality', 'unknown')
            if quality == 'poor':
                print(f"⚠️ Qualité du signal faible pour température")
                return False
            
            # Vérification du niveau de batterie
            battery = data.get('battery_level', 100)
            if battery < 10:
                print(f"⚠️ Batterie faible du capteur température: {battery}%")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur validation température: {e}")
            return False
    
    def transform_data(self, raw_data: Dict) -> Dict[str, Any]:
        """Transforme les données brutes en format standardisé"""
        try:
            # Conversion d'unité si nécessaire
            temp_celsius = raw_data['raw_value']
            if raw_data.get('unit') == 'fahrenheit':
                temp_celsius = (temp_celsius - 32) * 5/9
            elif raw_data.get('unit') == 'kelvin':
                temp_celsius = temp_celsius - 273.15
            
            transformed_data = {
                'sensor_type': 'temperature',
                'value': round(temp_celsius, 2),
                'unit': 'celsius',
                'timestamp': int(time.time()),
                'sensor_id': raw_data.get('sensor_id'),
                'quality_score': self._calculate_quality_score(raw_data),
                'metadata': {
                    'original_unit': raw_data.get('unit'),
                    'battery_level': raw_data.get('battery_level'),
                    'mqtt_topic': raw_data.get('mqtt_topic'),
                    'adapter_version': '1.0.0'
                }
            }
            
            return transformed_data
            
        except Exception as e:
            print(f"❌ Erreur transformation température: {e}")
            raise
    
    def _calculate_quality_score(self, raw_data: Dict) -> float:
        """Calcule un score de qualité pour la mesure"""
        score = 1.0
        
        # Pénalité pour qualité du signal
        quality = raw_data.get('quality', 'good')
        if quality == 'fair':
            score *= 0.8
        elif quality == 'poor':
            score *= 0.5
        
        # Pénalité pour batterie faible
        battery = raw_data.get('battery_level', 100)
        if battery < 20:
            score *= 0.7
        elif battery < 50:
            score *= 0.9
        
        return round(score, 2)