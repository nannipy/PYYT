from flask import Flask, request, render_template, send_file
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Necessario per Vercel
if __name__ == '__main__':
    app.run()