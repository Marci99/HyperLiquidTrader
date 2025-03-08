# HyperLiquidPerpBot Adaptation Guide

This guide outlines the steps needed to adapt the HyperLiquidPerpBot for your personal use, including the implementation of a simple user interface.

## Part 1: Getting Started with the Bot

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/itsumonemuidesu/HyperLiquidPerpBot.git
cd HyperLiquidPerpBot

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Your API Keys

Create a `.env` file in the root directory:

```
HYPERLIQUID_PRIVATE_KEY=your_private_key_here
```

### 3. Modify the Configuration

Edit the `config.yaml` file to match your trading preferences:

```yaml
# Basic bot configuration
bot:
  exchange: hyperliquid
  strategy: market_making
  assets:
    - BTC-PERP
    - ETH-PERP
  log_level: INFO

# Strategy-specific parameters
market_making:
  spread_percentage: 0.2
  order_size: 0.01
  max_position: 0.05
  rebalance_threshold: 0.5
  min_profit_percentage: 0.1
  
# Risk management
risk:
  max_daily_loss: 100  # In USD
  max_open_orders: 10
  stop_loss_percentage: 1.0
```

## Part 2: UI Implementation

### 1. Create the Database Module

Create a file called `db_manager.py`:

```python
import sqlite3
import datetime
import os

class DatabaseManager:
    def __init__(self, db_path="bot_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        # Create the database directory if it doesn't exist
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Create tables for data storage
        c.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            asset TEXT,
            type TEXT,
            size REAL,
            price REAL,
            pnl REAL
        )
        ''')
        
        c.execute('''
        CREATE TABLE IF NOT EXISTS balance_history (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            balance REAL
        )
        ''')
        
        c.execute('''
        CREATE TABLE IF NOT EXISTS bot_status (
            id INTEGER PRIMARY KEY,
            status TEXT,
            timestamp TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_trade(self, asset, trade_type, size, price, pnl):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        timestamp = datetime.datetime.now().isoformat()
        
        c.execute(
            "INSERT INTO trades (timestamp, asset, type, size, price, pnl) VALUES (?, ?, ?, ?, ?, ?)",
            (timestamp, asset, trade_type, size, price, pnl)
        )
        
        conn.commit()
        conn.close()
    
    def record_balance(self, balance):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        timestamp = datetime.datetime.now().isoformat()
        
        c.execute(
            "INSERT INTO balance_history (timestamp, balance) VALUES (?, ?)",
            (timestamp, balance)
        )
        
        conn.commit()
        conn.close()
    
    def update_status(self, status):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        timestamp = datetime.datetime.now().isoformat()
        
        c.execute(
            "INSERT INTO bot_status (status, timestamp) VALUES (?, ?)",
            (status, timestamp)
        )
        
        conn.commit()
        conn.close()
    
    def get_trades(self, limit=50):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute("SELECT * FROM trades ORDER BY timestamp DESC LIMIT ?", (limit,))
        trades = [dict(row) for row in c.fetchall()]
        
        conn.close()
        return trades
    
    def get_balance_history(self, days=7):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        # Calculate date for filtering
        cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
        
        c.execute("SELECT * FROM balance_history WHERE timestamp > ? ORDER BY timestamp ASC", (cutoff_date,))
        history = [dict(row) for row in c.fetchall()]
        
        conn.close()
        return history
    
    def get_latest_status(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute("SELECT * FROM bot_status ORDER BY id DESC LIMIT 1")
        status = c.fetchone()
        
        conn.close()
        return dict(status) if status else {"status": "UNKNOWN", "timestamp": datetime.datetime.now().isoformat()}
```

### 2. Modify the Bot Class

Integrate the database manager with the bot. In the bot's main class file (likely `bot.py`), add:

```python
from db_manager import DatabaseManager

class HyperLiquidBot:
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.db_manager = DatabaseManager()
        self.running = False
        # ... existing initialization code
    
    def start(self):
        self.running = True
        self.db_manager.update_status("RUNNING")
        # ... existing start code
    
    def stop(self):
        self.running = False
        self.db_manager.update_status("STOPPED")
        # ... existing stop code
    
    # Add new methods to expose data for the UI
    def get_open_positions(self):
        # Implement actual position fetching from HyperLiquid
        positions = []
        if hasattr(self, 'exchange'):
            try:
                # Fetch positions from the exchange API
                # This needs to be implemented based on HyperLiquid's API
                exchange_positions = self.exchange.get_positions()
                
                for pos in exchange_positions:
                    positions.append({
                        'asset': pos['asset'],
                        'size': pos['size'],
                        'entryPrice': pos['entry_price'],
                        'currentPrice': pos['mark_price'],
                        'pnl': pos['unrealized_pnl']
                    })
            except Exception as e:
                print(f"Error getting positions: {e}")
        
        return positions
    
    # After each trade execution, add:
    def on_trade_executed(self, trade_info):
        # Process trade information
        asset = trade_info['asset']
        trade_type = trade_info['type']  # BUY or SELL
        size = trade_info['size']
        price = trade_info['price']
        pnl = trade_info.get('pnl', 0)
        
        # Record the trade
        self.db_manager.record_trade(asset, trade_type, size, price, pnl)
        
        # Update balance
        current_balance = self.get_account_balance()
        self.db_manager.record_balance(current_balance)
    
    def get_account_balance(self):
        # Implement actual balance fetching from HyperLiquid
        balance = 0
        if hasattr(self, 'exchange'):
            try:
                # This needs to be implemented based on HyperLiquid's API
                balance_info = self.exchange.get_account_balance()
                balance = balance_info['total_equity']
            except Exception as e:
                print(f"Error getting account balance: {e}")
        
        return balance
```

### 3. Create the UI Server

Create a new file `ui_server.py`:

```python
from flask import Flask, jsonify, request, render_template, send_from_directory
import os
import time
import threading
import json

# Import your bot module
# Update this import to match your project structure
from bot import HyperLiquidBot

app = Flask(__name__)
bot_instance = None

# Routes for serving the UI
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# API routes
@app.route('/api/status')
def get_status():
    if bot_instance and hasattr(bot_instance, 'db_manager'):
        status = bot_instance.db_manager.get_latest_status()
        return jsonify(status)
    return jsonify({"status": "UNKNOWN", "timestamp": time.time()})

@app.route('/api/open_positions')
def get_open_positions():
    if bot_instance:
        positions = bot_instance.get_open_positions()
        return jsonify(positions)
    return jsonify([])

@app.route('/api/trade_history')
def get_trade_history():
    if bot_instance and hasattr(bot_instance, 'db_manager'):
        trades = bot_instance.db_manager.get_trades(limit=50)
        return jsonify(trades)
    return jsonify([])

@app.route('/api/balance_history')
def get_balance_history():
    if bot_instance and hasattr(bot_instance, 'db_manager'):
        history = bot_instance.db_manager.get_balance_history(days=7)
        return jsonify(history)
    return jsonify([])

@app.route('/api/start_bot', methods=['POST'])
def start_bot():
    if bot_instance:
        bot_instance.start()
        return jsonify({'status': 'started'})
    return jsonify({'status': 'error', 'message': 'Bot not initialized'}), 500

@app.route('/api/stop_bot', methods=['POST'])
def stop_bot():
    if bot_instance:
        bot_instance.stop()
        return jsonify({'status': 'stopped'})
    return jsonify({'status': 'error', 'message': 'Bot not initialized'}), 500

def run_flask_app(host='0.0.0.0', port=5000):
    app.run(host=host, port=port, debug=False)

def start_ui_server(bot, host='0.0.0.0', port=5000):
    global bot_instance
    bot_instance = bot
    
    # Create a thread for the UI server
    ui_thread = threading.Thread(target=run_flask_app, args=(host, port))
    ui_thread.daemon = True
    ui_thread.start()
    
    print(f"UI server started at http://{host}:{port}")
    return ui_thread
```

### 4. Create the UI Templates and Static Files

Create directories for templates and static files:

```bash
mkdir -p templates static/css static/js
```

Create `templates/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HyperLiquidPerpBot Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="/static/css/style.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container mt-4">
        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h2>HyperLiquidPerpBot Dashboard</h2>
                        <div>
                            <span id="status-indicator" class="status-indicator status-inactive"></span>
                            <span id="status-text">Inactive</span>
                            <button id="start-btn" class="btn btn-success ms-3">Start Bot</button>
                            <button id="stop-btn" class="btn btn-danger ms-2">Stop Bot</button>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4">
                                <div class="card">
                                    <div class="card-body">
                                        <h5 class="card-title">Current Balance</h5>
                                        <h3 id="current-balance">$0.00</h3>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card">
                                    <div class="card-body">
                                        <h5 class="card-title">24h Profit/Loss</h5>
                                        <h3 id="daily-pnl">$0.00 (0.00%)</h3>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card">
                                    <div class="card-body">
                                        <h5 class="card-title">Total Trades</h5>
                                        <h3 id="total-trades">0</h3>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h4>Open Positions</h4>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th>Asset</th>
                                        <th>Size</th>
                                        <th>Entry Price</th>
                                        <th>Current Price</th>
                                        <th>P/L</th>
                                    </tr>
                                </thead>
                                <tbody id="positions-table">
                                    <!-- Positions will be populated here -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h4>Balance History</h4>
                    </div>
                    <div class="card-body">
                        <canvas id="balance-chart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h4>Trade History</h4>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th>Time</th>
                                        <th>Asset</th>
                                        <th>Type</th>
                                        <th>Size</th>
                                        <th>Price</th>
                                        <th>P/L</th>
                                    </tr>
                                </thead>
                                <tbody id="trade-history">
                                    <!-- Trade history will be populated here -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="/static/js/dashboard.js"></script>
</body>
</html>
```

Create `static/css/style.css`:

```css
.status-indicator {
    width: 15px;
    height: 15px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 5px;
}
.status-active {
    background-color: #28a745;
}
.status-inactive {
    background-color: #dc3545;
}
.card {
    margin-bottom: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.card-header {
    background-color: #f8f9fa;
    border-bottom: 1px solid #e3e6f0;
}
.table {
    margin-bottom: 0;
}
.table th {
    font-weight: 500;
    border-top: none;
}
```

Create `static/js/dashboard.js`:

```javascript
// Helper function to format currency
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
}

// Helper function to format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Balance chart initialization
let balanceChart = null;

function initBalanceChart(data) {
    const ctx = document.getElementById('balance-chart').getContext('2d');
    
    if (balanceChart) {
        balanceChart.destroy();
    }
    
    balanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(item => formatDate(item.timestamp)),
            datasets: [{
                label: 'Account Balance',
                data: data.map(item => item.balance),
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
}

// Update bot status indicator
function updateStatusIndicator(status) {
    const indicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    
    if (status === 'RUNNING') {
        indicator.className = 'status-indicator status-active';
        statusText.textContent = 'Active';
    } else {
        indicator.className = 'status-indicator status-inactive';
        statusText.textContent = 'Inactive';
    }
}

// Fetch open positions
function fetchOpenPositions() {
    fetch('/api/open_positions')
        .then(response => response.json())
        .then(positions => {
            const tableBody = document.getElementById('positions-table');
            tableBody.innerHTML = '';
            
            if (positions.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="5" class="text-center">No open positions</td></tr>';
                return;
            }
            
            positions.forEach(position => {
                const row = document.createElement('tr');
                
                const pnlClass = position.pnl >= 0 ? 'text-success' : 'text-danger';
                
                row.innerHTML = `
                    <td>${position.asset}</td>
                    <td>${position.size}</td>
                    <td>${formatCurrency(position.entryPrice)}</td>
                    <td>${formatCurrency(position.currentPrice)}</td>
                    <td class="${pnlClass}">${formatCurrency(position.pnl)}</td>
                `;
                
                tableBody.appendChild(row);
            });
        })
        .catch(error => console.error('Error fetching positions:', error));
}

// Fetch trade history
function fetchTradeHistory() {
    fetch('/api/trade_history')
        .then(response => response.json())
        .then(trades => {
            const tableBody = document.getElementById('trade-history');
            tableBody.innerHTML = '';
            
            if (trades.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="6" class="text-center">No trade history</td></tr>';
                return;
            }
            
            document.getElementById('total-trades').textContent = trades.length;
            
            // Calculate 24h P/L
            const now = new Date();
            const oneDayAgo = new Date(now - 24 * 60 * 60 * 1000);
            
            let dailyPnl = 0;
            
            trades.forEach(trade => {
                const tradeDate = new Date(trade.timestamp);
                
                if (tradeDate >= oneDayAgo) {
                    dailyPnl += parseFloat(trade.pnl);
                }
                
                const row = document.createElement('tr');
                
                const pnlClass = parseFloat(trade.pnl) >= 0 ? 'text-success' : 'text-danger';
                
                row.innerHTML = `
                    <td>${formatDate(trade.timestamp)}</td>
                    <td>${trade.asset}</td>
                    <td>${trade.type}</td>
                    <td>${trade.size}</td>
                    <td>${formatCurrency(trade.price)}</td>
                    <td class="${pnlClass}">${formatCurrency(trade.pnl)}</td>
                `;
                
                tableBody.appendChild(row);
            });
            
            // Update daily P/L display
            const dailyPnlElement = document.getElementById('daily-pnl');
            const pnlClass = dailyPnl >= 0 ? 'text-success' : 'text-danger';
            dailyPnlElement.className = pnlClass;
            dailyPnlElement.textContent = `${formatCurrency(dailyPnl)}`;
        })
        .catch(error => console.error('Error fetching trade history:', error));
}

// Fetch balance history
function fetchBalanceHistory() {
    fetch('/api/balance_history')
        .then(response => response.json())
        .then(history => {
            if (history.length > 0) {
                // Update current balance
                const latestBalance = history[history.length - 1].balance;
                document.getElementById('current-balance').textContent = formatCurrency(latestBalance);
                
                // Update balance chart
                initBalanceChart(history);
            }
        })
        .catch(error => console.error('Error fetching balance history:', error));
}

// Fetch bot status
function fetchBotStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            updateStatusIndicator(data.status);
        })
        .catch(error => console.error('Error fetching bot status:', error));
}

// Start bot
document.getElementById('start-btn').addEventListener('click', function() {
    fetch('/api/start_bot', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(() => {
        updateStatusIndicator('RUNNING');
    })
    .catch(error => console.error('Error starting bot:', error));
});

// Stop bot
document.getElementById('stop-btn').addEventListener('click', function() {
    fetch('/api/stop_bot', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(() => {
        updateStatusIndicator('STOPPED');
    })
    .catch(error => console.error('Error stopping bot:', error));
});

// Initial data load
fetchBotStatus();
fetchOpenPositions();
fetchTradeHistory();
fetchBalanceHistory();

// Set up auto-refresh
setInterval(() => {
    fetchBotStatus();
    fetchOpenPositions();
    fetchTradeHistory();
    fetchBalanceHistory();
}, 30000); // Refresh every 30 seconds
```

### 5. Modify the Main Entry Point

Update the `main.py` file to include the UI server:

```python
import argparse
import threading
import time
import os
import signal
import sys

from bot import HyperLiquidBot
from ui_server import start_ui_server

def main():
    parser = argparse.ArgumentParser(description='HyperLiquidPerpBot with UI')
    parser.add_argument('--config', type=str, default='config.yaml', help='Path to configuration file')
    parser.add_argument('--no-ui', action='store_true', help='Disable UI server')
    parser.add_argument('--port', type=int, default=5000, help='UI server port')
    parser.add_argument('--autostart', action='store_true', help='Automatically start the bot')
    args = parser.parse_args()
    
    # Initialize the bot
    bot = HyperLiquidBot(args.config)
    
    # Start UI server unless disabled
    if not args.no_ui:
        ui_thread = start_ui_server(bot, port=args.port)
    
    # Auto-start if requested
    if args.autostart:
        print("Auto-starting bot...")
        bot.start()
    
    # Setup signal handling for graceful shutdown
    def signal_handler(sig, frame):
        print('Shutting down...')
        bot.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # If running in command line mode, handle commands
    if args.no_ui:
        try:
            # Keep the main thread alive
            while True:
                cmd = input("Enter command (start/stop/status/quit): ").lower()
                if cmd == 'start':
                    bot.start()
                elif cmd == 'stop':
                    bot.stop()
                elif cmd == 'status':
                    print(f"Bot status: {'RUNNING' if bot.running else 'STOPPED'}")
                elif cmd == 'quit':
                    bot.stop()
                    break
        except KeyboardInterrupt:
            bot.stop()
    else:
        # If UI is enabled, just keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            bot.stop()

if __name__ == "__main__":
    main()
```

### 6. Update requirements.txt

Add Flask to the requirements:

```
flask==2.0.1
# ... other existing requirements
```

## Part 3: Running the Bot with UI

### 1. Starting the Bot

```bash
# Start with UI enabled (default)
python main.py --config config.yaml

# Start with UI and auto-start the bot
python main.py --config config.yaml --autostart

# Start without UI (command line only)
python main.py --config config.yaml --no-ui
```

### 2. Accessing the UI

Once started, the UI will be available at:

```
http://localhost:5000
```

### 3. Deployment Considerations

For production use, consider:

1. Use a proper web server like Gunicorn to serve the Flask application
2. Set up process monitoring (e.g., systemd or supervisord)
3. Implement more robust security (API keys, HTTPS)

Example systemd service file (`hyperliquid-bot.service`):

```
[Unit]
Description=HyperLiquid Trading Bot
After=network.target

[Service]
User=youruser
WorkingDirectory=/path/to/HyperLiquidPerpBot
ExecStart=/path/to/HyperLiquidPerpBot/venv/bin/python main.py --config config.yaml --autostart
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

## Part 4: Common Issues and Troubleshooting

### 1. Database Issues

If you encounter database errors:

```bash
# Remove the database file to reset
rm bot_data.db
```

### 2. API Connection Problems

Check your `.env` file and make sure your API keys are correct. Verify Internet connectivity.

### 3. UI Not Loading

Make sure port 5000 is not in use by another application. Try running with a different port:

```bash
python main.py --port 5001
```

### 4. Bot Not Trading

Check logs for errors. Ensure your configuration is correct, especially asset names and trading parameters.

## Conclusion

You've now successfully set up the HyperLiquidPerpBot with a user interface that shows:

- Open trades
- Trade history
- Balance history
- P/L per trade
- Start and stop buttons

This implementation maintains the core functionality of the bot while adding monitoring and control capabilities. Adjust the configuration parameters to match your risk tolerance and trading strategy.

For more advanced usage, refer to the bot's documentation on GitHub and the HyperLiquid API documentation.