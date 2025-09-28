import pytest
import asyncio
from unittest.mock import Mock, patch
from src.adapters.temperature_adapter import TemperatureAdapter
from src.adapters.humidity_adapter import HumidityAdapter
from src.adapters.gps_adapter import GPSAdapter

class TestTemperatureAdapter:
    """Tests pour l'adapter de température"""
    
    def setup_method(self):
        config = {
            'mqtt_topic': 'sensors/test/temperature',
            'min_temperature': -50.0,
            'max_temperature': 100.0,
            'unit': 'celsius'
        }
        self.adapter = TemperatureAdapter(config)
    
    @pytest.mark.asyncio
    async def test_read_data(self):
        """Test de lecture des données"""
        data = await self.adapter.read_data()
        
        assert 'raw_value' in data
        assert 'unit' in data
        assert 'sensor_id' in data
        assert isinstance(data['raw_value'], (int, float))
    
    def test_validate_data_valid(self):
        """Test validation avec données valides"""
        valid_data = {
            'raw_value': 23.5,
            'quality': 'good',
            'battery_level': 80
        }
        
        assert self.adapter.validate_data(valid_data) == True
    
    def test_validate_data_invalid_temperature(self):
        """Test validation avec température invalide"""
        invalid_data = {
            'raw_value': 150.0,  # Trop chaud
            'quality': 'good',
            'battery_level': 80
        }
        
        assert self.adapter.validate_data(invalid_data) == False
    
    def test_validate_data_poor_quality(self):
        """Test validation avec qualité faible"""
        poor_quality_data = {
            'raw_value': 23.5,
            'quality': 'poor',
            'battery_level': 80
        }
        
        assert self.adapter.validate_data(poor_quality_data) == False
    
    def test_transform_data(self):
        """Test transformation des données"""
        raw_data = {
            'raw_value': 23.5,
            'unit': 'celsius',
            'sensor_id': 'temp_001',
            'quality': 'good',
            'battery_level': 80
        }
        
        transformed = self.adapter.transform_data(raw_data)
        
        assert transformed['sensor_type'] == 'temperature'
        assert transformed['value'] == 23.5
        assert transformed['unit'] == 'celsius'
        assert 'timestamp' in transformed
        assert 'quality_score' in transformed

class TestHumidityAdapter:
    """Tests pour l'adapter d'humidité"""
    
    def setup_method(self):
        config = {
            'mqtt_topic': 'sensors/test/humidity',
            'min_humidity': 0.0,
            'max_humidity': 100.0
        }
        self.adapter = HumidityAdapter(config)
    
    @pytest.mark.asyncio
    async def test_read_data(self):
        """Test de lecture des données d'humidité"""
        data = await self.adapter.read_data()
        
        assert 'raw_value' in data
        assert 'unit' in data
        assert data['unit'] == 'percent'
        assert isinstance(data['raw_value'], (int, float))
    
    def test_validate_data_valid(self):
        """Test validation avec données valides"""
        valid_data = {'raw_value': 65.5}
        assert self.adapter.validate_data(valid_data) == True
    
    def test_validate_data_invalid_range(self):
        """Test validation avec valeur hors limites"""
        invalid_data = {'raw_value': 150.0}  # > 100%
        assert self.adapter.validate_data(invalid_data) == False
    
    def test_transform_data_with_calibration(self):
        """Test transformation avec calibration"""
        raw_data = {
            'raw_value': 65.0,
            'sensor_id': 'hum_001',
            'calibration_offset': 2.0,
            'mqtt_topic': 'sensors/test/humidity'
        }
        
        transformed = self.adapter.transform_data(raw_data)
        
        assert transformed['sensor_type'] == 'humidity'
        assert transformed['value'] == 67.0  # 65 + 2
        assert transformed['unit'] == 'percent'

class TestGPSAdapter:
    """Tests pour l'adapter GPS"""
    
    def setup_method(self):
        config = {
            'mqtt_topic': 'sensors/test/gps',
            'base_latitude': 48.8566,
            'base_longitude': 2.3522
        }
        self.adapter = GPSAdapter(config)
    
    @pytest.mark.asyncio
    async def test_read_data(self):
        """Test de lecture des données GPS"""
        data = await self.adapter.read_data()
        
        assert 'latitude' in data
        assert 'longitude' in data
        assert 'satellites' in data
        assert 'hdop' in data
        assert 'fix_quality' in data
    
    def test_validate_data_valid_gps(self):
        """Test validation avec fix GPS valide"""
        valid_data = {
            'fix_quality': 'GPS',
            'satellites': 6,
            'latitude': 48.8566,
            'longitude': 2.3522,
            'hdop': 1.2
        }
        
        assert self.adapter.validate_data(valid_data) == True
    
    def test_validate_data_no_fix(self):
        """Test validation sans fix GPS"""
        no_fix_data = {
            'fix_quality': 'NO_FIX',
            'satellites': 2,
            'latitude': 48.8566,
            'longitude': 2.3522,
            'hdop': 1.2
        }
        
        assert self.adapter.validate_data(no_fix_data) == False
    
    def test_validate_data_poor_hdop(self):
        """Test validation avec HDOP trop élevé"""
        poor_hdop_data = {
            'fix_quality': 'GPS',
            'satellites': 6,
            'latitude': 48.8566,
            'longitude': 2.3522,
            'hdop': 6.0  # Trop élevé
        }
        
        assert self.adapter.validate_data(poor_hdop_data) == False
    
    def test_transform_data(self):
        """Test transformation des données GPS"""
        raw_data = {
            'latitude': 48.8566,
            'longitude': 2.3522,
            'altitude': 100.0,
            'satellites': 8,
            'hdop': 1.2,
            'speed': 0.0,
            'heading': 0,
            'fix_quality': 'GPS',
            'sensor_id': 'gps_001'
        }
        
        transformed = self.adapter.transform_data(raw_data)
        
        assert transformed['sensor_type'] == 'gps'
        assert transformed['unit'] == 'coordinates'
        assert 'value' in transformed
        assert 'latitude' in transformed['value']
        assert 'longitude' in transformed['value']
        assert 'accuracy' in transformed['value']

class TestAdapterIntegration:
    """Tests d'intégration des adapters"""
    
    @pytest.mark.asyncio
    async def test_multiple_adapters_concurrent(self):
        """Test de lecture simultanée de plusieurs adapters"""
        temp_adapter = TemperatureAdapter({'mqtt_topic': 'sensors/temp'})
        hum_adapter = HumidityAdapter({'mqtt_topic': 'sensors/hum'})
        gps_adapter = GPSAdapter({'mqtt_topic': 'sensors/gps'})
        
        # Lecture simultanée
        results = await asyncio.gather(
            temp_adapter.read_data(),
            hum_adapter.read_data(),
            gps_adapter.read_data()
        )
        
        assert len(results) == 3
        assert all(isinstance(result, dict) for result in results)
    
    def test_adapter_stats(self):
        """Test des statistiques des adapters"""
        adapter = TemperatureAdapter({'mqtt_topic': 'sensors/test'})
        
        # Simulation de lectures
        adapter.update_reading_stats()
        adapter.update_reading_stats()
        
        stats = adapter.get_stats()
        
        assert stats['sensor_type'] == 'temperature'
        assert stats['reading_count'] == 2
        assert 'last_reading_time' in stats
        assert 'polling_interval' in stats