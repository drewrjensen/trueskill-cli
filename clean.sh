#!/bin/bash
echo "Cleaning project..."
rm -rf build/
rm -rf __pycache__/
rm -f *.spec
rm -rf venv/
echo "Clean complete."