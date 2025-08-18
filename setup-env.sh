#!/bin/bash

# Setup Environment Variables on EC2
# This script sets environment variables at the system level

echo "🔧 Setting up environment variables on EC2..."

# Backend environment variables
sudo tee /etc/environment.d/generalchatbot.conf > /dev/null << EOF
# GeneralChatbot Environment Variables
OPENAI_API_KEY=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
PINECONE_API_KEY=pcsk_3ERFN3_KtTcKvRRWPLUMRw3tAijQG4nxCv7zyYn2UYnfqhpWZauDiiGyZf9Q583CWLqLhx
ELEVEN_API_KEY=sk_681c5b0b20bec4e9948806833d18063721553711427efd11

# Server Configuration
PORT=8000
HOST=0.0.0.0
ENVIRONMENT=production

# CORS Configuration (update with your domain)
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
EOF

# Frontend environment variables (for build time)
sudo tee /etc/environment.d/generalchatbot-frontend.conf > /dev/null << EOF
# Frontend Environment Variables
VITE_WEBSOCKET_URL=ws://localhost:8000/api/user/ws
VITE_SERVER_API_URL=http://localhost:8000/api/admin
EOF

# Make the files readable by the application user
sudo chown ubuntu:ubuntu /etc/environment.d/generalchatbot.conf
sudo chown ubuntu:ubuntu /etc/environment.d/generalchatbot-frontend.conf
sudo chmod 644 /etc/environment.d/generalchatbot.conf
sudo chmod 644 /etc/environment.d/generalchatbot-frontend.conf

# Source the environment variables for current session
export $(cat /etc/environment.d/generalchatbot.conf | xargs)
export $(cat /etc/environment.d/generalchatbot-frontend.conf | xargs)

echo "✅ Environment variables set successfully!"
echo "📋 Variables set:"
echo "  - OPENAI_API_KEY"
echo "  - PINECONE_API_KEY" 
echo "  - ELEVEN_API_KEY"
echo "  - VITE_WEBSOCKET_URL"
echo "  - VITE_SERVER_API_URL"
echo ""
echo "🔄 Please restart your application for changes to take effect:"
echo "   pm2 restart generalchatbot-backend"
echo "   sudo systemctl reload nginx" 