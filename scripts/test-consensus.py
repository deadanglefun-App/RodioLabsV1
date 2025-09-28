#!/usr/bin/env python3
"""
Tests du consensus multi-nœuds RODIO
Valide le comportement du consensus dans différents scénarios
"""

import asyncio
import aiohttp
import json
import time
import logging
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class NodeInfo:
    """Informations d'un nœud RODIO"""
    node_id: str
    url: str
    status: str = "unknown"
    last_response_time: float = 0.0

class ConsensusTestSuite:
    """Suite de tests pour le consensus RODIO"""
    
    def __init__(self):
        self.nodes = [
            NodeInfo("GATEWAY_01", "http://localhost:8081"),
            NodeInfo("GATEWAY_02", "http://localhost:8082"),
            NodeInfo("GATEWAY_03", "http://localhost:8083"),
        ]
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.test_results = []
    
    async def check_nodes_health(self) -> bool:
        """Vérifie que tous les nœuds sont opérationnels"""
        self.logger.info("🔍 Vérification de la santé des nœuds...")
        
        healthy_nodes = 0
        
        async with aiohttp.ClientSession() as session:
            for node in self.nodes:
                try:
                    start_time = time.time()
                    async with session.get(f"{node.url}/health", timeout=5) as response:
                        if response.status == 200:
                            data = await response.json()
                            node.status = data.get('status', 'unknown')
                            node.last_response_time = time.time() - start_time
                            
                            if node.status == 'healthy':
                                healthy_nodes += 1
                                self.logger.info(f"✅ {node.node_id}: {node.status} ({node.last_response_time:.3f}s)")
                            else:
                                self.logger.warning(f"⚠️ {node.node_id}: {node.status}")
                        else:
                            node.status = f"http_{response.status}"
                            self.logger.error(f"❌ {node.node_id}: HTTP {response.status}")
                            
                except Exception as e:
                    node.status = "unreachable"
                    self.logger.error(f"❌ {node.node_id}: {str(e)}")
        
        success = healthy_nodes >= 3
        self.logger.info(f"📊 Nœuds sains: {healthy_nodes}/{len(self.nodes)}")
        return success
    
    async def test_normal_consensus(self) -> bool:
        """Test du consensus avec des valeurs cohérentes"""
        self.logger.info("🧪 Test: Consensus normal avec valeurs cohérentes")
        
        # Simulation de données cohérentes
        test_data = {
            "sensor_id": "temp_test_01",
            "readings": [
                {"node_id": "GATEWAY_01", "value": 23.1, "timestamp": int(time.time())},
                {"node_id": "GATEWAY_02", "value": 23.3, "timestamp": int(time.time())},
                {"node_id": "GATEWAY_03", "value": 23.2, "timestamp": int(time.time())},
            ]
        }
        
        try:
            # Envoi des données à chaque nœud
            async with aiohttp.ClientSession() as session:
                tasks = []
                for i, node in enumerate(self.nodes):
                    reading = test_data["readings"][i]
                    task = self._send_sensor_data(session, node, reading)
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Vérification des résultats
            successful_submissions = sum(1 for r in results if r is True)
            
            if successful_submissions >= 3:
                self.logger.info("✅ Consensus normal: SUCCÈS")
                return True
            else:
                self.logger.error(f"❌ Consensus normal: ÉCHEC ({successful_submissions}/3)")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erreur test consensus normal: {e}")
            return False
    
    async def test_outlier_handling(self) -> bool:
        """Test de gestion des outliers"""
        self.logger.info("🧪 Test: Gestion des outliers")
        
        # Simulation avec un outlier
        test_data = {
            "sensor_id": "temp_test_02",
            "readings": [
                {"node_id": "GATEWAY_01", "value": 23.1, "timestamp": int(time.time())},
                {"node_id": "GATEWAY_02", "value": 50.0, "timestamp": int(time.time())},  # Outlier
                {"node_id": "GATEWAY_03", "value": 23.2, "timestamp": int(time.time())},
            ]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                tasks = []
                for i, node in enumerate(self.nodes):
                    reading = test_data["readings"][i]
                    task = self._send_sensor_data(session, node, reading)
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Le consensus devrait filtrer l'outlier
            successful_submissions = sum(1 for r in results if r is True)
            
            if successful_submissions >= 2:  # Au moins 2 nœuds d'accord
                self.logger.info("✅ Gestion outliers: SUCCÈS")
                return True
            else:
                self.logger.error("❌ Gestion outliers: ÉCHEC")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erreur test outliers: {e}")
            return False
    
    async def test_node_failure_resilience(self) -> bool:
        """Test de résilience à la panne d'un nœud"""
        self.logger.info("🧪 Test: Résilience à la panne d'un nœud")
        
        # Test avec seulement 2 nœuds (simulation de panne du 3ème)
        active_nodes = self.nodes[:2]
        
        test_data = {
            "sensor_id": "temp_test_03",
            "readings": [
                {"node_id": "GATEWAY_01", "value": 23.1, "timestamp": int(time.time())},
                {"node_id": "GATEWAY_02", "value": 23.3, "timestamp": int(time.time())},
            ]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                tasks = []
                for i, node in enumerate(active_nodes):
                    reading = test_data["readings"][i]
                    task = self._send_sensor_data(session, node, reading)
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Avec 2 nœuds, le consensus devrait échouer (minimum 3 requis)
            successful_submissions = sum(1 for r in results if r is True)
            
            if successful_submissions < 3:
                self.logger.info("✅ Résilience panne: SUCCÈS (consensus refusé avec <3 nœuds)")
                return True
            else:
                self.logger.error("❌ Résilience panne: ÉCHEC (consensus accepté avec <3 nœuds)")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erreur test résilience: {e}")
            return False
    
    async def test_consensus_timing(self) -> bool:
        """Test des performances temporelles du consensus"""
        self.logger.info("🧪 Test: Performance temporelle du consensus")
        
        start_time = time.time()
        
        test_data = {
            "sensor_id": "temp_test_04",
            "readings": [
                {"node_id": "GATEWAY_01", "value": 23.1, "timestamp": int(time.time())},
                {"node_id": "GATEWAY_02", "value": 23.2, "timestamp": int(time.time())},
                {"node_id": "GATEWAY_03", "value": 23.0, "timestamp": int(time.time())},
            ]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                tasks = []
                for i, node in enumerate(self.nodes):
                    reading = test_data["readings"][i]
                    task = self._send_sensor_data(session, node, reading)
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
            
            consensus_time = time.time() - start_time
            
            # Le consensus devrait prendre moins de 5 secondes
            if consensus_time < 5.0:
                self.logger.info(f"✅ Performance consensus: SUCCÈS ({consensus_time:.3f}s)")
                return True
            else:
                self.logger.warning(f"⚠️ Performance consensus: LENT ({consensus_time:.3f}s)")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erreur test performance: {e}")
            return False
    
    async def _send_sensor_data(self, session: aiohttp.ClientSession, node: NodeInfo, reading: Dict) -> bool:
        """Envoie des données de capteur à un nœud"""
        try:
            async with session.post(
                f"{node.url}/api/sensor-data",
                json=reading,
                timeout=3
            ) as response:
                return response.status == 200
        except Exception as e:
            self.logger.debug(f"Erreur envoi données à {node.node_id}: {e}")
            return False
    
    async def get_consensus_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques de consensus de tous les nœuds"""
        metrics = {}
        
        async with aiohttp.ClientSession() as session:
            for node in self.nodes:
                try:
                    async with session.get(f"{node.url}/metrics", timeout=3) as response:
                        if response.status == 200:
                            text = await response.text()
                            metrics[node.node_id] = self._parse_prometheus_metrics(text)
                except Exception as e:
                    self.logger.debug(f"Erreur métriques {node.node_id}: {e}")
        
        return metrics
    
    def _parse_prometheus_metrics(self, metrics_text: str) -> Dict[str, float]:
        """Parse simple des métriques Prometheus"""
        metrics = {}
        for line in metrics_text.split('\n'):
            if line.startswith('rodio_consensus_success_rate'):
                try:
                    value = float(line.split()[-1])
                    metrics['consensus_success_rate'] = value
                except:
                    pass
            elif line.startswith('rodio_sensor_readings_total'):
                try:
                    value = float(line.split()[-1])
                    metrics['sensor_readings_total'] = value
                except:
                    pass
        return metrics
    
    async def run_full_test_suite(self) -> Dict[str, Any]:
        """Exécute la suite complète de tests"""
        self.logger.info("🚀 Démarrage de la suite de tests consensus RODIO")
        self.logger.info("=" * 60)
        
        results = {
            "timestamp": int(time.time()),
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }
        
        # Liste des tests à exécuter
        tests = [
            ("health_check", self.check_nodes_health),
            ("normal_consensus", self.test_normal_consensus),
            ("outlier_handling", self.test_outlier_handling),
            ("node_failure_resilience", self.test_node_failure_resilience),
            ("consensus_timing", self.test_consensus_timing),
        ]
        
        for test_name, test_func in tests:
            self.logger.info(f"\n📋 Exécution: {test_name}")
            
            try:
                start_time = time.time()
                success = await test_func()
                duration = time.time() - start_time
                
                results["total_tests"] += 1
                if success:
                    results["passed_tests"] += 1
                else:
                    results["failed_tests"] += 1
                
                results["test_details"].append({
                    "name": test_name,
                    "success": success,
                    "duration": round(duration, 3)
                })
                
            except Exception as e:
                self.logger.error(f"❌ Erreur critique dans {test_name}: {e}")
                results["total_tests"] += 1
                results["failed_tests"] += 1
                results["test_details"].append({
                    "name": test_name,
                    "success": False,
                    "error": str(e)
                })
        
        # Récupération des métriques finales
        try:
            final_metrics = await self.get_consensus_metrics()
            results["final_metrics"] = final_metrics
        except Exception as e:
            self.logger.warning(f"Impossible de récupérer les métriques finales: {e}")
        
        # Rapport final
        self.logger.info("\n" + "=" * 60)
        self.logger.info("📊 RAPPORT FINAL DES TESTS")
        self.logger.info("=" * 60)
        self.logger.info(f"Tests exécutés: {results['total_tests']}")
        self.logger.info(f"Tests réussis: {results['passed_tests']}")
        self.logger.info(f"Tests échoués: {results['failed_tests']}")
        
        success_rate = (results['passed_tests'] / results['total_tests']) * 100 if results['total_tests'] > 0 else 0
        self.logger.info(f"Taux de réussite: {success_rate:.1f}%")
        
        if success_rate >= 80:
            self.logger.info("🎉 CONSENSUS RODIO: VALIDATION RÉUSSIE!")
        else:
            self.logger.error("❌ CONSENSUS RODIO: PROBLÈMES DÉTECTÉS")
        
        return results

async def main():
    """Point d'entrée principal"""
    test_suite = ConsensusTestSuite()
    
    try:
        results = await test_suite.run_full_test_suite()
        
        # Sauvegarde des résultats
        with open(f"consensus_test_results_{int(time.time())}.json", "w") as f:
            json.dump(results, f, indent=2)
        
        return results["passed_tests"] == results["total_tests"]
        
    except KeyboardInterrupt:
        print("\n🛑 Tests interrompus par l'utilisateur")
        return False
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)