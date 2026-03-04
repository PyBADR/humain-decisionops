#!/bin/bash
set -e

echo "=== HUMAIN DecisionOps Platform Starting ==="
echo "Database URL: ${DATABASE_URL:0:30}..."
echo "Heuristic Mode: $HEURISTIC_MODE"
echo "Port: $PORT"

# Start backend API server
echo "Starting Backend API on port $PORT..."
cd /app/backend
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} &
BACKEND_PID=$!

# Wait for backend to be ready
echo "Waiting for backend to start..."
sleep 5

# Start frontend Next.js server
echo "Starting Frontend on port 3000..."
cd /app/frontend
NODE_ENV=production node server.js &
FRONTEND_PID=$!

echo "=== Platform Ready ==="
echo "Backend API: http://localhost:$PORT"
echo "Frontend UI: http://localhost:3000"
echo "API Docs: http://localhost:$PORT/docs"

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?
