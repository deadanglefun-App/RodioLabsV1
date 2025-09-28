#!/usr/bin/env python3
"""
Script de configuration de l'environnement de test RODIO
Prépare les configurations et lance l'environnement de test
"""

import os
import json
import shutil
import subprocess
import sys
from pathlib import Path

class TestEnvironmentSetup:
    """Configuration de l'environnement de test"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_configs_dir = self.project_root / "test-configs"
        self.logs_dir = self.project_root / "logs"
    
    def create_directories(self):
        """Crée les répertoires nécessaires"""
        print("📁 Création des répertoires...")
        
        directories = [
            self.test_configs_dir,
            self.logs_dir,
            self.project_root / "data",
            self.project_root / "monitoring"
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
            print(f"   ✅ {directory}")
    
    def generate_test_configs(self):
        """Génère les configurations de test pour chaque nœud"""
        print("⚙️ Génération des configurations de test...")
        
        base_config = {
            "node": {
                "type": "gateway",
                "region": "test-local"
            },
            "network": {
                "blockchain_rpc": "http://ganache:8545",
                "chain_id": 1337,
                "contract_address": "0x1234567890123456789012345678901234567890",
                "private_key": "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"
            },
            "sensors": {
                "mqtt": {
                    "broker": "mqtt-broker",
                    "port": 1883,
                    "topics": ["sensors/+/data"]
                },
                "adapters": {
                    "temperature": {
                        "adapter": "TemperatureAdapter",
                        "mqtt_topic": "sensors/temperature",
                        "polling_interval": 10
                    },
                    "humidity": {
                        "adapter": "HumidityAdapter",
                        "mqtt_topic": "sensors/humidity",
                        "polling_interval": 10
                    },
                    "gps": {
                        "adapter": "GPSAdapter",
                        "mqtt_topic": "sensors/gps",
                        "polling_interval": 15
                    }
                }
            },
            "consensus": {
                "min_nodes": 3,
                "consensus_threshold": 0.8,
                "outlier_tolerance": 0.05,
                "timeout_seconds": 30
            },
            "monitoring": {
                "api_port": 8080,
                "metrics_enabled": True,
                "log_level": "DEBUG"
            }
        }
        
        # Configuration pour chaque nœud
        nodes = [
            {"id": "GATEWAY_01", "port": 8081},
            {"id": "GATEWAY_02", "port": 8082},
            {"id": "GATEWAY_03", "port": 8083}
        ]
        
        for i, node in enumerate(nodes):
            config = base_config.copy()
            config["node"]["id"] = node["id"]
            config["monitoring"]["api_port"] = node["port"]
            
            # Nœuds pairs (les autres nœuds)
            peer_nodes = [
                f"http://rodio-node-{j+1}:{nodes[j]['port']}"
                for j in range(len(nodes)) if j != i
            ]
            config["peer_nodes"] = peer_nodes
            
            # Sauvegarde de la configuration
            config_file = self.test_configs_dir / f"node{i+1}-config.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"   ✅ {config_file}")
    
    def create_docker_compose_override(self):
        """Crée un override pour docker-compose en mode test"""
        print("🐳 Création de l'override Docker Compose...")
        
        override_content = """version: '3.8'

services:
  # Override pour les tests
  rodio-node-1:
    environment:
      - LOG_LEVEL=DEBUG
      - TEST_MODE=true
    volumes:
      - ./logs:/app/logs
  
  rodio-node-2:
    environment:
      - LOG_LEVEL=DEBUG
      - TEST_MODE=true
    volumes:
      - ./logs:/app/logs
  
  rodio-node-3:
    environment:
      - LOG_LEVEL=DEBUG
      - TEST_MODE=true
    volumes:
      - ./logs:/app/logs
  
  # Ajout d'un simulateur de capteurs
  sensor-simulator:
    build:
      context: .
      dockerfile: docker/Dockerfile.simulator
    depends_on:
      - mqtt-broker
    environment:
      - MQTT_BROKER=mqtt-broker
      - SIMULATION_INTERVAL=5
      - OUTLIER_RATE=0.1
"""
        
        override_file = self.project_root / "docker-compose.override.yml"
        with open(override_file, 'w') as f:
            f.write(override_content)
        
        print(f"   ✅ {override_file}")
    
    def create_monitoring_config(self):
        """Crée la configuration de monitoring"""
        print("📊 Configuration du monitoring...")
        
        # Configuration Prometheus
        prometheus_config = """global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'rodio-nodes'
    static_configs:
      - targets: 
        - 'rodio-node-1:8081'
        - 'rodio-node-2:8082'
        - 'rodio-node-3:8083'
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
"""
        
        prometheus_file = self.project_root / "prometheus.yml"
        with open(prometheus_file, 'w') as f:
            f.write(prometheus_config)
        
        print(f"   ✅ {prometheus_file}")
    
    def create_test_scripts(self):
        """Crée les scripts de test"""
        print("🧪 Création des scripts de test...")
        
        # Script de lancement complet
        run_tests_script = """#!/bin/bash
set -e

echo "🚀 Lancement de l'environnement de test RODIO"
echo "=============================================="

# Nettoyage
echo "🧹 Nettoyage de l'environnement..."
docker-compose -f docker-compose.test.yml down -v 2>/dev/null || true

# Construction des images
echo "🔨 Construction des images Docker..."
docker-compose -f docker-compose.test.yml build

# Démarrage des services
echo "🚀 Démarrage des services..."
docker-compose -f docker-compose.test.yml up -d

# Attente que les services soient prêts
echo "⏳ Attente que les services soient prêts..."
sleep 30

# Vérification de la santé des nœuds
echo "🔍 Vérification de la santé des nœuds..."
for i in {1..3}; do
    port=$((8080 + i))
    echo "   Nœud $i (port $port):"
    curl -s http://localhost:$port/health | jq '.status' || echo "   ❌ Non accessible"
done

# Lancement des tests
echo "🧪 Lancement des tests de consensus..."
python3 scripts/test-consensus.py

# Lancement du simulateur de capteurs
echo "📡 Démarrage du simulateur de capteurs..."
python3 scripts/simulate-sensors.py &
SIMULATOR_PID=$!

# Attente et observation
echo "👀 Observation du consensus (30 secondes)..."
sleep 30

# Arrêt du simulateur
kill $SIMULATOR_PID 2>/dev/null || true

echo "✅ Tests terminés!"
echo "📊 Consultez les logs dans ./logs/"
echo "📈 Métriques disponibles sur http://localhost:9090"
"""
        
        run_tests_file = self.project_root / "run-tests.sh"
        with open(run_tests_file, 'w') as f:
            f.write(run_tests_script)
        
        # Rendre le script exécutable
        os.chmod(run_tests_file, 0o755)
        
        print(f"   ✅ {run_tests_file}")
    
    def check_dependencies(self):
        """Vérifie que les dépendances sont installées"""
        print("🔍 Vérification des dépendances...")
        
        dependencies = [
            ("docker", "Docker"),
            ("docker-compose", "Docker Compose"),
            ("python3", "Python 3"),
            ("curl", "cURL"),
            ("jq", "jq (JSON processor)")
        ]
        
        missing = []
        for cmd, name in dependencies:
            try:
                subprocess.run([cmd, "--version"], 
                             capture_output=True, check=True)
                print(f"   ✅ {name}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"   ❌ {name}")
                missing.append(name)
        
        if missing:
            print(f"\n⚠️ Dépendances manquantes: {', '.join(missing)}")
            print("   Installez-les avant de continuer.")
            return False
        
        return True
    
    def setup_complete_environment(self):
        """Configure l'environnement de test complet"""
        print("🌟 Configuration de l'environnement de test RODIO")
        print("=" * 50)
        
        if not self.check_dependencies():
            return False
        
        try:
            self.create_directories()
            self.generate_test_configs()
            self.create_docker_compose_override()
            self.create_monitoring_config()
            self.create_test_scripts()
            
            print("\n🎉 Environnement de test configuré avec succès!")
            print("\n📋 Prochaines étapes:")
            print("   1. ./run-tests.sh                    # Lancer tous les tests")
            print("   2. python3 scripts/test-consensus.py # Tests consensus uniquement")
            print("   3. python3 scripts/simulate-sensors.py # Simulateur capteurs")
            print("\n📊 Monitoring:")
            print("   - Prometheus: http://localhost:9090")
            print("   - Grafana: http://localhost:3000")
            print("   - Nœuds: http://localhost:8081-8083")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la configuration: {e}")
            return False

def main():
    """Point d'entrée principal"""
    setup = TestEnvironmentSetup()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--check-only":
        return setup.check_dependencies()
    
    success = setup.setup_complete_environment()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)