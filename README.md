# 🌐 RODIO - Réseau d'Oracles Décentralisés pour l'IoT

**Connectez vos capteurs IoT à la blockchain Polygon avec un réseau d'oracles décentralisé, sécurisé et haute performance.**

<div align="center">

![RODIO Logo](https://images.pexels.com/photos/373543/pexels-photo-373543.jpeg?auto=compress&cs=tinysrgb&w=800&h=200&fit=crop)

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)](https://python.org)
[![Polygon](https://img.shields.io/badge/Blockchain-Polygon-purple.svg)](https://polygon.technology)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)

</div>

---

## 📖 Table des Matières

- [🌟 Fonctionnalités](#-fonctionnalités)
- [🏗️ Architecture](#️-architecture)
- [🚀 Démarrage Rapide](#-démarrage-rapide)
- [🔧 Configuration](#-configuration)
- [🐳 Déploiement Docker](#-déploiement-docker)
- [🧪 Tests et Développement](#-tests-et-développement)
- [📊 Monitoring](#-monitoring)
- [🤝 Contribution](#-contribution)
- [📄 Licence](#-licence)

---

## 🌟 Fonctionnalités

### 🔗 **Connectivité Universelle**
- ✅ Support MQTT, HTTP, WebSocket pour capteurs IoT
- ✅ Adaptateurs pour température, humidité, GPS, énergie
- ✅ Formatage automatique des données pour blockchain

### 🛡️ **Sécurité Enterprise**
- ✅ Consensus multi-nœuds avec preuve de stake
- ✅ Détection et pénalisation des nœuds malhonnêtes
- ✅ Chiffrement end-to-end des données

### 📈 **Haute Performance**
- ✅ Architecture asynchrone avec asyncio
- ✅ Agrégation intelligente des données
- ✅ Scalabilité horizontale automatique

### 🔍 **Transparence Totale**
- ✅ Toutes les données vérifiables sur blockchain
- ✅ Dashboard de monitoring temps réel
- ✅ Métriques Prometheus complètes

---

## 🏗️ Architecture

```
rodio-node/
├── src/
│   ├── core/                # Cœur du système
│   │   ├── node.py         # Nœud principal
│   │   └── aggregator.py   # Agrégation consensus
│   ├── adapters/           # Connecteurs capteurs
│   │   ├── temperature.py
│   │   ├── gps.py
│   │   └── humidity.py
│   ├── blockchain/         # Intégration Web3
│   │   ├── web3_client.py
│   │   └── contract_handler.py
│   ├── security/           # Sécurité et staking
│   │   ├── staking.py
│   │   └── reputation.py
│   └── monitoring/         # Monitoring et métriques
│       ├── api.py
│       └── metrics.py
├── configs/                # Fichiers de configuration
├── tests/                  # Suite de tests
└── docker/                 # Configuration Docker
```

---

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.9+
- Docker et Docker Compose
- Accès à un nœud Polygon (testnet ou mainnet)

### Installation en 5 minutes

```bash
# 1. Cloner le dépôt
git clone https://github.com/rodio-iot/node.git
cd rodio-node

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configuration
cp config/config.json config/my-config.json
# Éditer my-config.json avec vos paramètres

# 4. Lancer le nœud
python main.py
```

### Configuration Minimaliste

```json
{
  "node_id": "MON_NOEUD_001",
  "network": {
    "blockchain_rpc": "https://rpc-mumbai.maticvigil.com",
    "contract_address": "0x...",
    "private_key": "0x..."
  },
  "sensors": {
    "temperature": {
      "adapter": "TemperatureAdapter",
      "mqtt_topic": "sensors/temperature"
    }
  }
}
```

---

## 🔧 Configuration Avancée

### Types de Nœuds

| Type | Rôle | Ressources Requises |
|------|------|-------------------|
| Gateway | Collecte données capteurs | 1 CPU, 2GB RAM |
| Aggregator | Agrège et valide données | 2 CPU, 4GB RAM |
| Validator | Consensus final | 2 CPU, 4GB RAM + Stake |

### Exemple Configuration Complète

```json
{
  "node_id": "GATEWAY_EU_WEST_001",
  "network": {
    "blockchain_rpc": "https://polygon-rpc.com",
    "contract_address": "0x1234567890123456789012345678901234567890"
  },
  "sensors": {
    "temperature": {
      "adapter": "TemperatureAdapter",
      "mqtt_topic": "sensors/temperature",
      "polling_interval": 30
    },
    "humidity": {
      "adapter": "HumidityAdapter",
      "mqtt_topic": "sensors/humidity",
      "polling_interval": 30
    },
    "gps": {
      "adapter": "GPSAdapter",
      "mqtt_topic": "sensors/gps",
      "polling_interval": 60
    }
  },
  "consensus": {
    "min_nodes": 3,
    "consensus_threshold": 0.8,
    "outlier_tolerance": 0.05
  },
  "peer_nodes": [
    "http://gateway-2:8080",
    "http://gateway-3:8080"
  ]
}
```

---

## 🐳 Déploiement Docker

### Déploiement Single Node

```bash
# Build l'image
docker build -t rodio-node .

# Lancer le container
docker run -d \
  --name rodio-node \
  -v $(pwd)/config:/app/config \
  -p 8080:8080 \
  rodio-node:latest
```

### Cluster Multi-Nœuds

```bash
# Lancer un cluster de test
docker-compose -f docker-compose.test.yml up -d

# Scale horizontal
docker-compose up -d --scale rodio-node=5
```

### Docker Compose Example

```yaml
version: '3.8'
services:
  rodio-node:
    build: .
    environment:
      - NODE_ID=GATEWAY_${HOSTNAME}
      - LOG_LEVEL=INFO
    volumes:
      - ./config:/app/config
    ports:
      - "8080:8080"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## 🧪 Tests et Développement

### Suite de Tests Complète

```bash
# Tests unitaires
pytest tests/unit -v

# Tests d'intégration
pytest tests/integration -v

# Tests de consensus
python scripts/test-consensus.py

# Tests de performance
python scripts/load-test.py
```

### Environnement de Développement

```bash
# Setup environnement dev
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

pip install -r requirements.txt

# Lancer en mode dev
python main.py
```

### Simulation Multi-Nœuds

```bash
# Lancer un cluster local de test
docker-compose -f docker-compose.test.yml up -d

# Simuler des capteurs
python scripts/simulate-sensors.py

# Tester le consensus
python scripts/test-consensus.py
```

---

## 📊 Monitoring

### Métriques Disponibles

- `rodio_node_health` - Santé du nœud (1 = healthy)
- `rodio_sensor_readings_total` - Total des lectures
- `rodio_consensus_success_rate` - Taux de succès consensus
- `rodio_transactions_success` - Transactions blockchain réussies
- `rodio_peers_connected` - Nœuds pairs connectés

### API de Monitoring

```bash
# Santé du nœud
curl http://localhost:8080/health

# Métriques Prometheus
curl http://localhost:8080/metrics

# Statut détaillé
curl http://localhost:8080/status
```

### Exemple de Réponse Health Check

```json
{
  "status": "healthy",
  "node_id": "RODIO_GATEWAY_001",
  "uptime_seconds": 3600,
  "uptime_human": "1h 0m 0s",
  "version": "1.0.0",
  "active_sensors": 3,
  "successful_submissions": 1500,
  "consensus_success_rate": 0.98,
  "memory_usage": 134217728,
  "cpu_usage": 15.2,
  "timestamp": 1705320000
}
```

---

## 🤝 Contribution

Nous adorons les contributions ! Voici comment aider:

### Rapporter un Bug

1. Vérifier les issues existantes
2. Créer une nouvelle issue avec le template bug report

### Proposer une Fonctionnalité

1. Utiliser le feature request template
2. Discuter avec la communauté

### Processus de Développement

```bash
# 1. Fork le projet
# 2. Créer une branche feature
git checkout -b feature/ma-nouvelle-fonctionnalite

# 3. Commiter les changements
git commit -m "feat: ajout nouvelle fonctionnalité"

# 4. Push la branche
git push origin feature/ma-nouvelle-fonctionnalite

# 5. Ouvrir une Pull Request
```

### Standards de Code

- Suivre PEP 8 pour Python
- Tests requis pour nouvelles fonctionnalités
- Documentation mise à jour

---

## 📄 Licence

Ce projet est sous licence Apache 2.0. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🔗 Liens Utiles

- [📚 Documentation](https://docs.rodio.io) - Documentation complète
- [💬 Discord](https://discord.gg/rodio) - Communauté et support
- [🌐 Site Web](https://rodio.io) - Site officiel
- [🔗 Polygon](https://polygon.technology) - Blockchain supportée

---

## 🆘 Support

- 🐛 **Bugs**: [GitHub Issues](https://github.com/rodio-iot/node/issues)
- 💬 **Discussions**: [Discord Community](https://discord.gg/rodio)
- 📧 **Email**: support@rodio.io
- 🔐 **Sécurité**: security@rodio.io

---

<div align="center">

## ✨ Fait avec ❤️ par l'équipe RODIO ✨

**Connectant le monde physique à la blockchain, une donnée à la fois.**

![IoT to Blockchain](https://images.pexels.com/photos/159304/network-cable-ethernet-computer-159304.jpeg?auto=compress&cs=tinysrgb&w=600&h=200&fit=crop)

</div>