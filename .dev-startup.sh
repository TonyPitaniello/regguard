#!/bin/bash
# Simple dev startup - runs both servers in the foreground

echo "🚀 RegGuard Dev Startup"
echo "Starting backend on port 8000 and frontend on port 5173..."
echo ""

# Start both in parallel
(cd backend && python3 -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload) &
BACKEND_PID=$!

sleep 3

(cd frontend && npm run dev) &
FRONTEND_PID=$!

echo "✅ Backend PID: $BACKEND_PID (port 8000)"
echo "✅ Frontend PID: $FRONTEND_PID (port 5173)"
echo ""
echo "Access the app at: http://localhost:5173"
echo "Backend API at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for both
wait
