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