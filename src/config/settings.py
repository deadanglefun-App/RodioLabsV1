"""
Configuration sécurisée pour RODIO
Gestion centralisée des variables d'environnement
"""

import os
import logging
from typing import Optional
from pydantic import BaseSettings, validator
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

class Settings(BaseSettings):
    """Configuration principale de l'application RODIO"""
    
    # ===== API CONFIGURATION =====
    api_host: str = "0.0.0.0"
    api_port: int = 8080
    debug: bool = False
    log_level: str = "INFO"
    
    # ===== BLOCKCHAIN CONFIGURATION =====
    polygon_rpc_url: str
    private_key: str
    contract_address: str
    chain_id: int = 80001  # Mumbai testnet par défaut
    
    # ===== MQTT CONFIGURATION =====
    mqtt_broker: str = "broker.hivemq.com"
    mqtt_port: int = 1883
    mqtt_username: Optional[str] = None
    mqtt_password: Optional[str] = None
    
    # ===== DATABASE CONFIGURATION =====
    database_url: Optional[str] = None
    redis_url: Optional[str] = None
    
    # ===== SECURITY =====
    jwt_secret: str
    api_key: str
    
    # ===== MONITORING =====
    prometheus_enabled: bool = True
    grafana_enabled: bool = True
    
    @validator('private_key')
    def validate_private_key(cls, v):
        """Valide que la clé privée est présente et au bon format"""
        if not v:
            raise ValueError("PRIVATE_KEY est requis")
        
        # Supprime le préfixe 0x si présent
        if v.startswith('0x'):
            v = v[2:]
        
        # Vérifie la longueur (64 caractères hex)
        if len(v) != 64:
            raise ValueError("PRIVATE_KEY doit faire 64 caractères hexadécimaux")
        
        # Vérifie que c'est bien de l'hexadécimal
        try:
            int(v, 16)
        except ValueError:
            raise ValueError("PRIVATE_KEY doit être en format hexadécimal")
        
        return v
    
    @validator('contract_address')
    def validate_contract_address(cls, v):
        """Valide l'adresse du contrat"""
        if not v:
            raise ValueError("CONTRACT_ADDRESS est requis")
        
        if not v.startswith('0x'):
            raise ValueError("CONTRACT_ADDRESS doit commencer par 0x")
        
        if len(v) != 42:
            raise ValueError("CONTRACT_ADDRESS doit faire 42 caractères")
        
        return v.lower()
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Valide le niveau de log"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL doit être un de: {valid_levels}")
        return v.upper()
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instance globale des settings
settings = Settings()

def setup_logging():
    """Configure le logging de l'application"""
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/rodio.log') if os.path.exists('logs') else logging.NullHandler()
        ]
    )

def get_settings() -> Settings:
    """Retourne l'instance des settings"""
    return settings