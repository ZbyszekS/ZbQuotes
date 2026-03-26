import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from zb_quotes.models import *
from sqlalchemy.orm import configure_mappers

print("---------> Configuring mappers...")
configure_mappers()
print("---------> Mappers configured successfully.")