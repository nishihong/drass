from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any

from app.api.v1 import chat, knowledge, documents, auth, settings, audit, audit_enhanced, audit_websocket, monitoring, security_enhancement, rag_optimization
from app.core.config import settings as app_settings
from app.core.logging import setup_logging
from app.middleware.error_handler import error_handler_middleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.rate_limit import RateLimitMiddleware

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle events
    """
    # Startup
    logger.info("Starting LangChain Compliance Assistant API...")
    logger.info(f"Environment: {app_settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {app_settings.DEBUG}")
    
    # Initialize connections
    try:
        # Initialize vector store connection
        from app.services.vector_store import vector_store_service
        await vector_store_service.initialize()
        logger.info("Vector store connection initialized")
        
        # Initialize unified LLM service
        from app.services.llm_service_enhanced import unified_llm_service
        await unified_llm_service.initialize()
        logger.info("Unified LLM service initialized with multiple providers")
        
        # Initialize embedding service
        from app.services.embedding_service import embedding_service
        await embedding_service.initialize()
        logger.info("Embedding service initialized")
        
        # Initialize document service
        from app.services.document_service import document_service
        await document_service.initialize()
        logger.info("Document service initialized")
        
        # Start document processor workers
        from app.tasks.document_processor import document_processor
        await document_processor.start()
        logger.info("Document processor workers started")
        
        # Initialize RAG optimization service
        from app.services.rag_optimization_service import rag_optimization_service
        await rag_optimization_service.initialize()
        logger.info("RAG optimization service initialized")
        
        # Initialize WebSocket message broker (only if Redis is enabled)
        if getattr(app_settings, 'REDIS_ENABLED', True):
            try:
                from app.api.v1.message_queue import message_broker
                await message_broker.initialize()
                logger.info("WebSocket message broker initialized")
            except Exception as e:
                logger.warning(f"WebSocket message broker initialization failed (Redis may be disabled): {e}")
        else:
            logger.info("WebSocket message broker skipped (Redis disabled)")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down LangChain Compliance Assistant API...")
    
    # Cleanup connections
    try:
        # Stop document processor workers
        from app.tasks.document_processor import document_processor
        await document_processor.stop()
        
        # Close services
        from app.services.document_service import document_service
        from app.services.storage_service import storage_service
        await storage_service.close()
        
        await vector_store_service.close()
        await unified_llm_service.close()
        await embedding_service.close()
        if getattr(app_settings, 'REDIS_ENABLED', True):
            try:
                from app.api.v1.message_queue import message_broker
                await message_broker.shutdown()
            except Exception as e:
                logger.warning(f"Error shutting down message broker: {e}")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI app instance
app = FastAPI(
    title="LangChain Compliance Assistant API",
    description="Intelligent compliance assistance powered by LangChain and RAG",
    version="1.0.0",
    docs_url="/api/docs" if app_settings.ENABLE_DOCS else None,
    redoc_url="/api/redoc" if app_settings.ENABLE_DOCS else None,
    openapi_url="/api/openapi.json" if app_settings.ENABLE_DOCS else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=app_settings.RATE_LIMIT_PER_MINUTE)
app.middleware("http")(error_handler_middleware)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["knowledge"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(settings.router, prefix="/api/v1/settings", tags=["settings"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["audit"])
app.include_router(audit_enhanced.router, prefix="/api/v1/audit", tags=["audit"])
app.include_router(audit_websocket.router, prefix="/api/v1/audit", tags=["audit"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["monitoring"])
app.include_router(security_enhancement.router, prefix="/api/v1/security", tags=["security"])
app.include_router(rag_optimization.router, prefix="/api/v1/rag", tags=["rag"])

# Include WebSocket routers
from app.api.v1 import websocket
app.include_router(websocket.router, prefix="/api/v1", tags=["websocket"])

# Root endpoint
@app.get("/", tags=["root"])
async def root() -> Dict[str, Any]:
    """
    Root endpoint returning API information
    """
    return {
        "name": "LangChain Compliance Assistant API",
        "version": "1.0.0",
        "status": "healthy",
        "environment": app_settings.ENVIRONMENT,
        "docs": "/api/docs" if app_settings.ENABLE_DOCS else None
    }

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for monitoring
    """
    health_status = {
        "status": "healthy",
        "services": {}
    }
    
    try:
        # Check vector store
        from app.services.vector_store import vector_store_service
        health_status["services"]["vector_store"] = await vector_store_service.health_check()
    except Exception as e:
        health_status["services"]["vector_store"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    try:
        # Check LLM service (using unified service)
        from app.services.llm_service_enhanced import unified_llm_service
        health_status["services"]["llm"] = await unified_llm_service.health_check()
    except Exception as e:
        health_status["services"]["llm"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    try:
        # Check embedding service
        from app.services.embedding_service import embedding_service
        health_status["services"]["embedding"] = await embedding_service.health_check()
    except Exception as e:
        health_status["services"]["embedding"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    return health_status

# Metrics endpoint
@app.get("/metrics", tags=["monitoring"])
async def metrics() -> Dict[str, Any]:
    """
    Metrics endpoint for monitoring
    """
    from app.core.metrics import get_metrics
    return await get_metrics()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=app_settings.HOST,
        port=app_settings.PORT,
        reload=app_settings.DEBUG,
        log_level=app_settings.LOG_LEVEL.lower()
    )