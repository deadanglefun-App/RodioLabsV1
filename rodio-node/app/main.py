import logging
import asyncio
from web3 import Web3
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
from contextlib import asynccontextmanager

from config import settings

# Configuration du logging
logger = logging.getLogger(__name__)

# Variables globales pour Web3
web3 = None
account = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    global web3, account
    
    try:
        # Initialisation Web3
        logger.info("🔄 Initialisation de la connexion Web3...")
        web3 = Web3(Web3.HTTPProvider(settings.polygon_rpc_url))
        
        if not web3.is_connected():
            raise ConnectionError("Impossible de se connecter à Polygon RPC")
        
        # Configuration du compte (SÉCURISÉ)
        account = web3.eth.account.from_key(f"0x{settings.private_key}")
        web3.eth.default_account = account.address
        
        # Log sécurisé (sans exposer la clé privée)
        logger.info(f"✅ Connecté à Polygon avec le compte {account.address[:10]}...{account.address[-4:]}")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Erreur initialisation: {e}")
        raise
    finally:
        logger.info("🛑 Arrêt de l'application")

# Création de l'application FastAPI
app = FastAPI(
    title="RODIO Node API",
    description="Réseau d'Oracles Décentralisés pour l'IoT",
    version="1.0.0",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sécurité API (optionnelle)
security = HTTPBearer(auto_error=False)

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Vérifie la clé API si configurée"""
    if settings.api_key:
        if not credentials or credentials.credentials != settings.api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Clé API invalide",
                headers={"WWW-Authenticate": "Bearer"},
            )
    return credentials

@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        "message": "RODIO Node API", 
        "version": "1.0.0",
        "node_id": settings.node_id,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Endpoint de santé de l'application"""
    try:
        if not web3 or not web3.is_connected():
            raise HTTPException(status_code=503, detail="Blockchain non connectée")
        
        # Vérifications de santé
        block_number = web3.eth.block_number
        balance = web3.eth.get_balance(web3.eth.default_account)
        
        return {
            "status": "healthy",
            "blockchain_connected": True,
            "current_block": block_number,
            "account_balance": float(web3.from_wei(balance, 'ether')),
            "node_id": settings.node_id,
            "account_address": f"{account.address[:10]}...{account.address[-4:]}"  # Masqué pour sécurité
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.post("/api/sensor-data")
async def submit_sensor_data(
    sensor_data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Endpoint pour soumettre des données capteur (sécurisé)"""
    try:
        # Validation des données
        required_fields = ['sensor_id', 'value', 'timestamp']
        for field in required_fields:
            if field not in sensor_data:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Champ requis manquant: {field}"
                )
        
        # Log sécurisé (sans données sensibles)
        logger.info(f"📡 Données reçues du capteur: {sensor_data.get('sensor_id')}")
        
        # TODO: Ici, implémenter la logique pour envoyer vers le smart contract
        # contract = web3.eth.contract(address=settings.contract_address, abi=contract_abi)
        # tx = contract.functions.submitData(...).build_transaction({...})
        
        return {
            "status": "success",
            "message": "Données reçues et traitées",
            "sensor_id": sensor_data.get('sensor_id'),
            "timestamp": sensor_data.get('timestamp')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur traitement données: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@app.get("/api/status")
async def get_status(credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)):
    """Status détaillé du nœud (sécurisé)"""
    try:
        return {
            "node_info": {
                "node_id": settings.node_id,
                "version": "1.0.0",
                "blockchain": "Polygon Mumbai",
                "rpc_url": settings.polygon_rpc_url
            },
            "blockchain_status": {
                "connected": web3.is_connected() if web3 else False,
                "current_block": web3.eth.block_number if web3 else 0,
                "network_id": web3.net.version if web3 else "unknown"
            },
            "configuration": {
                "mqtt_broker": settings.mqtt_broker,
                "mqtt_port": settings.mqtt_port,
                "api_port": settings.api_port,
                "log_level": settings.log_level
            }
        }
    except Exception as e:
        logger.error(f"Erreur récupération status: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

if __name__ == "__main__":
    logger.info(f"🚀 Démarrage du nœud RODIO: {settings.node_id}")
    logger.info(f"🔗 Connexion à: {settings.polygon_rpc_url}")
    logger.info(f"📡 Port API: {settings.api_port}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.api_port,
        reload=True,  # Seulement en développement
        log_level=settings.log_level.lower()
    )