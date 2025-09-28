import asyncio
import random
import time
from typing import Dict, Any
from src.adapters.base_adapter import SensorAdapter

class GPSAdapter(SensorAdapter):
    """Adapter pour capteurs GPS"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.mqtt_topic = config.get('mqtt_topic', 'sensors/gps')
        # Coordonnées de base (Paris par défaut)
        self.base_lat = config.get('base_latitude', 48.8566)
        self.base_lon = config.get('base_longitude', 2.3522)
    
    async def read_data(self) -> Dict[str, Any]:
        """Lit les données GPS"""
        await asyncio.sleep(0.2)  # GPS plus lent
        
        # Simulation de dérive GPS réaliste
        lat_drift = random.uniform(-0.001, 0.001)  # ~100m de dérive
        lon_drift = random.uniform(-0.001, 0.001)
        
        # Précision variable selon conditions
        hdop = random.uniform(0.8, 3.0)  # Horizontal Dilution of Precision
        satellites = random.randint(4, 12)
        
        raw_data = {
            'latitude': round(self.base_lat + lat_drift, 6),
            'longitude': round(self.base_lon + lon_drift, 6),
            'altitude': round(random.uniform(50, 200), 1),  # Altitude en mètres
            'speed': round(random.uniform(0, 5), 1),  # Vitesse en km/h
            'heading': random.randint(0, 359),  # Direction en degrés
            'satellites': satellites,
            'hdop': round(hdop, 1),
            'fix_quality': 'GPS' if satellites >= 4 else 'NO_FIX',
            'timestamp_gps': int(time.time()),
            'sensor_id': f'gps_{hash(self.mqtt_topic) % 1000}'
        }
        
        # Simulation de perte de signal
        if random.random() < 0.1:  # 10% de chance de perte
            raw_data['fix_quality'] = 'NO_FIX'
            raw_data['satellites'] = random.randint(0, 3)
        
        self.update_reading_stats()
        return raw_data
    
    def validate_data(self, data: Dict) -> bool:
        """Valide les données GPS"""
        try:
            # Vérification de la qualité du fix
            if data.get('fix_quality') != 'GPS':
                print("⚠️ Pas de fix GPS valide")
                return False
            
            # Vérification du nombre de satellites
            satellites = data.get('satellites', 0)
            if satellites < 4:
                print(f"⚠️ Pas assez de satellites: {satellites}")
                return False
            
            # Vérification des coordonnées
            lat = data.get('latitude')
            lon = data.get('longitude')
            
            if lat is None or lon is None:
                return False
            
            # Vérification des limites géographiques
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                print(f"⚠️ Coordonnées invalides: {lat}, {lon}")
                return False
            
            # Vérification HDOP (précision)
            hdop = data.get('hdop', 999)
            if hdop > 5.0:  # HDOP trop élevé = précision faible
                print(f"⚠️ Précision GPS insuffisante: HDOP {hdop}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur validation GPS: {e}")
            return False
    
    def transform_data(self, raw_data: Dict) -> Dict[str, Any]:
        """Transforme les données GPS"""
        try:
            # Calcul de la précision estimée basée sur HDOP
            hdop = raw_data.get('hdop', 1.0)
            estimated_accuracy = hdop * 5  # Approximation en mètres
            
            transformed_data = {
                'sensor_type': 'gps',
                'value': {
                    'latitude': raw_data['latitude'],
                    'longitude': raw_data['longitude'],
                    'altitude': raw_data.get('altitude'),
                    'accuracy': round(estimated_accuracy, 1)
                },
                'unit': 'coordinates',
                'timestamp': raw_data.get('timestamp_gps', int(time.time())),
                'sensor_id': raw_data.get('sensor_id'),
                'quality_score': self._calculate_gps_quality(raw_data),
                'metadata': {
                    'satellites': raw_data.get('satellites'),
                    'hdop': raw_data.get('hdop'),
                    'speed': raw_data.get('speed'),
                    'heading': raw_data.get('heading'),
                    'fix_quality': raw_data.get('fix_quality'),
                    'mqtt_topic': self.mqtt_topic
                }
            }
            
            return transformed_data
            
        except Exception as e:
            print(f"❌ Erreur transformation GPS: {e}")
            raise
    
    def _calculate_gps_quality(self, raw_data: Dict) -> float:
        """Calcule un score de qualité GPS"""
        score = 1.0
        
        # Pénalité basée sur HDOP
        hdop = raw_data.get('hdop', 1.0)
        if hdop > 2.0:
            score *= 0.7
        elif hdop > 1.5:
            score *= 0.9
        
        # Bonus pour nombre de satellites
        satellites = raw_data.get('satellites', 4)
        if satellites >= 8:
            score *= 1.1
        elif satellites < 6:
            score *= 0.8
        
        return min(1.0, round(score, 2))