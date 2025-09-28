import pytest
import time
from unittest.mock import Mock, AsyncMock
from src.core.aggregator import DataAggregator, SensorReading, ConsensusError

class TestDataAggregator:
    """Tests pour l'agrégateur de données avec consensus"""
    
    def setup_method(self):
        consensus_config = {
            'consensus_threshold': 0.8,
            'outlier_tolerance': 0.05,
            'min_nodes': 3
        }
        self.aggregator = DataAggregator(consensus_config)
    
    def create_sensor_readings(self, values, node_prefix="node"):
        """Crée des lectures de capteurs pour les tests"""
        readings = []
        timestamp = int(time.time())
        
        for i, value in enumerate(values):
            reading = SensorReading(
                value=value,
                timestamp=timestamp,
                node_id=f"{node_prefix}_{i+1}",
                signature=f"sig_{i+1}"
            )
            readings.append(reading)
        
        return readings
    
    @pytest.mark.asyncio
    async def test_aggregate_readings_success(self):
        """Test d'agrégation réussie avec consensus"""
        # Valeurs cohérentes
        values = [23.1, 23.3, 23.2, 23.4, 23.0]
        readings = self.create_sensor_readings(values)
        
        result = await self.aggregator.aggregate_readings(readings)
        
        assert 'value' in result
        assert 'confidence' in result
        assert 'nodes_participated' in result
        assert result['nodes_participated'] == 5
        assert 22.5 <= result['value'] <= 24.0  # Valeur raisonnable
    
    @pytest.mark.asyncio
    async def test_aggregate_readings_with_outliers(self):
        """Test d'agrégation avec outliers"""
        # Valeurs avec outliers
        values = [23.1, 23.2, 23.3, 50.0, 23.0]  # 50.0 est un outlier
        readings = self.create_sensor_readings(values)
        
        result = await self.aggregator.aggregate_readings(readings)
        
        # L'outlier devrait être filtré
        assert 'outliers_removed' in result
        assert result['outliers_removed'] >= 1
        assert 22.5 <= result['value'] <= 24.0
    
    @pytest.mark.asyncio
    async def test_aggregate_readings_insufficient_nodes(self):
        """Test avec nombre insuffisant de nœuds"""
        values = [23.1, 23.2]  # Seulement 2 nœuds
        readings = self.create_sensor_readings(values)
        
        with pytest.raises(ValueError, match="Minimum .* nœuds requis"):
            await self.aggregator.aggregate_readings(readings)
    
    @pytest.mark.asyncio
    async def test_aggregate_readings_no_consensus(self):
        """Test sans consensus possible"""
        # Valeurs très dispersées
        values = [10.0, 20.0, 30.0, 40.0, 50.0]
        readings = self.create_sensor_readings(values)
        
        with pytest.raises(ConsensusError, match="consensus"):
            await self.aggregator.aggregate_readings(readings)
    
    def test_validate_signatures(self):
        """Test de validation des signatures"""
        readings = [
            SensorReading(23.1, int(time.time()), "node1", "a" * 64),  # Signature valide
            SensorReading(23.2, int(time.time()), "node2", "invalid"),  # Signature invalide
            SensorReading(23.3, int(time.time()), "node3", "b" * 64),  # Signature valide
        ]
        
        validated = self.aggregator.validate_signatures(readings)
        
        assert len(validated) == 2  # Seulement les signatures valides
        assert all(len(r.signature) == 64 for r in validated)
    
    def test_remove_outliers_iqr(self):
        """Test de suppression d'outliers avec méthode IQR"""
        values = [20, 21, 22, 23, 24, 25, 100]  # 100 est un outlier évident
        
        filtered = self.aggregator.remove_outliers(values)
        
        assert 100 not in filtered
        assert len(filtered) < len(values)
        assert all(20 <= v <= 30 for v in filtered)
    
    def test_remove_outliers_insufficient_data(self):
        """Test avec données insuffisantes pour filtrage"""
        values = [20, 21, 22]  # Moins de 4 valeurs
        
        filtered = self.aggregator.remove_outliers(values)
        
        # Devrait retourner toutes les valeurs
        assert filtered == values
    
    def test_check_consensus_success(self):
        """Test de vérification de consensus réussi"""
        values = [23.0, 23.1, 23.2, 23.1, 23.0]  # Valeurs très proches
        
        consensus = self.aggregator.check_consensus(values)
        
        assert consensus == True
    
    def test_check_consensus_failure(self):
        """Test de vérification de consensus échoué"""
        values = [10.0, 20.0, 30.0, 40.0]  # Valeurs très dispersées
        
        consensus = self.aggregator.check_consensus(values)
        
        assert consensus == False
    
    def test_check_consensus_edge_cases(self):
        """Test des cas limites pour le consensus"""
        # Liste vide
        assert self.aggregator.check_consensus([]) == False
        
        # Une seule valeur
        assert self.aggregator.check_consensus([23.0]) == True
        
        # Valeurs autour de zéro
        assert self.aggregator.check_consensus([0.0, 0.1, -0.1]) == True
    
    def test_calculate_confidence(self):
        """Test de calcul du niveau de confiance"""
        # Valeurs très cohérentes
        high_confidence_values = [23.0, 23.0, 23.0, 23.0]
        confidence = self.aggregator.calculate_confidence(high_confidence_values)
        assert confidence > 0.9
        
        # Valeurs dispersées
        low_confidence_values = [20.0, 25.0, 30.0, 35.0]
        confidence = self.aggregator.calculate_confidence(low_confidence_values)
        assert confidence < 0.7
        
        # Une seule valeur
        single_value = [23.0]
        confidence = self.aggregator.calculate_confidence(single_value)
        assert confidence == 1.0
    
    def test_detect_malicious_nodes(self):
        """Test de détection de nœuds malveillants"""
        readings = [
            SensorReading(23.0, int(time.time()), "honest_node_1", "sig1"),
            SensorReading(23.1, int(time.time()), "honest_node_2", "sig2"),
            SensorReading(50.0, int(time.time()), "malicious_node", "sig3"),  # Valeur suspecte
            SensorReading(23.2, int(time.time()), "honest_node_3", "sig4"),
        ]
        
        malicious = self.aggregator.detect_malicious_nodes(readings)
        
        assert "malicious_node" in malicious
        assert len(malicious) == 1
    
    def test_detect_malicious_nodes_insufficient_data(self):
        """Test détection avec données insuffisantes"""
        readings = [
            SensorReading(23.0, int(time.time()), "node1", "sig1"),
            SensorReading(23.1, int(time.time()), "node2", "sig2"),
        ]
        
        malicious = self.aggregator.detect_malicious_nodes(readings)
        
        assert malicious == []  # Pas assez de données pour détecter

class TestConsensusScenarios:
    """Tests de scénarios de consensus complexes"""
    
    def setup_method(self):
        consensus_config = {
            'consensus_threshold': 0.8,
            'outlier_tolerance': 0.05,
            'min_nodes': 3
        }
        self.aggregator = DataAggregator(consensus_config)
    
    @pytest.mark.asyncio
    async def test_scenario_normal_operation(self):
        """Scénario: Fonctionnement normal avec 5 nœuds"""
        values = [22.8, 23.0, 23.1, 22.9, 23.2]
        readings = self.create_sensor_readings(values)
        
        result = await self.aggregator.aggregate_readings(readings)
        
        assert result['confidence'] > 0.8
        assert result['outliers_removed'] == 0
        assert 22.5 <= result['value'] <= 23.5
    
    @pytest.mark.asyncio
    async def test_scenario_one_faulty_sensor(self):
        """Scénario: Un capteur défaillant"""
        values = [23.0, 23.1, 45.0, 22.9, 23.2]  # Un capteur défaillant
        readings = self.create_sensor_readings(values)
        
        result = await self.aggregator.aggregate_readings(readings)
        
        assert result['outliers_removed'] == 1
        assert 22.5 <= result['value'] <= 23.5
    
    @pytest.mark.asyncio
    async def test_scenario_network_partition(self):
        """Scénario: Partition réseau avec seulement 3 nœuds"""
        values = [23.0, 23.1, 22.9]  # Minimum requis
        readings = self.create_sensor_readings(values)
        
        result = await self.aggregator.aggregate_readings(readings)
        
        assert result['nodes_participated'] == 3
        assert 22.5 <= result['value'] <= 23.5
    
    def create_sensor_readings(self, values, node_prefix="node"):
        """Helper pour créer des lectures de test"""
        readings = []
        timestamp = int(time.time())
        
        for i, value in enumerate(values):
            reading = SensorReading(
                value=value,
                timestamp=timestamp,
                node_id=f"{node_prefix}_{i+1}",
                signature=f"signature_{i+1:064d}"  # Signature de 64 caractères
            )
            readings.append(reading)
        
        return readings