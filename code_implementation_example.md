# HyperLiquidPerpBot UI Implementation Example Code

This document provides example code snippets to illustrate how the UI implementation would work with the existing HyperLiquidPerpBot codebase.

## 1. Data Collection Hooks

Add the following code to the bot's main execution loop to collect data:

```python
# In bot.py or similar core file

class BotDataCollector:
    def __init__(self, db_path="bot_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        import sqlite3
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
        import sqlite3
        import datetime
        
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
        import sqlite3
        import datetime
        
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
        import sqlite3
        import datetime
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        timestamp = datetime.datetime.now().isoformat()
        
        c.execute(
            "INSERT INTO bot_status (status, timestamp) VALUES (?, ?)",
            (status, timestamp)
        )
        
        conn.commit()
        conn.close()


# Integrate with the bot
class HyperLiquidBot:
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.data_collector = BotDataCollector()
        self.running = False
        # ... other initialization code
    
    def start(self):
        self.running = True
        self.data_collector.update_status("RUNNING")
        # ... existing start code
    
    def stop(self):
        self.running = False
        self.data_collector.update_status("STOPPED")
        # ... existing stop code
    
    def execute_trade(self, asset, trade_type, size, price):
        # ... existing trade execution code
        
        # Calculate PnL
        pnl = self.calculate_pnl(asset, trade_type, size, price)
        
        # Record the trade
        self.data_collector.record_trade(asset, trade_type, size, price, pnl)
        
        # Update balance record
        current_balance = self.get_account_balance()
        self.data_collector.record_balance(current_balance)
```

## 2. Flask API Implementation

Create a Flask application to serve as the API layer:

```python
# In ui_server.py

from flask import Flask, jsonify, request, render_template
import sqlite3
import datetime
import json
import threading
import time

app = Flask(__name__)

# Import the bot module
from bot import HyperLiquidBot

# Initialize the bot with configuration
bot_instance = HyperLiquidBot("config.yaml")

# Database helper functions
def get_db_connection():
    conn = sqlite3.connect('bot_data.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    conn = get_db_connection()
    status = conn.execute('SELECT * FROM bot_status ORDER BY id DESC LIMIT 1').fetchone()
    conn.close()
    
    if status:
        return jsonify({
            'status': status['status'],
            'timestamp': status['timestamp']
        })
    else:
        return jsonify({
            'status': 'UNKNOWN',
            'timestamp': datetime.datetime.now().isoformat()
        })

@app.route('/api/open_positions')
def get_open_positions():
    # This would connect to the bot to get real-time position data
    # For now, we'll just return sample data
    positions = bot_instance.get_open_positions()
    return jsonify(positions)

@app.route('/api/trade_history')
def get_trade_history():
    conn = get_db_connection()
    trades = conn.execute('SELECT * FROM trades ORDER BY timestamp DESC LIMIT 50').fetchall()
    conn.close()
    
    return jsonify([{
        'timestamp': trade['timestamp'],
        'asset': trade['asset'],
        'type': trade['type'],
        'size': trade['size'],
        'price': trade['price'],
        'pnl': trade['pnl']
    } for trade in trades])

@app.route('/api/balance_history')
def get_balance_history():
    conn = get_db_connection()
    history = conn.execute('SELECT * FROM balance_history ORDER BY timestamp ASC').fetchall()
    conn.close()
    
    return jsonify([{
        'timestamp': record['timestamp'],
        'balance': record['balance']
    } for record in history])

@app.route('/api/start_bot', methods=['POST'])
def start_bot():
    bot_instance.start()
    return jsonify({'status': 'started'})

@app.route('/api/stop_bot', methods=['POST'])
def stop_bot():
    bot_instance.stop()
    return jsonify({'status': 'stopped'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## 3. HTML/CSS/JavaScript Frontend

Create a basic frontend interface:

```html
<!-- In templates/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HyperLiquidPerpBot Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
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
        }
    </style>
</head>
<body>
    <div class="container mt-4">
        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-between">
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

        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h4>Open Positions</h4>
                    </div>
                    <div class="card-body">
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

        <div class="row">
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

        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h4>Trade History</h4>
                    </div>
                    <div class="card-body">
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

    <script>
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
                            dailyPnl += trade.pnl;
                        }
                        
                        const row = document.createElement('tr');
                        
                        const pnlClass = trade.pnl >= 0 ? 'text-success' : 'text-danger';
                        
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
                        if (balanceChart) {
                            balanceChart.destroy();
                        }
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
    </script>
</body>
</html>
```

## 4. Integration with the Bot's Main File

Modify the bot's main entry point:

```python
# In main.py

import argparse
from bot import HyperLiquidBot
import threading
import ui_server

def main():
    parser = argparse.ArgumentParser(description='HyperLiquidPerpBot with UI')
    parser.add_argument('--config', type=str, default='config.yaml', help='Path to configuration file')
    parser.add_argument('--ui', action='store_true', help='Start UI server')
    args = parser.parse_args()
    
    # Initialize the bot
    bot = HyperLiquidBot(args.config)
    
    # Start UI server if requested
    if args.ui:
        print("Starting UI server...")
        ui_thread = threading.Thread(target=ui_server.app.run, kwargs={'host': '0.0.0.0', 'port': 5000})
        ui_thread.daemon = True
        ui_thread.start()
    
    # Ask if user wants to start the bot right away
    start_bot = input("Start the bot now? (y/n): ")
    if start_bot.lower() == 'y':
        bot.start()
    
    try:
        # Keep the main thread alive
        while True:
            cmd = input("Enter command (start/stop/quit): ")
            if cmd.lower() == 'start':
                bot.start()
            elif cmd.lower() == 'stop':
                bot.stop()
            elif cmd.lower() == 'quit':
                break
    except KeyboardInterrupt:
        pass
    finally:
        # Make sure to stop the bot before exiting
        bot.stop()
        print("Bot stopped. Exiting...")

if __name__ == "__main__":
    main()
```

## 5. Example Bot Extension for API Integration

Add the following methods to the `HyperLiquidBot` class:

```python
def get_open_positions(self):
    # This is a placeholder. In a real implementation, 
    # you would get the actual open positions from the exchange
    # through the HyperLiquid API
    positions = []
    
    # Query the exchange for open positions
    try:
        # Assuming self.exchange is the HyperLiquid exchange client
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

def get_account_balance(self):
    # Get the current account balance from the exchange
    try:
        # Assuming self.exchange is the HyperLiquid exchange client
        balance_info = self.exchange.get_account_balance()
        return balance_info['total_equity']
    except Exception as e:
        print(f"Error getting account balance: {e}")
        return 0.0

def calculate_pnl(self, asset, trade_type, size, price):
    # This is a simplified PnL calculation
    # In a real implementation, you would need to consider:
    # - Previous positions
    # - Fees
    # - Funding rates
    # - etc.
    
    # For this example, we'll just return a dummy value
    import random
    return random.uniform(-50, 50)  # Return a random PnL between -$50 and $50
```

## Using the Implementation

To run the bot with the UI:

```bash
python main.py --config config.yaml --ui
```

This will:
1. Start the Flask UI server on port 5000
2. Initialize the bot with the provided configuration
3. Allow the user to start/stop the bot via command line or web UI

The web UI will be accessible at `http://localhost:5000` and will provide:
- Real-time status of the bot
- Display of open positions
- Trade history
- Balance history chart
- Start/stop controls