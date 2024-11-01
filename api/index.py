import sys
import os

# Aggiungi la directory corrente al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

from app import app as application