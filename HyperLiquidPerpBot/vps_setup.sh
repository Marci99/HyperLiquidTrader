#!/bin/bash
# HyperLiquidPerpBot VPS Setup Script
# Run this script on your VPS to set up the environment

# Exit on error
set -e

echo "============================================"
echo "HyperLiquidPerpBot VPS Setup Script"
echo "============================================"

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install dependencies
echo "Installing required packages..."
sudo apt install -y python3-pip python3-venv git curl wget

# Install Node.js and PM2
echo "Installing Node.js and PM2..."
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g pm2

# Create directory structure
echo "Creating application directory..."
mkdir -p ~/hyperliquid-bot
cd ~/hyperliquid-bot

# Create Python virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Prompt for path to bot files
echo ""
echo "Please enter the path where your bot files are located:"
echo "1. I will clone from Git"
echo "2. I have uploaded files to this server"
read -p "Enter your choice (1 or 2): " file_choice

if [ "$file_choice" = "1" ]; then
    read -p "Enter Git repository URL: " git_url
    git clone $git_url .
elif [ "$file_choice" = "2" ]; then
    echo "Please ensure all files are copied to ~/hyperliquid-bot before continuing."
    read -p "Press Enter to continue..."
else
    echo "Invalid choice. Exiting."
    exit 1
fi

# Install requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file
echo "Setting up environment variables..."
if [ ! -f .env ]; then
    echo "Creating .env file..."
    read -p "Enter your HYPERLIQUID_PRIVATE_KEY: " private_key
    read -p "Enter your HYPERLIQUID_ACCOUNT_ADDRESS: " account_address
    read -p "Enter your HYPERLIQUID_MONITORING_ADDRESS: " monitoring_address
    
    echo "HYPERLIQUID_PRIVATE_KEY=$private_key" > .env
    echo "HYPERLIQUID_ACCOUNT_ADDRESS=$account_address" >> .env
    echo "HYPERLIQUID_MONITORING_ADDRESS=$monitoring_address" >> .env
    echo ".env file created."
else
    echo ".env file already exists, skipping..."
fi

# Configure firewall
echo "Configuring firewall..."
sudo ufw allow 5001/tcp
sudo ufw allow 8000/tcp
sudo ufw status

# Create start script
echo "Creating startup script..."
cat > start_bot.sh << 'EOL'
#!/bin/bash
cd ~/hyperliquid-bot
source venv/bin/activate
python run.py
EOL

chmod +x start_bot.sh

# Set up PM2
echo "Setting up PM2 for process management..."
pm2 start ./start_bot.sh --name hyperliquid-bot

# Configure PM2 to start on boot
echo "Configuring PM2 to start on system boot..."
pm2 startup
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u $USER --hp /home/$USER
pm2 save

echo ""
echo "============================================"
echo "Setup completed successfully!"
echo "============================================"
echo ""
echo "Your HyperLiquidPerpBot is now running."
echo "- Web UI: http://$(hostname -I | awk '{print $1}'):5001"
echo "- Webhook endpoint: http://$(hostname -I | awk '{print $1}'):8000/webhook"
echo ""
echo "To check the bot status: pm2 status"
echo "To view logs: pm2 logs hyperliquid-bot"
echo ""
echo "For more information, refer to the DEPLOYMENT.md file."