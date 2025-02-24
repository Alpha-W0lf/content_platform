#!/bin/bash

# Exit on error
set -e

# Get the frontend directory (we're already in it)
FRONTEND_DIR="$(pwd)"

# Run cleanup script first
if [ -f "./cleanup.sh" ]; then
    ./cleanup.sh
else
    echo "Error: cleanup.sh not found in current directory"
    exit 1
fi

# Function to detect if we're on M2 Max or M2 Pro
detect_machine() {
    local cpu_model
    cpu_model=$(sysctl -n machdep.cpu.brand_string)
    if [[ $cpu_model == *"M2 Max"* ]]; then
        echo "M2_MAX"
    elif [[ $cpu_model == *"M2 Pro"* ]]; then
        echo "M2_PRO"
    else
        echo "UNKNOWN"
    fi
}

# Create logs directory if it doesn't exist
mkdir -p "logs/frontend/runtime_logs"

# Detect which machine we're on
MACHINE_TYPE=$(detect_machine)
echo "Detected machine type: $MACHINE_TYPE"

# Set the API URL based on machine type
if [ "$MACHINE_TYPE" = "M2_MAX" ]; then
    # Running on the server machine, use localhost
    API_URL="http://localhost:8000"
    echo "Running client on SERVER machine (M2 Max 💻⚡️🔥) - using localhost for API"
    echo "Switch to M2 Pro machine to distribute load a little more efficiently 😉"
elif [ "$MACHINE_TYPE" = "M2_PRO" ]; then
    # Running on the client machine, use the M2 Max's IP
    API_URL="http://192.168.1.167:8000"
    echo "Running client on CLIENT machine (M2 Pro 💻🛰️) (Preferred 👍) - using remote server at $API_URL"
else
    echo "⚠️ Could not detect machine type. Please specify the API URL manually."
    read -p "Enter API URL (default: http://192.168.1.167:8000): " user_input
    API_URL=${user_input:-"http://192.168.1.167:8000"}
fi

# Update .env.local with the correct API URL
echo "Updating API configuration..."
if [ -f ".env.local" ]; then
    # Update existing NEXT_PUBLIC_API_URL if it exists
    sed -i '' "s|^NEXT_PUBLIC_API_URL=.*|NEXT_PUBLIC_API_URL=${API_URL}|" .env.local
else
    # Create new .env.local if it doesn't exist
    echo "NEXT_PUBLIC_API_URL=${API_URL}" > .env.local
fi

# Start Next.js development server
echo "👨‍💻 Starting Next.js development server..."
nohup npm run dev > logs/frontend/runtime_logs/server.log 2>&1 &
NEXT_PID=$!
disown $NEXT_PID

# Save PID for cleanup
echo $NEXT_PID > logs/frontend/next.pid

# Wait briefly to check if the process is still running
sleep 3
if ps -p $NEXT_PID > /dev/null; then
    echo "✅✅ Next.js development server started successfully ✅✅ (PID: $NEXT_PID)"
    echo "Logs available at: logs/frontend/runtime_logs/server.log"
    echo "Access the application at: 🖥️ http://localhost:3000"
else
    echo "‼️ Error: Next.js development server failed to start"
    cat logs/frontend/runtime_logs/server.log
    exit 1
fi