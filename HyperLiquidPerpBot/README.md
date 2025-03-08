# HyperLiquidPerpBot

A trading bot for automated trading on the HyperLiquid exchange with a web-based UI for monitoring and control.

## Features

- Automated trading on HyperLiquid Perpetual Contracts
- Web dashboard for monitoring trades and performance
- Real-time balance and trade history tracking
- Start/stop trading functionality
- P/L monitoring per trade

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your HyperLiquid API credentials:
   ```
   HYPERLIQUID_PRIVATE_KEY=your_private_key
   HYPERLIQUID_ACCOUNT_ADDRESS=your_account_address
   HYPERLIQUID_MONITORING_ADDRESS=your_monitoring_address
   ```

## Usage

Start the bot and UI:

```
python -m app.main
```

Access the web dashboard at http://localhost:5000

The webhook server will be available at http://localhost:8000/webhook

## Configuration

Edit the bot settings in `app/config.py` or by setting environment variables.

Available settings:
- `HYPERLIQUID_PRIVATE_KEY`: Your HyperLiquid private key
- `HYPERLIQUID_ACCOUNT_ADDRESS`: Your account address
- `HYPERLIQUID_MONITORING_ADDRESS`: Your monitoring address
- `ASSET_NAME`: Trading pair (default: "ETH")
- `LEVERAGE`: Trading leverage (default: 5)
- `IS_CROSS`: Whether to use cross margin (default: true)

## Dashboard

The web dashboard provides:
- Real-time account balance
- Open positions
- Trade history with P/L metrics
- Account balance history chart
- Start/stop bot functionality

## Project Structure

- `/app`: Core bot functionality
  - `main.py`: Main application entry point
  - `config.py`: Configuration settings
  - `exchange_manager.py`: Exchange interaction logic
  - `webhook.py`: Webhook server for trade signals
- `/ui`: User interface
  - `server.py`: Flask web server
  - `database.py`: Local database for trade history
  - `/templates`: HTML templates
  - `/static`: CSS, JavaScript, and other static files

## License

MIT