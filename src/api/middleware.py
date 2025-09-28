"""
Middleware de sécurité pour l'API RODIO
"""

import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware de sécurité et logging"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Headers de sécurité
        response = await call_next(request)
        
        # Ajout des headers de sécurité
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Logging des requêtes
        process_time = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s - "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware de limitation de taux (simple)"""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = {}
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Nettoyage des anciens enregistrements
        self.clients = {
            ip: timestamps for ip, timestamps in self.clients.items()
            if any(t > current_time - self.period for t in timestamps)
        }
        
        # Vérification du taux pour ce client
        if client_ip in self.clients:
            # Filtrage des timestamps récents
            recent_calls = [
                t for t in self.clients[client_ip]
                if t > current_time - self.period
            ]
            
            if len(recent_calls) >= self.calls:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Trop de requêtes. Réessayez plus tard."}
                )
            
            self.clients[client_ip] = recent_calls + [current_time]
        else:
            self.clients[client_ip] = [current_time]
        
        return await call_next(request)