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