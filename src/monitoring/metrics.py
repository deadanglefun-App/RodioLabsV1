import time
import asyncio
import logging
from typing import Dict, List, Any
from dataclasses import dataclass, field
from collections import defaultdict, deque

@dataclass
class MetricPoint:
    """Point de métrique avec timestamp"""
    timestamp: int
    value: float
    labels: Dict[str, str] = field(default_factory=dict)

class MetricsCollector:
    """Collecteur de métriques pour le nœud RODIO"""
    
    def __init__(self, retention_hours: int = 24):
        self.retention_seconds = retention_hours * 3600
        self.metrics = defaultdict(lambda: deque(maxlen=10000))  # Limite par métrique
        
        # Métriques système
        self.system_metrics = {
            'cpu_usage': deque(maxlen=1000),
            'memory_usage': deque(maxlen=1000),
            'disk_usage': deque(maxlen=1000),
            'network_io': deque(maxlen=1000)
        }
        
        # Métriques métier
        self.business_metrics = {
            'sensor_readings_rate': deque(maxlen=1000),
            'consensus_success_rate': deque(maxlen=1000),
            'blockchain_latency': deque(maxlen=1000),
            'data_quality_score': deque(maxlen=1000)
        }
        
        # Compteurs
        self.counters = defaultdict(int)
        
        # Histogrammes (pour latences, etc.)
        self.histograms = defaultdict(list)
        
        logging.info("📈 MetricsCollector initialisé")
    
    def record_metric(self, name: str, value: float, labels: Dict[str, str] = None):
        """Enregistre une métrique"""
        metric_point = MetricPoint(
            timestamp=int(time.time()),
            value=value,
            labels=labels or {}
        )
        
        self.metrics[name].append(metric_point)
        self.cleanup_old_metrics()
    
    def increment_counter(self, name: str, value: int = 1, labels: Dict[str, str] = None):
        """Incrémente un compteur"""
        key = f"{name}_{self._labels_to_string(labels)}" if labels else name
        self.counters[key] += value
    
    def record_histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """Enregistre une valeur dans un histogramme"""
        key = f"{name}_{self._labels_to_string(labels)}" if labels else name
        self.histograms[key].append(value)
        
        # Garde seulement les 1000 dernières valeurs
        if len(self.histograms[key]) > 1000:
            self.histograms[key] = self.histograms[key][-1000:]
    
    def get_metric_summary(self, name: str, duration_minutes: int = 60) -> Dict[str, Any]:
        """Récupère un résumé d'une métrique sur une période"""
        cutoff_time = int(time.time()) - (duration_minutes * 60)
        
        if name not in self.metrics:
            return {"error": f"Métrique {name} non trouvée"}
        
        # Filtrage par période
        recent_points = [
            point for point in self.metrics[name]
            if point.timestamp >= cutoff_time
        ]
        
        if not recent_points:
            return {"error": "Aucune donnée récente"}
        
        values = [point.value for point in recent_points]
        
        return {
            "metric_name": name,
            "period_minutes": duration_minutes,
            "data_points": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1] if values else None,
            "first_timestamp": recent_points[0].timestamp,
            "last_timestamp": recent_points[-1].timestamp
        }
    
    def get_rate_metric(self, counter_name: str, duration_minutes: int = 5) -> float:
        """Calcule le taux d'une métrique (événements par minute)"""
        cutoff_time = int(time.time()) - (duration_minutes * 60)
        
        if counter_name not in self.metrics:
            return 0.0
        
        recent_points = [
            point for point in self.metrics[counter_name]
            if point.timestamp >= cutoff_time
        ]
        
        if len(recent_points) < 2:
            return 0.0
        
        # Calcul du taux basé sur les points de données
        time_span = recent_points[-1].timestamp - recent_points[0].timestamp
        if time_span == 0:
            return 0.0
        
        events_count = len(recent_points)
        rate_per_second = events_count / time_span
        rate_per_minute = rate_per_second * 60
        
        return round(rate_per_minute, 2)
    
    def get_percentile(self, histogram_name: str, percentile: float) -> float:
        """Calcule un percentile d'un histogramme"""
        if histogram_name not in self.histograms:
            return 0.0
        
        values = sorted(self.histograms[histogram_name])
        if not values:
            return 0.0
        
        index = int((percentile / 100.0) * len(values))
        index = min(index, len(values) - 1)
        
        return values[index]
    
    async def collect_system_metrics(self):
        """Collecte les métriques système en continu"""
        logging.info("🖥️ Démarrage de la collecte des métriques système")
        
        while True:
            try:
                import psutil
                
                # CPU
                cpu_percent = psutil.cpu_percent(interval=1)
                self.record_metric('system_cpu_usage', cpu_percent)
                
                # Mémoire
                memory = psutil.virtual_memory()
                self.record_metric('system_memory_usage', memory.percent)
                self.record_metric('system_memory_available', memory.available)
                
                # Disque
                disk = psutil.disk_usage('/')
                self.record_metric('system_disk_usage', disk.percent)
                
                # Réseau
                net_io = psutil.net_io_counters()
                self.record_metric('system_network_bytes_sent', net_io.bytes_sent)
                self.record_metric('system_network_bytes_recv', net_io.bytes_recv)
                
                await asyncio.sleep(30)  # Collecte toutes les 30 secondes
                
            except Exception as e:
                logging.error(f"❌ Erreur collecte métriques système: {e}")
                await asyncio.sleep(60)
    
    def record_sensor_reading(self, sensor_type: str, value: float, quality_score: float):
        """Enregistre une lecture de capteur"""
        labels = {"sensor_type": sensor_type}
        
        self.record_metric('sensor_reading_value', value, labels)
        self.record_metric('sensor_quality_score', quality_score, labels)
        self.increment_counter('sensor_readings_total', labels=labels)
    
    def record_consensus_event(self, success: bool, nodes_count: int, confidence: float):
        """Enregistre un événement de consensus"""
        self.increment_counter('consensus_attempts_total')
        
        if success:
            self.increment_counter('consensus_success_total')
            self.record_metric('consensus_confidence', confidence)
            self.record_metric('consensus_nodes_participated', nodes_count)
        else:
            self.increment_counter('consensus_failures_total')
    
    def record_blockchain_transaction(self, success: bool, latency_ms: float, gas_used: int):
        """Enregistre une transaction blockchain"""
        self.increment_counter('blockchain_transactions_total')
        
        if success:
            self.increment_counter('blockchain_transactions_success')
            self.record_histogram('blockchain_latency_ms', latency_ms)
            self.record_metric('blockchain_gas_used', gas_used)
        else:
            self.increment_counter('blockchain_transactions_failed')
    
    def cleanup_old_metrics(self):
        """Nettoie les anciennes métriques"""
        cutoff_time = int(time.time()) - self.retention_seconds
        
        for metric_name, points in self.metrics.items():
            # Supprime les points trop anciens
            while points and points[0].timestamp < cutoff_time:
                points.popleft()
    
    def _labels_to_string(self, labels: Dict[str, str]) -> str:
        """Convertit les labels en string pour les clés"""
        if not labels:
            return ""
        
        sorted_labels = sorted(labels.items())
        return "_".join([f"{k}={v}" for k, v in sorted_labels])
    
    def export_prometheus_metrics(self) -> str:
        """Exporte les métriques au format Prometheus"""
        lines = []
        
        # Compteurs
        for counter_name, value in self.counters.items():
            lines.append(f"# TYPE {counter_name} counter")
            lines.append(f"{counter_name} {value}")
        
        # Métriques récentes (dernière valeur)
        for metric_name, points in self.metrics.items():
            if points:
                latest_point = points[-1]
                lines.append(f"# TYPE {metric_name} gauge")
                
                if latest_point.labels:
                    labels_str = ",".join([f'{k}="{v}"' for k, v in latest_point.labels.items()])
                    lines.append(f"{metric_name}{{{labels_str}}} {latest_point.value}")
                else:
                    lines.append(f"{metric_name} {latest_point.value}")
        
        # Histogrammes (percentiles)
        for hist_name, values in self.histograms.items():
            if values:
                lines.append(f"# TYPE {hist_name} histogram")
                lines.append(f"{hist_name}_p50 {self.get_percentile(hist_name, 50)}")
                lines.append(f"{hist_name}_p95 {self.get_percentile(hist_name, 95)}")
                lines.append(f"{hist_name}_p99 {self.get_percentile(hist_name, 99)}")
        
        return "\n".join(lines)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Prépare les données pour un dashboard"""
        return {
            "overview": {
                "total_metrics": len(self.metrics),
                "total_counters": len(self.counters),
                "total_histograms": len(self.histograms),
                "retention_hours": self.retention_seconds / 3600
            },
            "recent_activity": {
                "sensor_readings_rate": self.get_rate_metric('sensor_readings_total'),
                "consensus_success_rate": self.calculate_success_rate(),
                "avg_blockchain_latency": self.get_percentile('blockchain_latency_ms', 50),
                "system_cpu_usage": self.get_latest_metric_value('system_cpu_usage'),
                "system_memory_usage": self.get_latest_metric_value('system_memory_usage')
            },
            "performance": {
                "blockchain_latency_p95": self.get_percentile('blockchain_latency_ms', 95),
                "consensus_confidence_avg": self.get_metric_summary('consensus_confidence', 60).get('avg', 0),
                "sensor_quality_avg": self.get_average_sensor_quality()
            }
        }
    
    def calculate_success_rate(self) -> float:
        """Calcule le taux de succès du consensus"""
        success = self.counters.get('consensus_success_total', 0)
        total = self.counters.get('consensus_attempts_total', 0)
        
        if total == 0:
            return 1.0
        
        return round(success / total, 3)
    
    def get_latest_metric_value(self, metric_name: str) -> float:
        """Récupère la dernière valeur d'une métrique"""
        if metric_name in self.metrics and self.metrics[metric_name]:
            return self.metrics[metric_name][-1].value
        return 0.0
    
    def get_average_sensor_quality(self) -> float:
        """Calcule la qualité moyenne des capteurs"""
        quality_summary = self.get_metric_summary('sensor_quality_score', 60)
        return quality_summary.get('avg', 0.0)

# Instance globale du collecteur
metrics_collector = MetricsCollector()