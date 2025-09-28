#!/usr/bin/env python3
"""
Simulateur de capteurs IoT pour tests RODIO
Génère des données réalistes avec outliers occasionnels
"""

import asyncio
import random
import json
import time
import logging
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class SensorProfile:
    """Profile d'un capteur avec ses caractéristiques"""
    sensor_id: str
    sensor_type: str
    min_value: float
    max_value: float
    unit: str
    noise_level: float = 0.1
    outlier_probability: float = 0.05

class SensorSimulator:
    """Simulateur de capteurs IoT pour tests"""
    
    def __init__(self):
        self.sensors = self._create_sensor_profiles()
        self.running = False
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _create_sensor_profiles(self) -> List[SensorProfile]:
        """Crée des profils de capteurs réalistes"""
        return [
            # Capteurs de température
            SensorProfile("temp_fridge_01", "temperature", 2.0, 8.0, "celsius", 0.2, 0.03),
            SensorProfile("temp_room_01", "temperature", 18.0, 25.0, "celsius", 0.5, 0.05),
            SensorProfile("temp_outdoor_01", "temperature", -10.0, 35.0, "celsius", 1.0, 0.08),
            
            # Capteurs d'humidité
            SensorProfile("humidity_room_01", "humidity", 40.0, 70.0, "percent", 2.0, 0.04),
            SensorProfile("humidity_greenhouse_01", "humidity", 60.0, 90.0, "percent", 1.5, 0.02),
            
            # Capteurs GPS
            SensorProfile("gps_truck_01", "gps", 0.0, 1.0, "coordinates", 0.001, 0.1),
            SensorProfile("gps_drone_01", "gps", 0.0, 1.0, "coordinates", 0.0005, 0.15),
        ]
    
    def generate_sensor_reading(self, sensor: SensorProfile) -> Dict:
        """Génère une lecture de capteur"""
        # Valeur de base
        base_value = (sensor.min_value + sensor.max_value) / 2
        
        # Variation naturelle
        variation_range = (sensor.max_value - sensor.min_value) * 0.3
        variation = random.uniform(-variation_range, variation_range)
        
        # Bruit du capteur
        noise = random.uniform(-sensor.noise_level, sensor.noise_level)
        
        # Valeur finale
        value = base_value + variation + noise
        
        # Génération d'outliers occasionnels
        if random.random() < sensor.outlier_probability:
            if sensor.sensor_type == "temperature":
                value = random.uniform(-50, 100)  # Valeur aberrante
            elif sensor.sensor_type == "humidity":
                value = random.uniform(-10, 120)
            elif sensor.sensor_type == "gps":
                # Simulation de perte de signal GPS
                return self._generate_gps_no_fix(sensor)
        
        # Formatage selon le type de capteur
        if sensor.sensor_type == "gps":
            return self._generate_gps_reading(sensor, value)
        else:
            return {
                "sensor_id": sensor.sensor_id,
                "sensor_type": sensor.sensor_type,
                "value": round(value, 2),
                "unit": sensor.unit,
                "timestamp": int(time.time()),
                "quality_score": random.uniform(0.8, 1.0),
                "battery_level": random.uniform(20, 100),
                "signal_strength": random.randint(1, 5)
            }
    
    def _generate_gps_reading(self, sensor: SensorProfile, drift: float) -> Dict:
        """Génère une lecture GPS réaliste"""
        # Coordonnées de base (Paris)
        base_lat = 48.8566
        base_lon = 2.3522
        
        # Dérive GPS réaliste
        lat_drift = drift * random.uniform(-0.001, 0.001)
        lon_drift = drift * random.uniform(-0.001, 0.001)
        
        satellites = random.randint(4, 12)
        hdop = random.uniform(0.8, 3.0)
        
        return {
            "sensor_id": sensor.sensor_id,
            "sensor_type": "gps",
            "value": {
                "latitude": round(base_lat + lat_drift, 6),
                "longitude": round(base_lon + lon_drift, 6),
                "altitude": round(random.uniform(50, 200), 1),
                "accuracy": round(hdop * 5, 1)
            },
            "unit": "coordinates",
            "timestamp": int(time.time()),
            "satellites": satellites,
            "hdop": round(hdop, 1),
            "fix_quality": "GPS" if satellites >= 4 else "NO_FIX",
            "speed": round(random.uniform(0, 80), 1),
            "heading": random.randint(0, 359)
        }
    
    def _generate_gps_no_fix(self, sensor: SensorProfile) -> Dict:
        """Génère une lecture GPS sans fix (perte de signal)"""
        return {
            "sensor_id": sensor.sensor_id,
            "sensor_type": "gps",
            "value": None,
            "unit": "coordinates",
            "timestamp": int(time.time()),
            "satellites": random.randint(0, 3),
            "hdop": random.uniform(5.0, 20.0),
            "fix_quality": "NO_FIX",
            "error": "Insufficient satellites"
        }
    
    async def start_simulation(self, interval: float = 5.0):
        """Démarre la simulation continue"""
        self.running = True
        self.logger.info(f"🚀 Démarrage simulation avec {len(self.sensors)} capteurs")
        
        while self.running:
            try:
                # Génération des lectures pour tous les capteurs
                readings = []
                for sensor in self.sensors:
                    reading = self.generate_sensor_reading(sensor)
                    readings.append(reading)
                    
                    # Log de la lecture
                    if reading.get('value') is not None:
                        if sensor.sensor_type == "gps":
                            lat = reading['value']['latitude']
                            lon = reading['value']['longitude']
                            self.logger.info(f"📍 {sensor.sensor_id}: {lat}, {lon}")
                        else:
                            value = reading['value']
                            unit = reading['unit']
                            self.logger.info(f"📊 {sensor.sensor_id}: {value} {unit}")
                    else:
                        self.logger.warning(f"⚠️ {sensor.sensor_id}: Pas de données")
                
                # Simulation d'envoi MQTT (ici juste un log)
                self.logger.info(f"📡 {len(readings)} lectures générées")
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"❌ Erreur simulation: {e}")
                await asyncio.sleep(1)
    
    def stop_simulation(self):
        """Arrête la simulation"""
        self.running = False
        self.logger.info("🛑 Simulation arrêtée")
    
    def get_sensor_stats(self) -> Dict:
        """Retourne les statistiques des capteurs"""
        stats = {
            "total_sensors": len(self.sensors),
            "sensor_types": {},
            "sensors": []
        }
        
        for sensor in self.sensors:
            if sensor.sensor_type not in stats["sensor_types"]:
                stats["sensor_types"][sensor.sensor_type] = 0
            stats["sensor_types"][sensor.sensor_type] += 1
            
            stats["sensors"].append({
                "id": sensor.sensor_id,
                "type": sensor.sensor_type,
                "range": f"{sensor.min_value}-{sensor.max_value} {sensor.unit}",
                "outlier_rate": f"{sensor.outlier_probability*100:.1f}%"
            })
        
        return stats

async def main():
    """Point d'entrée principal"""
    simulator = SensorSimulator()
    
    # Affichage des statistiques
    stats = simulator.get_sensor_stats()
    print("📊 Configuration des capteurs:")
    print(f"   Total: {stats['total_sensors']} capteurs")
    for sensor_type, count in stats['sensor_types'].items():
        print(f"   {sensor_type}: {count} capteurs")
    
    print("\n🚀 Démarrage de la simulation...")
    print("   Ctrl+C pour arrêter\n")
    
    try:
        await simulator.start_simulation(interval=3.0)
    except KeyboardInterrupt:
        simulator.stop_simulation()
        print("\n✅ Simulation terminée")

if __name__ == "__main__":
    asyncio.run(main())