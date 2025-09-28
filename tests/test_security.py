import pytest
import time
from unittest.mock import Mock, AsyncMock, patch
from src.security.staking import StakingManager
from src.security.reputation import ReputationSystem

class TestStakingManager:
    """Tests pour le gestionnaire de staking"""
    
    def setup_method(self):
        self.mock_web3 = Mock()
        self.mock_web3.get_account_address.return_value = "0x1234567890123456789012345678901234567890"
        
        staking_config = {
            'min_stake': '1000000000000000000000',  # 1000 tokens
            'staking_contract': '0x9876543210987654321098765432109876543210'
        }
        
        self.staking_manager = StakingManager(self.mock_web3, staking_config)
    
    @pytest.mark.asyncio
    async def test_check_stake_sufficient(self):
        """Test vérification stake suffisant"""
        # Mock du stake suffisant
        with patch.object(self.staking_manager, 'get_node_stake', return_value=2000000000000000000000):
            result = await self.staking_manager.check_stake()
            assert result == True
    
    @pytest.mark.asyncio
    async def test_check_stake_insufficient(self):
        """Test vérification stake insuffisant"""
        # Mock du stake insuffisant
        with patch.object(self.staking_manager, 'get_node_stake', return_value=500000000000000000000):
            result = await self.staking_manager.check_stake()
            assert result == False
    
    @pytest.mark.asyncio
    async def test_slash_node_with_consensus(self):
        """Test pénalisation avec consensus"""
        malicious_node = "0xmalicious"
        amount = 100000000000000000000  # 100 tokens
        reason = "data_manipulation"
        
        # Mock consensus positif
        with patch.object(self.staking_manager, 'is_consensus_slashing', return_value=True), \
             patch.object(self.staking_manager, 'get_node_stake', return_value=1000000000000000000000), \
             patch.object(self.mock_web3, 'send_transaction', return_value="0xtxhash"):
            
            result = await self.staking_manager.slash_node(malicious_node, amount, reason)
            
            assert result == True
            assert len(self.staking_manager.slash_events) == 1
            assert self.staking_manager.slash_events[0]['node_address'] == malicious_node
    
    @pytest.mark.asyncio
    async def test_slash_node_no_consensus(self):
        """Test pénalisation sans consensus"""
        malicious_node = "0xmalicious"
        amount = 100000000000000000000
        reason = "suspicious_behavior"
        
        # Mock consensus négatif
        with patch.object(self.staking_manager, 'is_consensus_slashing', return_value=False):
            result = await self.staking_manager.slash_node(malicious_node, amount, reason)
            
            assert result == False
            assert len(self.staking_manager.slash_events) == 0
    
    @pytest.mark.asyncio
    async def test_increase_stake(self):
        """Test augmentation du stake"""
        amount = 500000000000000000000  # 500 tokens
        
        with patch.object(self.mock_web3, 'send_transaction', return_value="0xtxhash"):
            tx_hash = await self.staking_manager.increase_stake(amount)
            
            assert tx_hash == "0xtxhash"
            assert len(self.staking_manager.stake_history) == 1
            assert self.staking_manager.stake_history[0]['action'] == 'increase'
    
    @pytest.mark.asyncio
    async def test_withdraw_stake_sufficient(self):
        """Test retrait de stake avec solde suffisant"""
        amount = 100000000000000000000  # 100 tokens
        
        with patch.object(self.staking_manager, 'get_node_stake', return_value=2000000000000000000000), \
             patch.object(self.mock_web3, 'send_transaction', return_value="0xtxhash"):
            
            tx_hash = await self.staking_manager.withdraw_stake(amount)
            
            assert tx_hash == "0xtxhash"
            assert len(self.staking_manager.stake_history) == 1
            assert self.staking_manager.stake_history[0]['action'] == 'withdraw'
    
    @pytest.mark.asyncio
    async def test_withdraw_stake_insufficient(self):
        """Test retrait de stake avec solde insuffisant"""
        amount = 1500000000000000000000  # 1500 tokens (trop)
        
        with patch.object(self.staking_manager, 'get_node_stake', return_value=2000000000000000000000):
            with pytest.raises(ValueError, match="stake résiduel insuffisant"):
                await self.staking_manager.withdraw_stake(amount)
    
    def test_update_reputation_score(self):
        """Test mise à jour du score de réputation"""
        node_address = "0xnode123"
        
        # Score initial
        initial_score = self.staking_manager.get_reputation_score(node_address)
        assert initial_score == 1.0
        
        # Mise à jour négative
        self.staking_manager.update_reputation_score(node_address, -0.2)
        new_score = self.staking_manager.get_reputation_score(node_address)
        assert new_score == 0.8
        
        # Mise à jour positive
        self.staking_manager.update_reputation_score(node_address, 0.1)
        final_score = self.staking_manager.get_reputation_score(node_address)
        assert final_score == 0.9
    
    def test_get_security_metrics(self):
        """Test récupération des métriques de sécurité"""
        # Ajout de quelques événements de test
        self.staking_manager.slash_events.append({
            'node_address': '0xtest',
            'amount': 100,
            'reason': 'test',
            'timestamp': int(time.time())
        })
        
        metrics = self.staking_manager.get_security_metrics()
        
        assert 'min_stake_required' in metrics
        assert 'slash_events_count' in metrics
        assert 'nodes_with_reputation' in metrics
        assert metrics['slash_events_count'] == 1

class TestReputationSystem:
    """Tests pour le système de réputation"""
    
    def setup_method(self):
        self.reputation_system = ReputationSystem()
    
    def test_get_reputation_new_node(self):
        """Test récupération réputation nouveau nœud"""
        node_id = "new_node_001"
        reputation = self.reputation_system.get_reputation(node_id)
        
        assert reputation == 0.8  # Réputation par défaut
        assert node_id in self.reputation_system.node_reputations
    
    def test_update_reputation_positive(self):
        """Test mise à jour réputation positive"""
        node_id = "test_node"
        initial_rep = self.reputation_system.get_reputation(node_id)
        
        self.reputation_system.update_reputation(node_id, 'consensus_success')
        
        new_rep = self.reputation_system.get_reputation(node_id)
        assert new_rep > initial_rep
    
    def test_update_reputation_negative(self):
        """Test mise à jour réputation négative"""
        node_id = "test_node"
        initial_rep = self.reputation_system.get_reputation(node_id)
        
        self.reputation_system.update_reputation(node_id, 'consensus_failure')
        
        new_rep = self.reputation_system.get_reputation(node_id)
        assert new_rep < initial_rep
    
    def test_update_reputation_bounds(self):
        """Test limites de réputation"""
        node_id = "test_node"
        
        # Test limite supérieure
        for _ in range(10):
            self.reputation_system.update_reputation(node_id, 'stake_increase')
        
        reputation = self.reputation_system.get_reputation(node_id)
        assert reputation <= 1.0
        
        # Test limite inférieure
        for _ in range(20):
            self.reputation_system.update_reputation(node_id, 'malicious_behavior')
        
        reputation = self.reputation_system.get_reputation(node_id)
        assert reputation >= 0.0
    
    def test_get_trusted_nodes(self):
        """Test récupération nœuds de confiance"""
        # Création de nœuds avec différentes réputations
        self.reputation_system.node_reputations = {
            'trusted_node_1': 0.9,
            'trusted_node_2': 0.8,
            'average_node': 0.6,
            'suspicious_node': 0.3
        }
        
        trusted = self.reputation_system.get_trusted_nodes(min_reputation=0.7)
        
        assert len(trusted) == 2
        assert 'trusted_node_1' in trusted
        assert 'trusted_node_2' in trusted
        assert 'suspicious_node' not in trusted
    
    def test_get_suspicious_nodes(self):
        """Test récupération nœuds suspects"""
        self.reputation_system.node_reputations = {
            'trusted_node': 0.9,
            'average_node': 0.6,
            'suspicious_node_1': 0.2,
            'suspicious_node_2': 0.1
        }
        
        suspicious = self.reputation_system.get_suspicious_nodes(max_reputation=0.3)
        
        assert len(suspicious) == 2
        assert 'suspicious_node_1' in suspicious
        assert 'suspicious_node_2' in suspicious
        assert 'trusted_node' not in suspicious
    
    def test_calculate_consensus_weight(self):
        """Test calcul poids consensus"""
        node_id = "test_node"
        
        # Réputation élevée
        self.reputation_system.node_reputations[node_id] = 0.9
        weight = self.reputation_system.calculate_consensus_weight(node_id)
        assert weight == 1.0
        
        # Réputation moyenne
        self.reputation_system.node_reputations[node_id] = 0.6
        weight = self.reputation_system.calculate_consensus_weight(node_id)
        assert weight == 0.8
        
        # Réputation faible
        self.reputation_system.node_reputations[node_id] = 0.1
        weight = self.reputation_system.calculate_consensus_weight(node_id)
        assert weight == 0.1
    
    def test_get_reputation_history(self):
        """Test historique de réputation"""
        node_id = "test_node"
        
        # Ajout d'événements
        self.reputation_system.update_reputation(node_id, 'consensus_success')
        self.reputation_system.update_reputation(node_id, 'data_quality_high')
        
        history = self.reputation_system.get_reputation_history(node_id, days=7)
        
        assert len(history) == 2
        assert all(event.node_id == node_id for event in history)
        assert history[0].timestamp >= history[1].timestamp  # Ordre décroissant
    
    def test_generate_reputation_report(self):
        """Test génération rapport de réputation"""
        # Ajout de données de test
        self.reputation_system.node_reputations = {
            'excellent_node': 0.95,
            'good_node': 0.8,
            'average_node': 0.6,
            'poor_node': 0.4,
            'very_poor_node': 0.2
        }
        
        report = self.reputation_system.generate_reputation_report()
        
        assert 'total_nodes' in report
        assert 'average_reputation' in report
        assert 'reputation_distribution' in report
        assert 'top_nodes' in report
        assert 'bottom_nodes' in report
        
        assert report['total_nodes'] == 5
        assert report['reputation_distribution']['excellent'] == 1
        assert report['reputation_distribution']['good'] == 1
    
    def test_cleanup_old_events(self):
        """Test nettoyage anciens événements"""
        node_id = "test_node"
        
        # Ajout d'événements récents et anciens
        self.reputation_system.update_reputation(node_id, 'consensus_success')
        
        # Simulation d'événement ancien
        old_event = self.reputation_system.reputation_events[0]
        old_event.timestamp = int(time.time()) - (40 * 24 * 3600)  # 40 jours
        
        initial_count = len(self.reputation_system.reputation_events)
        self.reputation_system.cleanup_old_events(days_to_keep=30)
        final_count = len(self.reputation_system.reputation_events)
        
        assert final_count < initial_count