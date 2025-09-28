import os
import logging
from dotenv import load_dotenv
from pydantic import BaseSettings, validator
from typing import Optional

class Settings(BaseSettings):
    """Configuration de l'application avec validation stricte"""
    
    # ===== BLOCKCHAIN CONFIGURATION =====
    private_key: str
    polygon_rpc_url: str = "https://rpc-mumbai.maticvigil.com"
    contract_address: str
    
    # ===== APPLICATION CONFIGURATION =====
    node_id: str = "RODIO_NODE_001"
    log_level: str = "INFO"
    api_port: int = 8000
    
    # ===== MQTT CONFIGURATION =====
    mqtt_broker: str = "localhost"
    mqtt_port: int = 1883
    mqtt_username: Optional[str] = None
    mqtt_password: Optional[str] = None
    
    # ===== SECURITY =====
    api_key: Optional[str] = None
    jwt_secret: Optional[str] = None
    
    # ===== DATABASE =====
    database_url: Optional[str] = None
    redis_url: Optional[str] = None
    
    @validator('private_key')
    def validate_private_key(cls, v):
        """Valide que la clé privée est au bon format"""
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

def get_settings():
    """Retourne la configuration validée"""
    load_dotenv()
    return Settings()

def setup_logging(settings: Settings):
    """Configure le logging de l'application"""
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/rodio.log') if os.path.exists('logs') else logging.NullHandler()
        ]
    )

# Instance globale de configuration
try:
    settings = get_settings()
    setup_logging(settings)
    logger = logging.getLogger(__name__)
    logger.info("✅ Configuration chargée avec succès")
except Exception as e:
    print(f"❌ Erreur de configuration: {e}")
    raise