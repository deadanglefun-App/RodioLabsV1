import asyncio
import logging
from src.core.node import RodioNode
from src.monitoring.api import start_monitoring_api

async def main():
    """Point d'entrée principal du nœud RODIO"""
    logging.info("🚀 Démarrage du nœud RODIO...")
    
    # Initialisation du nœud RODIO
    node = RodioNode("config/config.json")
    
    # Démarrage concurrent des services
    await asyncio.gather(
        node.start(),  # Nœud principal
        start_monitoring_api(port=8080),  # API monitoring
    )

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    asyncio.run(main())