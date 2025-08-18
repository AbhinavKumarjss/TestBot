#!/bin/bash

# GeneralChatbot Complete Deployment Script
# This script deploys both frontend and backend on a single EC2 instance

set -e  # Exit on any error

echo "🚀 Starting GeneralChatbot Complete Deployment..."

# Function to print status
print_status() {
    echo "📋 $1"
}

# Function to print success
print_success() {
    echo "✅ $1"
}

# Function to print error
print_error() {
    echo "❌ $1"
}

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Node.js 18+
print_status "Installing Node.js 18+..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python 3.11+
print_status "Installing Python 3.11+..."
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Nginx
print_status "Installing Nginx..."
sudo apt install nginx -y

# Install PM2
print_status "Installing PM2..."
sudo npm install -g pm2

# Install build essentials
print_status "Installing build essentials..."
sudo apt install build-essential -y

# Create application directory
print_status "Creating application directory..."
sudo mkdir -p /var/www/generalchatbot
sudo chown -R $USER:$USER /var/www/generalchatbot

# Copy application files
print_status "Copying application files..."
cp -r . /var/www/generalchatbot/

# Set up environment variables
print_status "Setting up environment variables..."
sudo mkdir -p /etc/environment.d

# Backend environment variables
sudo tee /etc/environment.d/generalchatbot.conf > /dev/null << EOF
# GeneralChatbot Environment Variables
OPENAI_API_KEY=sk-proj-H30vwBURw4TJmZfvrEcXcDkfxoE8o2-ddpqDFzi-e4Evd5KygtUhks8rwZrXQMhZuE8rWr6Wt_T3BlbkFJy5wG96kVNNYOFdSkCPgDjUp7HaUXMAT_F8nQU8HXhg5eyGJ3RL9VNI5NnstWkM6oun2KJlMA
PINECONE_API_KEY=pcsk_3ERFN3_KtTcKvRRWPLUMRw3tAijQG4nxCv7zyYn2UYnfqhpWZauDiiGyZf9Q583CWLqLhx
ELEVEN_API_KEY=sk_681c5b0b20bec4e9948806833d18063721553711427efd11
PORT=8000
HOST=0.0.0.0
ENVIRONMENT=production
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
EOF

# Frontend environment variables
sudo tee /etc/environment.d/generalchatbot-frontend.conf > /dev/null << EOF
# GeneralChatbot Frontend Environment Variables
VITE_WEBSOCKET_URL=wss://yourdomain.com/api/user/ws
VITE_SERVER_API_URL=https://yourdomain.com/api/admin
EOF

# Set up backend
print_status "Setting up backend..."
cd /var/www/generalchatbot/Server
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Build frontend
print_status "Building frontend..."
cd /var/www/generalchatbot/Frontend
npm install
npm run build

# Configure Nginx
print_status "Configuring Nginx..."
sudo tee /etc/nginx/sites-available/generalchatbot > /dev/null << EOF
server {
    listen 80;
    server_name _;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Frontend static files
    location / {
        root /var/www/generalchatbot/Frontend/dist;
        try_files \$uri \$uri/ /index.html;

        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;

        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket endpoint
    location /api/user/ws {
        proxy_pass http://127.0.0.1:8000/api/user/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # WebSocket specific settings
        proxy_buffering off;
        proxy_cache off;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_set_header Host \$host;
    }

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript;
}
EOF

# Enable site and restart Nginx
sudo ln -sf /etc/nginx/sites-available/generalchatbot /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl restart nginx
sudo systemctl enable nginx

# Start backend with PM2
print_status "Starting backend with PM2..."
cd /var/www/generalchatbot/Server
source venv/bin/activate
pm2 start "python server.py" --name "generalchatbot-backend" --cwd /var/www/generalchatbot/Server
pm2 save
pm2 startup

# Configure firewall
print_status "Configuring firewall..."
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

print_success "Deployment completed successfully!"
print_success "Your application is now running at: http://your-ec2-public-ip"
print_success "Backend API: http://your-ec2-public-ip/api"
print_success "WebSocket: ws://your-ec2-public-ip/api/user/ws"

echo ""
echo "🔧 Next steps:"
echo "1. Update domain URLs in environment variables"
echo "2. Set up SSL certificate for HTTPS"
echo "3. Configure custom domain in Route 53"
echo "4. Set up monitoring and alerts" 