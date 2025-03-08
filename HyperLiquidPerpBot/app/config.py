import os
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # HyperLiquid API settings
    hyperliquid_private_key: str = Field(default="", env='HYPERLIQUID_PRIVATE_KEY')
    hyperliquid_account_address: str = Field(default="", env='HYPERLIQUID_ACCOUNT_ADDRESS')
    hyperliquid_monitoring_address: str = Field(default="", env='HYPERLIQUID_MONITORING_ADDRESS')
    
    # Trading settings
    asset_name: str = Field(default="ETH")
    leverage: int = Field(default=5)
    is_cross: bool = Field(default=True)
    
    # API settings
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    
    # UI settings
    ui_host: str = Field(default="0.0.0.0")
    ui_port: int = Field(default=5000)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create the settings object
settings = Settings()

# Validate the required fields
if not settings.hyperliquid_private_key:
    import logging
    logging.warning("HYPERLIQUID_PRIVATE_KEY is not set. Bot will run in demo mode.")
    
if not settings.hyperliquid_account_address:
    import logging
    logging.warning("HYPERLIQUID_ACCOUNT_ADDRESS is not set. Bot will run in demo mode.")