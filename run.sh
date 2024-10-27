#!/bin/bash

echo "Starting web server for UI..."

python3 -m http.server --directory ./ui/ &

echo "Starting robo3 script..."
python3 robo3.py

