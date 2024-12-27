#!/bin/bash
source /eniac_venv/bin/activate
cd /app

daphne -b 0.0.0.0 -p 8001 BackEnd.asgi:application