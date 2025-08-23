#!/bin/bash
gunicorn major_banks_calc:app --bind 0.0.0.0:$PORT
chmod +x start.sh