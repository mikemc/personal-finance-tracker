# Personal Finance Tracker

A simple personal finance tracker that uses the Plaid API to fetch transaction and balance data from your bank accounts.

## Features

- Connect to bank accounts via Plaid API
- Fetch transaction history and current balances
- Store data locally in TSV files
- Support for major banks

## Setup

1. Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Clone or create this project
3. Install dependencies: `uv sync`
4. Copy `.env.example` to `.env` and add your Plaid credentials
5. Run: `uv run python run.py`

## Sandbox Testing

For testing, use Plaid's sandbox environment with these credentials:
- Username: `user_good`, Password: `pass_good`
- This will create fake accounts with sample data

## Usage

1. Create link token to connect accounts
2. Use Plaid Link to authorize accounts
3. Fetch transactions and balances
4. View data in the `data/` directory as TSV files
