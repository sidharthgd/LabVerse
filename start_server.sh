#!/bin/bash

# LabVerse FastAPI Server Startup Script
# This script starts the FastAPI server for testing

echo "🚀 Starting LabVerse FastAPI Server"
echo "Server will be available at: http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""

# Change to the backend directory
cd backend

# Start the FastAPI server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
