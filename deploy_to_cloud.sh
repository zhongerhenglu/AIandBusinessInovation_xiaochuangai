#!/bin/bash

echo "=========================================="
echo "  Super Agent Cloud Deployment Script"
echo "=========================================="

if [ -z "$1" ]; then
    echo "Usage: $0 <server_ip_or_hostname>"
    echo "Example: $0 root@123.123.123.123"
    exit 1
fi

SERVER=$1
APP_DIR="/opt/super_agent"

echo ""
echo "1. Connecting to server: $SERVER"
echo ""

ssh $SERVER << 'EOF'
    echo "=========================================="
    echo "  Step 1: Update system packages"
    echo "=========================================="
    apt-get update && apt-get upgrade -y

    echo ""
    echo "=========================================="
    echo "  Step 2: Install required packages"
    echo "=========================================="
    apt-get install -y python3 python3-pip python3-venv git docker.io docker-compose

    echo ""
    echo "=========================================="
    echo "  Step 3: Create application directory"
    echo "=========================================="
    mkdir -p /opt/super_agent
    cd /opt/super_agent

    echo ""
    echo "=========================================="
    echo "  Step 4: Clone repository"
    echo "=========================================="
    if [ -d ".git" ]; then
        git pull origin main
    else
        git clone https://github.com/zhongerhenglu/AIandBusinessInovation_xiaochuangai.git .
    fi

    echo ""
    echo "=========================================="
    echo "  Step 5: Set up environment"
    echo "=========================================="
    if [ ! -f ".env" ]; then
        cp .env.example .env
        echo ""
        echo "Please edit .env file with your API keys:"
        echo "nano /opt/super_agent/.env"
    fi

    echo ""
    echo "=========================================="
    echo "  Step 6: Build and start Docker container"
    echo "=========================================="
    docker-compose up -d --build

    echo ""
    echo "=========================================="
    echo "  Step 7: Check container status"
    echo "=========================================="
    docker ps -a

    echo ""
    echo "=========================================="
    echo "  Deployment completed!"
    echo "=========================================="
    echo ""
    echo "To check logs:"
    echo "  docker logs -f super_agent_service"
    echo ""
    echo "To restart service:"
    echo "  docker-compose restart"
    echo ""
    echo "To stop service:"
    echo "  docker-compose down"
EOF

echo ""
echo "=========================================="
echo "  Deployment to $SERVER completed!"
echo "=========================================="