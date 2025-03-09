# HyperLiquidPerpBot VPS Deployment Guide

This guide provides detailed instructions for deploying the HyperLiquidPerpBot on a Virtual Private Server (VPS).

## Prerequisites

- A VPS with Ubuntu 20.04 or later (recommended providers: DigitalOcean, Linode, AWS, Vultr)
- Basic knowledge of terminal/command line usage
- Your HyperLiquid API credentials (private key and addresses)
- SSH access to your VPS

## Step 1: Set Up Your VPS

After creating your VPS instance:

1. Connect to your VPS via SSH:
   ```bash
   ssh username@your_server_ip
   ```

2. Update the system:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

3. Install essential packages:
   ```bash
   sudo apt install -y python3-pip python3-venv git curl wget
   ```

## Step 2: Install Node.js and PM2

PM2 is a process manager that will keep your bot running even after you disconnect from the server:

```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installation
node --version
npm --version

# Install PM2 globally
sudo npm install -g pm2
```

## Step 3: Set Up the Bot

1. Create a directory for the bot:
   ```bash
   mkdir -p ~/hyperliquid-bot
   cd ~/hyperliquid-bot
   ```

2. Clone the repository (if using Git):
   ```bash
   git clone https://your-repository-url.git .
   ```
   
   OR Transfer files using SCP (from your local machine):
   ```bash
   # Run this on your local machine, not on the VPS
   scp -r ./HyperLiquidPerpBot/* username@your_server_ip:~/hyperliquid-bot/
   ```

3. Set up Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create and configure the .env file:
   ```bash
   nano .env
   ```
   
   Add the following content to the .env file:
   ```
   HYPERLIQUID_PRIVATE_KEY=your_private_key
   HYPERLIQUID_ACCOUNT_ADDRESS=your_account_address
   HYPERLIQUID_MONITORING_ADDRESS=your_monitoring_address
   ```
   
   Save and exit: Press `Ctrl+X`, then `Y`, then `Enter`

## Step 4: Configure Network and Firewall

1. Make sure ports 5001 (UI) and 8000 (webhook) are accessible:
   ```bash
   sudo ufw allow 5001/tcp
   sudo ufw allow 8000/tcp
   ```

   If UFW is not enabled, run:
   ```bash
   sudo ufw enable
   ```

2. Verify firewall status:
   ```bash
   sudo ufw status
   ```

## Step 5: Run the Bot with PM2

PM2 will ensure your bot continues running after you log out and automatically restarts if it crashes:

1. Create a startup script:
   ```bash
   nano start_bot.sh
   ```
   
   Add the following content:
   ```bash
   #!/bin/bash
   cd ~/hyperliquid-bot
   source venv/bin/activate
   python run.py
   ```
   
   Save and exit: Press `Ctrl+X`, then `Y`, then `Enter`

2. Make the script executable:
   ```bash
   chmod +x start_bot.sh
   ```

3. Start the bot with PM2:
   ```bash
   pm2 start ./start_bot.sh --name hyperliquid-bot
   ```

4. Set PM2 to start on boot:
   ```bash
   pm2 startup
   ```
   
   Run the command that PM2 outputs.

5. Save the current PM2 configuration:
   ```bash
   pm2 save
   ```

6. Check status:
   ```bash
   pm2 status
   ```

## Step 6: Access Your Bot

After deployment, your bot can be accessed at:

- Web UI: `http://your_server_ip:5001`
- Webhook endpoint: `http://your_server_ip:8000/webhook`

## Step 7: Set Up TradingView Alerts

1. In TradingView, create a new alert
2. Configure it to send a webhook to `http://your_server_ip:8000/webhook`
3. Use the following JSON payload format:
   ```json
   {
     "action": "BUY",     // or "SELL" or "CLOSE"
     "asset": "BTC",      // or "ETH" or other supported assets
     "size": 0.1          // position size to open/close
   }
   ```

## Step 8: Domain Name and SSL (Optional but Recommended)

For a more professional setup, you can configure a domain name and SSL:

1. Point your domain to your server IP through your domain registrar
2. Install Nginx:
   ```bash
   sudo apt install -y nginx
   ```

3. Configure Nginx as a reverse proxy:
   ```bash
   sudo nano /etc/nginx/sites-available/hyperliquid-bot
   ```
   
   Add configuration:
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       location /webhook {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }

       location / {
           proxy_pass http://localhost:5001;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

4. Enable the site:
   ```bash
   sudo ln -s /etc/nginx/sites-available/hyperliquid-bot /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

5. Install SSL with Certbot:
   ```bash
   sudo apt install -y certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

## Maintenance and Monitoring

### Viewing Logs

```bash
# View real-time logs
pm2 logs hyperliquid-bot

# View specific number of lines
pm2 logs hyperliquid-bot --lines 100
```

### Managing the Bot

```bash
# Restart the bot
pm2 restart hyperliquid-bot

# Stop the bot
pm2 stop hyperliquid-bot

# Start the bot
pm2 start hyperliquid-bot

# Check resource usage
pm2 monit
```

### Updating the Bot

1. Stop the bot:
   ```bash
   pm2 stop hyperliquid-bot
   ```

2. Get the latest code (if using Git):
   ```bash
   cd ~/hyperliquid-bot
   git pull
   ```
   
   OR transfer new files using SCP.

3. Activate virtual environment and update dependencies:
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Restart the bot:
   ```bash
   pm2 restart hyperliquid-bot
   ```

## Troubleshooting

### Bot Not Starting

Check the logs:
```bash
pm2 logs hyperliquid-bot
```

### Can't Access UI or Webhook

Verify the firewall settings:
```bash
sudo ufw status
```

Check if the services are running:
```bash
pm2 status
```

### Database Issues

Backup the database:
```bash
cp ~/hyperliquid-bot/bot_data.db ~/hyperliquid-bot/bot_data.db.backup
```

## Security Best Practices

1. Keep your system updated:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. Set up automatic updates:
   ```bash
   sudo apt install -y unattended-upgrades
   sudo dpkg-reconfigure -plow unattended-upgrades
   ```

3. Consider setting up a non-root user with sudo privileges for added security.

4. Regularly backup your .env file and database.

## Support

If you encounter any issues, please:
1. Check the application logs using `pm2 logs hyperliquid-bot`
2. Review the configuration in the .env file
3. Contact support if problems persist