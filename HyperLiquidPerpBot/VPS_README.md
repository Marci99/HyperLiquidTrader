# HyperLiquidPerpBot

A sophisticated trading automation tool designed for cryptocurrency perpetual futures trading on HyperLiquid exchange.

## Overview

HyperLiquidPerpBot automates trading on the HyperLiquid exchange by receiving signals via webhooks (typically from TradingView) and executing trades based on these signals. It also provides a web dashboard for monitoring trading activity.

## Features

- **Webhook Integration**: Receive trading signals from TradingView or other platforms
- **Automated Trading**: Execute trades on HyperLiquid exchange
- **Web Dashboard**: Monitor account balance, open positions, and trade history
- **Secure Credential Management**: Environment variable based configuration
- **Position Size Configuration**: Flexible position sizing

## Getting Started

### Installation

See the [DEPLOYMENT.md](DEPLOYMENT.md) file for detailed installation instructions, including:
- VPS setup guide
- System requirements
- Configuration instructions
- Deployment best practices

### Requirements

- Python 3.9+
- Required Python packages (listed in requirements.txt)
- HyperLiquid API credentials
- (Optional) Domain name for production use

### Configuration

Create a `.env` file with the following variables:

```
HYPERLIQUID_PRIVATE_KEY=your_private_key
HYPERLIQUID_ACCOUNT_ADDRESS=your_account_address
HYPERLIQUID_MONITORING_ADDRESS=your_monitoring_address
```

## Usage

### Webhook Endpoint

Send POST requests to `/webhook` with the following JSON format:

```json
{
  "action": "BUY",     // or "SELL" or "CLOSE"
  "asset": "BTC",      // or "ETH" or other supported assets
  "size": 0.1          // position size to open/close
}
```

### Dashboard

Access the web dashboard at port 5001 (default) to view:
- Account balance and balance history
- Open positions
- Trade history
- Bot status

## Architecture

- **Backend**: Python with FastAPI for the webhook server
- **Frontend**: Flask-based web interface with Bootstrap
- **Database**: SQLite for persistence
- **Process Management**: PM2 (for production deployment)

## Support

For questions or issues, please refer to the troubleshooting section in the [DEPLOYMENT.md](DEPLOYMENT.md) file.

## License

This project is licensed under the MIT License - see the LICENSE file for details.