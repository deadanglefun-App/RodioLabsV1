"""
API principale RODIO - Refactorisée et sécurisée
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse

from src.config.settings import get_settings, setup_logging
from src.core.oracle_manager import OracleManager
from src.api.routes import health, sensors, oracle
from src.api.middleware import SecurityMiddleware

# Configuration du logging
setup_logging()
logger = logging.getLogger(__name__)

# Instance globale de l'Oracle Manager
oracle_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    global oracle_manager
    
    try:
        # Initialisation
        logger.info("🚀 Démarrage de RODIO Oracle Node...")
        settings = get_settings()
        
        # Initialisation de l'Oracle Manager
        oracle_manager = OracleManager(settings)
        await oracle_manager.initialize()
        
        logger.info("✅ RODIO Oracle Node démarré avec succès")
        yield
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du démarrage: {e}")
        raise
    finally:
        # Nettoyage
        if oracle_manager:
            await oracle_manager.shutdown()
        logger.info("🛑 RODIO Oracle Node arrêté")

# Création de l'application FastAPI
app = FastAPI(
    title="RODIO Oracle Node",
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

# Middleware de sécurité
app.add_middleware(SecurityMiddleware)

# Sécurité API
security = HTTPBearer()

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Vérifie la clé API"""
    settings = get_settings()
    
    if credentials.credentials != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

# Inclusion des routes
app.include_router(health.router, prefix="/api/v1")
app.include_router(
    sensors.router, 
    prefix="/api/v1", 
    dependencies=[Depends(verify_api_key)]
)
app.include_router(
    oracle.router, 
    prefix="/api/v1", 
    dependencies=[Depends(verify_api_key)]
)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Gestionnaire global d'exceptions"""
    logger.error(f"Erreur non gérée: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erreur interne du serveur"}
    )

def get_oracle_manager() -> OracleManager:
    """Dependency injection pour l'Oracle Manager"""
    if oracle_manager is None:
        raise HTTPException(
            status_code=503,
            detail="Service non disponible"
        )
    return oracle_manager