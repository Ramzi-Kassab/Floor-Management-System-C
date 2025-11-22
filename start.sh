#!/bin/bash
# Floor Management System - Quick Start Script
# This script activates the virtual environment and starts the Django server

set -e

echo "🚀 Starting Floor Management System..."
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
else
    echo "❌ Virtual environment not found!"
    echo "Run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file from .env.example"
    else
        echo "❌ No .env.example found. Please create .env manually."
        exit 1
    fi
fi

# Run system check
echo "🔍 Running system check..."
python manage.py check --deploy 2>/dev/null || python manage.py check

# Check for pending migrations
echo "🔄 Checking for pending migrations..."
if python manage.py showmigrations | grep -q "\[ \]"; then
    echo "⚠️  You have pending migrations. Run: python manage.py migrate"
    read -p "Do you want to run migrations now? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python manage.py migrate
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ Starting Django development server..."
echo ""
echo "🌐 Server will be available at:"
echo "   - Local: http://127.0.0.1:8000/"

# Detect if running in Codespaces
if [ -n "$CODESPACE_NAME" ]; then
    echo "   - Codespaces: https://${CODESPACE_NAME}-8000.app.github.dev/"
fi

echo ""
echo "📝 Press Ctrl+C to stop the server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start the server
# Use 0.0.0.0 to allow external connections (needed for Codespaces)
python manage.py runserver 0.0.0.0:8000
