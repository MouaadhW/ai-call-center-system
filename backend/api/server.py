from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import config
from api.routes import router

# Create FastAPI app
app = FastAPI(
    title=f"{config.COMPANY_NAME} API",
    description="AI Call Center System API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {config.COMPANY_NAME} API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

@app.on_event("startup")
async def startup_event():
    """Startup event"""
    logger.info("API Server starting up...")
    logger.info(f"API available at http://{config.API_HOST}:{config.API_PORT}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    logger.info("API Server shutting down...")
