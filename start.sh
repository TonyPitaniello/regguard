#!/bin/bash
# Startup script for Render - changes to backend directory then starts FastAPI
cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000
