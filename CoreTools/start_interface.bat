@echo off
echo Starting Hegemonic Strategic Interface Server...
echo ------------------------------------------------
echo This script starts a local web server to bypass CORS restrictions
echo allowing the interface to communicate with Ollama.
echo.
echo Server running at: http://localhost:8000
echo.

start "" "http://localhost:8000/Hegemonic Strategic Interface v4.9_Fixed.html"
python -m http.server 8000
