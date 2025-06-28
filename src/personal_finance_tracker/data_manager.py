import pandas as pd
from datetime import datetime
from . import config

class DataManager:
    def __init__(self):
        # Initialize files if they don't exist
        if not config.TRANSACTIONS_FILE.exists():
            self.init_transactions_file()
        if not config.BALANCES_FILE.exists():
            self.init_balances_file()

    def init_transactions_file(self):
        """Initialize transactions TSV file with headers"""
        headers = [
            'transaction_id', 'account_id', 'account_name', 'amount',
            'date', 'description', 'category', 'merchant_name'
        ]
        df = pd.DataFrame(columns=headers)
        df.to_csv(config.TRANSACTIONS_FILE, sep='\t', index=False)

    def init_balances_file(self):
        """Initialize balances TSV file with headers"""
        headers = [
            'account_id', 'account_name', 'account_type', 'balance_current',
            'balance_available', 'last_updated'
        ]
        df = pd.DataFrame(columns=headers)
        df.to_csv(config.BALANCES_FILE, sep='\t', index=False)

    def save_transactions(self, transactions, accounts):
        """Save new transactions to TSV file"""
        # Load existing data
        existing_df = pd.read_csv(config.TRANSACTIONS_FILE, sep='\t')
        existing_ids = set(existing_df['transaction_id'].values)

        # Create account lookup
        account_lookup = {acc['account_id']: acc['name'] for acc in accounts}

        # Process new transactions
        new_rows = []
        for trans in transactions:
            if trans['transaction_id'] not in existing_ids:
                row = {
                    'transaction_id': trans['transaction_id'],
                    'account_id': trans['account_id'],
                    'account_name': account_lookup.get(trans['account_id'], 'Unknown'),
                    'amount': -trans['amount'],  # Plaid uses negative for expenses
                    'date': trans['date'],
                    'description': trans['name'],
                    'category': ', '.join(trans.get('category', [])),
                    'merchant_name': trans.get('merchant_name', '')
                }
                new_rows.append(row)

        if new_rows:
            new_df = pd.DataFrame(new_rows)
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            combined_df.to_csv(config.TRANSACTIONS_FILE, sep='\t', index=False)
            print(f"Added {len(new_rows)} new transactions")
        else:
            print("No new transactions found")

    def save_balances(self, accounts):
        """Save current account balances"""
        rows = []
        for account in accounts:
            row = {
                'account_id': account['account_id'],
                'account_name': account['name'],
                'account_type': account['type'],
                'balance_current': account['balances']['current'],
                'balance_available': account['balances'].get('available', ''),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            rows.append(row)

        df = pd.DataFrame(rows)
        df.to_csv(config.BALANCES_FILE, sep='\t', index=False)
        print(f"Updated balances for {len(rows)} accounts")

    def get_latest_balances(self):
        """Get the most recent balance data"""
        try:
            df = pd.read_csv(config.BALANCES_FILE, sep='\t')
            return df
        except FileNotFoundError:
            return pd.DataFrame()
