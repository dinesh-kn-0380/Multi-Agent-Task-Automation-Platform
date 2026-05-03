#!/bin/bash
# Startup script for the production container
# Runs both the Flask backend and Next.js frontend concurrently

set -e

echo "🤖 Starting Multi-Agent Task Automation Platform..."

# Start Flask backend in background
echo "→ Starting Flask backend on port ${PORT_BACKEND:-5000}..."
cd /app
gunicorn \
  --worker-class sync \
  --workers 2 \
  --threads 4 \
  --timeout 120 \
  --bind "0.0.0.0:${PORT_BACKEND:-5000}" \
  backend.api.server:app &

# Start Next.js frontend
echo "→ Starting Next.js frontend on port ${PORT_FRONTEND:-3000}..."
cd /app/frontend
PORT=${PORT_FRONTEND:-3000} node_modules/.bin/next start &

# Wait for any process to exit
wait -n

echo "❌ A service exited unexpectedly. Shutting down."
exit 1
