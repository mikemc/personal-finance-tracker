import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')

# Create data directory in project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
DATA_DIR.mkdir(exist_ok=True)

# File paths
TRANSACTIONS_FILE = DATA_DIR / 'transactions.tsv'
BALANCES_FILE = DATA_DIR / 'balances.tsv'

