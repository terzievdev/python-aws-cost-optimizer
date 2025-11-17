import os
from datetime import datetime

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_ACCOUNT_ID = os.getenv('AWS_ACCOUNT_ID', '411203042419')

# All AWS regions to scan
AWS_REGIONS = [
    'us-east-1', 'us-west-1', 'us-west-2',
    'eu-west-1', 'eu-central-1', 'ap-southeast-1'
]

# Thresholds for recommendations
IDLE_CPU_THRESHOLD = 5.0  # CPU % below this = idle
IDLE_DAYS_THRESHOLD = 7    # Days idle before recommendation
EBS_UNATTACHED_DAYS = 30   # Days unattached before cleanup

# Cost settings
EC2_HOURLY_COST = {
    't2.micro': 0.0116,
    't2.small': 0.023,
    't2.medium': 0.0464,
    't3.micro': 0.0104,
    't3.small': 0.0208,
    't3.medium': 0.0416,
}

# Scheduler settings
SCAN_SCHEDULE_HOUR = 2  # Run daily at 2 AM
REPORT_EMAIL = os.getenv('REPORT_EMAIL', 'your-email@example.com')

# Flask settings
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5000
SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'super-secret-dev-key-change-in-prod')

# Data directories
SCAN_DATA_DIR = 'data/scans'
RECOMMENDATIONS_DIR = 'data/recommendations'

# Create directories if they don't exist
os.makedirs(SCAN_DATA_DIR, exist_ok=True)
os.makedirs(RECOMMENDATIONS_DIR, exist_ok=True)

# Current timestamp for filenames
def get_timestamp():
    return datetime.now().strftime('%Y%m%d_%H%M%S')
