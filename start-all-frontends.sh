#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Multi-Frontend Development Environment${NC}"
echo -e "${BLUE}===============================================${NC}"

# Function to start a frontend
start_frontend() {
    local name=$1
    local port=$2
    local path=$3
    
    echo -e "${YELLOW}📦 Starting $name on port $port...${NC}"
    cd "$path"
    
    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}📥 Installing dependencies for $name...${NC}"
        npm install
    fi
    
    # Start the frontend in background
    npm start &
    
    echo -e "${GREEN}✅ $name started successfully${NC}"
    cd ..
}

# Start all frontends
echo -e "${BLUE}🔧 Starting Frontend Applications...${NC}"

start_frontend "Admin Frontend" "3001" "frontend-admin"
start_frontend "Teacher Frontend" "3002" "frontend-teacher" 
start_frontend "Student Frontend" "3003" "frontend-student"
start_frontend "Main Frontend" "3000" "frontend"

echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}🎉 All frontends are starting up!${NC}"
echo -e "${BLUE}📱 Frontend URLs:${NC}"
echo -e "  ${YELLOW}Admin:${NC}    http://localhost:3001"
echo -e "  ${YELLOW}Teacher:${NC}  http://localhost:3002"
echo -e "  ${YELLOW}Student:${NC}  http://localhost:3003"
echo -e "  ${YELLOW}Main:${NC}     http://localhost:3000"
echo -e "${BLUE}===============================================${NC}"
echo -e "${RED}⚠️  Press Ctrl+C to stop all frontends${NC}"

# Wait for all background processes
wait
