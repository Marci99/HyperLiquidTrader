import os
import logging
import datetime

# Set up the logger with basic configuration
logger = logging.getLogger("hyperliquid_perp_bot")

def setup_logger():
    """Configure the application logger"""
    global logger
    
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Set up logging level
    logger.setLevel(logging.INFO)
    
    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create a file handler
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    file_handler = logging.FileHandler(os.path.join(log_dir, f"{today}.log"))
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info("Logger initialized")
    
    return logger