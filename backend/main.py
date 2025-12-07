import asyncio
import uvicorn
from loguru import logger
from api.server import app
from agi.agi_handler import AGIServer
import config

# Configure logging
logger.add(
    config.LOG_FILE,
    rotation="500 MB",
    retention="10 days",
    level=config.LOG_LEVEL
)

async def start_agi_server():
    """Start the AGI server for Asterisk communication"""
    logger.info(f"Starting AGI server on port {config.ASTERISK_AGI_PORT}")
    agi_server = AGIServer(host="0.0.0.0", port=config.ASTERISK_AGI_PORT)
    await agi_server.start()

async def start_api_server():
    """Start the FastAPI server"""
    logger.info(f"Starting API server on {config.API_HOST}:{config.API_PORT}")
    config_uvicorn = uvicorn.Config(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        log_level=config.LOG_LEVEL.lower()
    )
    server = uvicorn.Server(config_uvicorn)
    await server.serve()

async def main():
    """Main entry point - start both servers concurrently"""
    logger.info("=" * 50)
    logger.info(f"Starting {config.COMPANY_NAME} System")
    logger.info("=" * 50)
    
    # Start both servers concurrently
    await asyncio.gather(
        start_agi_server(),
        start_api_server()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
