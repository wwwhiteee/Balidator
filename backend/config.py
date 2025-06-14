from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env at project root
load_dotenv(Path(__file__).resolve().parent.parent / '.env')

# JWT settings
JWT_SECRET = os.getenv('JWT_SECRET', 'changeme')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '15'))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv('REFRESH_TOKEN_EXPIRE_MINUTES', '60'))

# Database
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./data/oee.db')

# InfluxDB
INFLUXDB_URL = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN', 'my-token')
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG', 'oee')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET', 'oee')

# Acquisition settings
ACQUISITION_INTERVAL_SECONDS = int(os.getenv('ACQUISITION_INTERVAL_SECONDS', '5'))

# Grafana (for completeness, though backend does not use them)
GRAFANA_USER = os.getenv('GRAFANA_USER', 'admin')
GRAFANA_PASSWORD = os.getenv('GRAFANA_PASSWORD', 'admin')
