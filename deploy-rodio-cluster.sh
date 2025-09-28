#!/bin/bash

# Script de déploiement d'un cluster de nœuds RODIO
# Usage: ./deploy-rodio-cluster.sh

set -e

echo "🚀 Déploiement du cluster RODIO Oracle Network"
echo "=============================================="

# Configuration
NODES=("gateway-1" "gateway-2" "gateway-3" "gateway-4")
CONFIG_DIR="./configs"
NETWORK_NAME="rodio-network"
IMAGE_NAME="rodio-node"
IMAGE_TAG="latest"

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérification des prérequis
check_prerequisites() {
    log_info "Vérification des prérequis..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker n'est pas installé"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_warning "Docker Compose n'est pas installé (optionnel)"
    fi
    
    log_success "Prérequis vérifiés"
}

# Création du réseau Docker
create_network() {
    log_info "Création du réseau Docker..."
    
    if docker network ls | grep -q $NETWORK_NAME; then
        log_warning "Le réseau $NETWORK_NAME existe déjà"
    else
        docker network create $NETWORK_NAME
        log_success "Réseau $NETWORK_NAME créé"
    fi
}

# Construction de l'image Docker
build_image() {
    log_info "Construction de l'image Docker..."
    
    docker build -t $IMAGE_NAME:$IMAGE_TAG .
    
    if [ $? -eq 0 ]; then
        log_success "Image $IMAGE_NAME:$IMAGE_TAG construite avec succès"
    else
        log_error "Échec de la construction de l'image"
        exit 1
    fi
}

# Préparation des configurations
prepare_configs() {
    log_info "Préparation des configurations..."
    
    mkdir -p $CONFIG_DIR
    
    for i in "${!NODES[@]}"; do
        node=${NODES[$i]}
        port=$((8080 + i))
        
        # Copie et personnalisation de la configuration
        cp config/config.json $CONFIG_DIR/$node-config.json
        
        # Remplacement des placeholders
        sed -i "s/RODIO_GATEWAY_001/RODIO_$node/g" $CONFIG_DIR/$node-config.json
        sed -i "s/8080/$port/g" $CONFIG_DIR/$node-config.json
        
        log_success "Configuration préparée pour $node (port $port)"
    done
}

# Déploiement des nœuds
deploy_nodes() {
    log_info "Déploiement des nœuds..."
    
    for i in "${!NODES[@]}"; do
        node=${NODES[$i]}
        port=$((8080 + i))
        
        log_info "Déploiement de $node..."
        
        # Arrêt du conteneur existant s'il existe
        if docker ps -a | grep -q "rodio-$node"; then
            log_warning "Arrêt du conteneur existant rodio-$node"
            docker stop rodio-$node || true
            docker rm rodio-$node || true
        fi
        
        # Déploiement du nouveau conteneur
        docker run -d \
            --name rodio-$node \
            --network $NETWORK_NAME \
            -v $(pwd)/$CONFIG_DIR/$node-config.json:/app/config/config.json:ro \
            -p $port:8080 \
            --restart unless-stopped \
            --memory="512m" \
            --cpus="0.5" \
            -e RODIO_NODE_ID=$node \
            -e RODIO_PORT=$port \
            $IMAGE_NAME:$IMAGE_TAG
        
        if [ $? -eq 0 ]; then
            log_success "Nœud $node déployé sur le port $port"
        else
            log_error "Échec du déploiement de $node"
            exit 1
        fi
        
        # Attente que le nœud soit prêt
        log_info "Attente que $node soit prêt..."
        for attempt in {1..30}; do
            if curl -s http://localhost:$port/health > /dev/null 2>&1; then
                log_success "$node est prêt"
                break
            fi
            
            if [ $attempt -eq 30 ]; then
                log_error "$node n'est pas prêt après 30 tentatives"
                exit 1
            fi
            
            sleep 2
        done
    done
}

# Vérification du déploiement
verify_deployment() {
    log_info "Vérification du déploiement..."
    
    echo ""
    echo "📊 État du cluster RODIO:"
    echo "========================"
    
    for i in "${!NODES[@]}"; do
        node=${NODES[$i]}
        port=$((8080 + i))
        
        if curl -s http://localhost:$port/health > /dev/null 2>&1; then
            health_data=$(curl -s http://localhost:$port/health)
            status=$(echo $health_data | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null || echo "unknown")
            uptime=$(echo $health_data | python3 -c "import sys, json; print(json.load(sys.stdin)['uptime_human'])" 2>/dev/null || echo "unknown")
            
            echo -e "✅ $node: ${GREEN}$status${NC} (uptime: $uptime) - http://localhost:$port"
        else
            echo -e "❌ $node: ${RED}unreachable${NC} - http://localhost:$port"
        fi
    done
    
    echo ""
    log_success "Cluster RODIO déployé avec ${#NODES[@]} nœuds"
}

# Génération du docker-compose.yml
generate_docker_compose() {
    log_info "Génération du fichier docker-compose.yml..."
    
    cat > docker-compose.yml << EOF
version: '3.8'

services:
EOF

    for i in "${!NODES[@]}"; do
        node=${NODES[$i]}
        port=$((8080 + i))
        
        cat >> docker-compose.yml << EOF
  rodio-$node:
    build: .
    container_name: rodio-$node
    ports:
      - "$port:8080"
    volumes:
      - ./configs/$node-config.json:/app/config/config.json:ro
    environment:
      - RODIO_NODE_ID=$node
      - RODIO_PORT=$port
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
    networks:
      - rodio-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

EOF
    done
    
    cat >> docker-compose.yml << EOF
networks:
  rodio-network:
    driver: bridge

volumes:
  rodio-data:
EOF

    log_success "Fichier docker-compose.yml généré"
}

# Affichage des informations de monitoring
show_monitoring_info() {
    echo ""
    echo "📈 Monitoring et métriques:"
    echo "=========================="
    
    for i in "${!NODES[@]}"; do
        node=${NODES[$i]}
        port=$((8080 + i))
        
        echo "🔍 $node:"
        echo "   - Health: http://localhost:$port/health"
        echo "   - Metrics: http://localhost:$port/metrics"
        echo "   - Status: http://localhost:$port/status"
    done
    
    echo ""
    echo "🐳 Commandes Docker utiles:"
    echo "=========================="
    echo "docker ps                              # Voir les conteneurs"
    echo "docker logs rodio-gateway-1            # Voir les logs d'un nœud"
    echo "docker stop \$(docker ps -q --filter name=rodio)  # Arrêter tous les nœuds"
    echo "docker-compose up -d                   # Démarrer avec docker-compose"
    echo "docker-compose down                    # Arrêter avec docker-compose"
}

# Fonction de nettoyage
cleanup() {
    log_info "Nettoyage en cas d'erreur..."
    
    for node in "${NODES[@]}"; do
        docker stop rodio-$node 2>/dev/null || true
        docker rm rodio-$node 2>/dev/null || true
    done
}

# Gestion des signaux pour nettoyage
trap cleanup EXIT

# Fonction principale
main() {
    echo "🌟 RODIO Oracle Network - Cluster Deployment"
    echo "============================================="
    echo ""
    
    check_prerequisites
    create_network
    build_image
    prepare_configs
    deploy_nodes
    verify_deployment
    generate_docker_compose
    show_monitoring_info
    
    echo ""
    log_success "🎉 Déploiement terminé avec succès!"
    echo ""
    echo "Le cluster RODIO est maintenant opérationnel avec ${#NODES[@]} nœuds."
    echo "Consultez les URLs ci-dessus pour surveiller l'état du réseau."
}

# Exécution du script principal
main "$@"