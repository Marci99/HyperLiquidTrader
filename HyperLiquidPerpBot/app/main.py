import asyncio
import os
import logging
from app.config import settings
from app.exchange_manager import ExchangeManager
from app.webhook import app as webhook_app, exchange_manager, webhook_handler
from app.logger import setup_logger, logger

# Import UI components
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.server import start_ui_server

def create_app():
    # Initialize the logger
    setup_logger()
    
    logger.info("Initializing HyperLiquidPerpBot")
    
    # Create the exchange manager
    global exchange_manager
    exchange_manager = ExchangeManager()
    
    # Initialize the webhook handler
    global webhook_handler
    from app.webhook import WebhookHandler
    webhook_handler = WebhookHandler(exchange_manager)
    
    # Set up globals in the webhook module
    import app.webhook as webhook_module
    webhook_module.exchange_manager = exchange_manager
    webhook_module.webhook_handler = webhook_handler
    
    logger.info("HyperLiquidPerpBot initialized")
    
    return webhook_app

def main():
    # Create the FastAPI app
    app = create_app()
    
    # Start the UI server
    ui_host = settings.ui_host
    ui_port = settings.ui_port
    ui_thread = start_ui_server(exchange_manager, host=ui_host, port=ui_port)
    
    # Start the webhook server
    import uvicorn
    host = settings.api_host
    port = settings.api_port
    
    logger.info(f"Starting webhook server on {host}:{port}")
    logger.info(f"UI server running on http://{ui_host}:{ui_port}")
    
    # Run the FastAPI app
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()