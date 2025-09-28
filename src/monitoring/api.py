import asyncio
import json
import time
import psutil
from typing import Dict, Any

# Simulation d'une API de monitoring simple
class MonitoringAPI:
    """API de monitoring pour le nœud RODIO"""
    
    def __init__(self):
        self.start_time = time.time()
        self.metrics = {
            'requests_count': 0,
            'sensor_readings': 0,
            'successful_submissions': 0,
            'failed_submissions': 0,
            'consensus_success': 0,
            'consensus_failures': 0
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Endpoint de vérification de santé"""
        self.metrics['requests_count'] += 1
        
        uptime = time.time() - self.start_time
        
        return {
            "status": "healthy",
            "node_id": "RODIO_GATEWAY_001",
            "uptime_seconds": int(uptime),
            "uptime_human": self.format_uptime(uptime),
            "version": "1.0.0",
            "active_sensors": 3,
            "successful_submissions": self.metrics['successful_submissions'],
            "consensus_success_rate": self.calculate_success_rate(),
            "memory_usage": self.get_memory_usage(),
            "cpu_usage": self.get_cpu_usage(),
            "timestamp": int(time.time())
        }
    
    async def get_metrics(self) -> str:
        """Endpoint compatible Prometheus"""
        self.metrics['requests_count'] += 1
        
        uptime = time.time() - self.start_time
        success_rate = self.calculate_success_rate()
        
        prometheus_metrics = f"""# HELP rodio_node_health Node health status (1=healthy, 0=unhealthy)
# TYPE rodio_node_health gauge
rodio_node_health{{node_id="RODIO_GATEWAY_001"}} 1

# HELP rodio_uptime_seconds Node uptime in seconds
# TYPE rodio_uptime_seconds counter
rodio_uptime_seconds{{node_id="RODIO_GATEWAY_001"}} {int(uptime)}

# HELP rodio_sensor_readings_total Total number of sensor readings
# TYPE rodio_sensor_readings_total counter
rodio_sensor_readings_total{{node_id="RODIO_GATEWAY_001"}} {self.metrics['sensor_readings']}

# HELP rodio_submissions_total Total number of blockchain submissions
# TYPE rodio_submissions_total counter
rodio_submissions_total{{node_id="RODIO_GATEWAY_001",status="success"}} {self.metrics['successful_submissions']}
rodio_submissions_total{{node_id="RODIO_GATEWAY_001",status="failed"}} {self.metrics['failed_submissions']}

# HELP rodio_consensus_success_rate Consensus success rate (0-1)
# TYPE rodio_consensus_success_rate gauge
rodio_consensus_success_rate{{node_id="RODIO_GATEWAY_001"}} {success_rate}

# HELP rodio_memory_usage_bytes Memory usage in bytes
# TYPE rodio_memory_usage_bytes gauge
rodio_memory_usage_bytes{{node_id="RODIO_GATEWAY_001"}} {self.get_memory_usage()}

# HELP rodio_cpu_usage_percent CPU usage percentage
# TYPE rodio_cpu_usage_percent gauge
rodio_cpu_usage_percent{{node_id="RODIO_GATEWAY_001"}} {self.get_cpu_usage()}
"""
        
        return prometheus_metrics
    
    async def get_detailed_status(self) -> Dict[str, Any]:
        """Status détaillé du nœud"""
        self.metrics['requests_count'] += 1
        
        return {
            "node_info": {
                "node_id": "RODIO_GATEWAY_001",
                "version": "1.0.0",
                "network": "polygon",
                "start_time": self.start_time,
                "uptime": time.time() - self.start_time
            },
            "performance": {
                "cpu_usage": self.get_cpu_usage(),
                "memory_usage": self.get_memory_usage(),
                "disk_usage": self.get_disk_usage(),
                "network_io": self.get_network_io()
            },
            "blockchain": {
                "connected": True,
                "latest_block": 18500000 + int(time.time() % 1000),
                "successful_transactions": self.metrics['successful_submissions'],
                "failed_transactions": self.metrics['failed_submissions'],
                "pending_transactions": 0
            },
            "sensors": {
                "active_sensors": 3,
                "total_readings": self.metrics['sensor_readings'],
                "last_reading": int(time.time()) - 30,
                "sensor_types": ["temperature", "humidity", "gps"]
            },
            "consensus": {
                "success_count": self.metrics['consensus_success'],
                "failure_count": self.metrics['consensus_failures'],
                "success_rate": self.calculate_success_rate(),
                "peer_nodes": 3
            },
            "security": {
                "stake_status": "sufficient",
                "reputation_score": 0.95,
                "slash_events": 0,
                "last_security_check": int(time.time()) - 300
            }
        }
    
    def format_uptime(self, uptime_seconds: float) -> str:
        """Formate l'uptime en format lisible"""
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m {seconds}s"
        elif hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def calculate_success_rate(self) -> float:
        """Calcule le taux de succès du consensus"""
        total = self.metrics['consensus_success'] + self.metrics['consensus_failures']
        if total == 0:
            return 1.0
        return round(self.metrics['consensus_success'] / total, 3)
    
    def get_memory_usage(self) -> int:
        """Récupère l'usage mémoire"""
        try:
            process = psutil.Process()
            return process.memory_info().rss
        except:
            return 0
    
    def get_cpu_usage(self) -> float:
        """Récupère l'usage CPU"""
        try:
            return round(psutil.cpu_percent(interval=0.1), 1)
        except:
            return 0.0
    
    def get_disk_usage(self) -> Dict[str, Any]:
        """Récupère l'usage disque"""
        try:
            disk = psutil.disk_usage('/')
            return {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": round((disk.used / disk.total) * 100, 1)
            }
        except:
            return {"total": 0, "used": 0, "free": 0, "percent": 0}
    
    def get_network_io(self) -> Dict[str, Any]:
        """Récupère les stats réseau"""
        try:
            net_io = psutil.net_io_counters()
            return {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            }
        except:
            return {"bytes_sent": 0, "bytes_recv": 0, "packets_sent": 0, "packets_recv": 0}
    
    def increment_metric(self, metric_name: str):
        """Incrémente une métrique"""
        if metric_name in self.metrics:
            self.metrics[metric_name] += 1

# Instance globale de l'API
monitoring_api = MonitoringAPI()

async def start_monitoring_api(port: int = 8080):
    """Démarre l'API de monitoring"""
    import logging
    
    logging.info(f"🌐 Démarrage de l'API de monitoring sur le port {port}")
    
    # Simulation d'un serveur HTTP simple
    while True:
        try:
            # Simulation de requêtes périodiques
            await asyncio.sleep(10)
            
            # Mise à jour des métriques simulées
            monitoring_api.increment_metric('sensor_readings')
            
            if monitoring_api.metrics['sensor_readings'] % 3 == 0:
                monitoring_api.increment_metric('successful_submissions')
                monitoring_api.increment_metric('consensus_success')
            
            # Log périodique des métriques
            if monitoring_api.metrics['sensor_readings'] % 10 == 0:
                health = await monitoring_api.health_check()
                logging.info(f"📊 Métriques - Lectures: {health['successful_submissions']}, Uptime: {health['uptime_human']}")
            
        except Exception as e:
            logging.error(f"❌ Erreur API monitoring: {e}")
            await asyncio.sleep(5)

# Fonctions utilitaires pour les endpoints
async def handle_health_request():
    """Gestionnaire pour /health"""
    return await monitoring_api.health_check()

async def handle_metrics_request():
    """Gestionnaire pour /metrics"""
    return await monitoring_api.get_metrics()

async def handle_status_request():
    """Gestionnaire pour /status"""
    return await monitoring_api.get_detailed_status()