from flask import Flask, jsonify, request, render_template, redirect, url_for, send_from_directory
import os
import sys
import threading
import time

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.database import DatabaseManager
from app.exchange_manager import ExchangeManager
from app.logger import logger
from app.config import settings

app = Flask(__name__,
            static_folder='static',
            template_folder='templates')

# Global variables
bot_instance = None
db_manager = DatabaseManager()

# API routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/api/status')
def get_status():
    status = db_manager.get_latest_status()
    return jsonify(status)

@app.route('/api/open_positions')
def get_open_positions():
    if bot_instance:
        try:
            positions = []
            # In a real implementation, get positions from exchange
            positions = bot_instance.get_open_positions()
            return jsonify(positions)
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return jsonify([])
    return jsonify([])

@app.route('/api/trade_history')
def get_trade_history():
    try:
        trades = db_manager.get_trades(limit=50)
        return jsonify(trades)
    except Exception as e:
        logger.error(f"Error getting trade history: {e}")
        return jsonify([])

@app.route('/api/balance_history')
def get_balance_history():
    try:
        history = db_manager.get_balance_history(days=7)
        return jsonify(history)
    except Exception as e:
        logger.error(f"Error getting balance history: {e}")
        return jsonify([])

@app.route('/api/start_bot', methods=['POST'])
def start_bot():
    if bot_instance:
        try:
            # In a real implementation, start the bot's trading functionality
            # For now, just update the status
            db_manager.update_status("RUNNING")
            return jsonify({'status': 'started'})
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    return jsonify({'status': 'error', 'message': 'Bot not initialized'}), 500

@app.route('/api/stop_bot', methods=['POST'])
def stop_bot():
    if bot_instance:
        try:
            # In a real implementation, stop the bot's trading functionality
            # For now, just update the status
            db_manager.update_status("STOPPED")
            return jsonify({'status': 'stopped'})
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    return jsonify({'status': 'error', 'message': 'Bot not initialized'}), 500

@app.route('/api/update_keys', methods=['POST'])
def update_api_keys():
    if not bot_instance:
        return jsonify({'status': 'error', 'message': 'Bot not initialized'}), 500
    
    try:
        data = request.json
        
        # Update environment variables
        if 'privateKey' in data and data['privateKey']:
            os.environ['HYPERLIQUID_PRIVATE_KEY'] = data['privateKey']
            # Update the bot instance
            bot_instance.private_key = data['privateKey']
        
        if 'accountAddress' in data and data['accountAddress']:
            os.environ['HYPERLIQUID_ACCOUNT_ADDRESS'] = data['accountAddress']
            # Update the bot instance
            bot_instance.account_address = data['accountAddress']
        
        if 'monitoringAddress' in data and data['monitoringAddress']:
            os.environ['HYPERLIQUID_MONITORING_ADDRESS'] = data['monitoringAddress']
            # Update the bot instance
            bot_instance.monitoring_address = data['monitoringAddress']
        
        # Optional: Re-initialize the bot with new keys
        bot_instance.initialize_exchange()
        
        logger.info("API keys updated successfully")
        return jsonify({'status': 'success', 'message': 'API keys updated successfully'})
    except Exception as e:
        logger.error(f"Error updating API keys: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/generate_alert', methods=['POST'])
def generate_alert():
    try:
        data = request.json
        trading_pair = data.get('tradingPair', 'ETH')
        position_size_percent = float(data.get('positionSize', 10))
        action = data.get('action', 'BUY')
        
        # Get current balance
        balance = bot_instance.get_account_balance()
        
        # Calculate the absolute position size based on percentage
        position_size = (balance * (position_size_percent / 100))
        
        # Format to a reasonable number of decimal places for the asset
        if trading_pair in ['BTC']:
            position_size = round(position_size / 30000, 4)  # Example BTC price $30,000
        elif trading_pair in ['ETH']:
            position_size = round(position_size / 2000, 4)  # Example ETH price $2,000
        else:
            position_size = round(position_size / 100, 4)  # Default divisor
        
        # Generate the alert JSON
        alert_json = {
            "action": action,
            "asset": trading_pair,
            "size": position_size
        }
        
        return jsonify({
            'status': 'success', 
            'alert': alert_json,
            'webhook_url': f"http://your-server:8000/webhook"
        })
    except Exception as e:
        logger.error(f"Error generating alert: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def run_flask_app(host='0.0.0.0', port=5000):
    app.run(host=host, port=port, debug=False)

def start_ui_server(exchange_manager_instance=None, host='0.0.0.0', port=5000):
    global bot_instance
    bot_instance = exchange_manager_instance
    
    # Initialize with a stopped status if nothing exists
    try:
        status = db_manager.get_latest_status()
        if not status or 'status' not in status:
            db_manager.update_status("STOPPED")
    except Exception:
        db_manager.update_status("STOPPED")
    
    # Create a thread for the UI server
    ui_thread = threading.Thread(target=run_flask_app, args=(host, port))
    ui_thread.daemon = True
    ui_thread.start()
    
    logger.info(f"UI server started at http://{host}:{port}")
    return ui_thread

if __name__ == "__main__":
    # For testing, create an exchange manager instance
    try:
        exchange_manager = ExchangeManager()
        start_ui_server(exchange_manager, port=5000)
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("UI server stopping...")