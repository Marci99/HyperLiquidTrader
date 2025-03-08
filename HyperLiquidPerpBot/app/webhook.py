from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import json
import logging
from app.exchange_manager import ExchangeManager
from app.logger import logger

# Import the database manager
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.database import DatabaseManager

class WebhookHandler:
    def __init__(self, exchange_manager: ExchangeManager):
        self.exchange_manager = exchange_manager
        self.db_manager = DatabaseManager()
        
        # Initialize the bot status
        self.db_manager.update_status("INITIALIZED")
        
        # Record initial balance
        initial_balance = self.exchange_manager.get_account_balance()
        self.db_manager.record_balance(initial_balance)
    
    async def handle_webhook(self, request: Request):
        try:
            # Parse the incoming webhook payload
            payload = await request.json()
            logger.info(f"Received webhook: {payload}")
            
            # Extract the action from the payload
            if "action" not in payload:
                raise HTTPException(status_code=400, detail="Missing 'action' field in payload")
            
            action = payload["action"]
            
            # Execute the action on the exchange
            success, result = self.exchange_manager.handle_action(action)
            
            if success:
                logger.info(f"Action executed successfully: {result}")
                
                # Update the database with trade information
                # For BUY and SELL actions, record the trade
                if action.upper() in ["BUY", "SELL"]:
                    # Extract position info from the result
                    # This assumes the result is in a specific format
                    # In a real implementation, you would parse the result properly
                    if isinstance(result, str) and "position" in result:
                        try:
                            # Extract position data - in a real implementation, 
                            # this would be a proper object
                            position_str = result.split("position: ")[1].strip("}")
                            position_data = json.loads(position_str + "}")
                            
                            self.db_manager.record_trade(
                                asset=position_data["asset"],
                                trade_type=position_data["direction"],
                                size=position_data["size"],
                                price=position_data["entryPrice"],
                                pnl=position_data["pnl"]
                            )
                        except Exception as e:
                            logger.error(f"Error recording trade: {e}")
                
                # For CLOSE actions, record the closing trade with PnL
                elif action.upper() == "CLOSE":
                    if isinstance(result, str) and "PnL" in result:
                        try:
                            # Extract PnL value
                            pnl = float(result.split("PnL: ")[1])
                            
                            # Get the first position (assumes only one is being closed)
                            positions = self.exchange_manager.get_open_positions()
                            if len(positions) > 0:
                                position = positions[0]
                                
                                self.db_manager.record_trade(
                                    asset=position["asset"],
                                    trade_type=f"CLOSE_{position['direction']}",
                                    size=position["size"],
                                    price=position["currentPrice"],
                                    pnl=pnl
                                )
                        except Exception as e:
                            logger.error(f"Error recording close trade: {e}")
                
                # Update the account balance after any action
                current_balance = self.exchange_manager.get_account_balance()
                self.db_manager.record_balance(current_balance)
                
                return {"status": "success", "result": result}
            else:
                logger.error(f"Action failed: {result}")
                return {"status": "error", "message": result}
                
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# FastAPI routes
app = FastAPI()

# Global variables
exchange_manager = None
webhook_handler = None

@app.get("/")
async def root():
    return {"status": "HyperLiquidPerpBot webhook server is running"}

@app.post("/webhook")
async def webhook_endpoint(request: Request):
    if webhook_handler is None:
        raise HTTPException(status_code=500, detail="Webhook handler not initialized")
    
    return await webhook_handler.handle_webhook(request)