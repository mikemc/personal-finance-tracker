from .plaid_client import PlaidClient
from .data_manager import DataManager
import pandas as pd

def main():
    plaid_client = PlaidClient()
    data_manager = DataManager()

    print("Personal Finance Tracker")
    print("=" * 30)

    while True:
        print("\nOptions:")
        print("1. Connect new account (get link token)")
        print("2. Fetch transactions and balances")
        print("3. View current balances")
        print("4. Exit")

        choice = input("\nEnter your choice (1-4): ")

        if choice == '1':
            # In sandbox mode, you'll use the Plaid Link demo
            link_token = plaid_client.create_link_token()
            print(f"\nLink token created: {link_token}")
            print("\nFor sandbox testing, use the Plaid Link demo:")
            print("https://plaid.com/docs/quickstart/")
            print("\nUse any of the sandbox credentials provided by Plaid")

        elif choice == '2':
            access_token = input("Enter your access token: ")
            try:
                # Get accounts
                accounts = plaid_client.get_accounts(access_token)
                print(f"\nFound {len(accounts)} accounts")

                # Get transactions
                transactions = plaid_client.get_transactions(access_token)
                print(f"Found {len(transactions)} transactions")

                # Save to files
                data_manager.save_transactions(transactions, accounts)
                data_manager.save_balances(accounts)

            except Exception as e:
                print(f"Error fetching data: {e}")

        elif choice == '3':
            balances_df = data_manager.get_latest_balances()
            if not balances_df.empty:
                print("\nCurrent Account Balances:")
                print("-" * 50)
                for _, row in balances_df.iterrows():
                    print(f"{row['account_name']}: ${row['balance_current']:.2f}")
                    if pd.notna(row['balance_available']):
                        print(f"  Available: ${row['balance_available']:.2f}")
                    print(f"  Last Updated: {row['last_updated']}")
                    print()
            else:
                print("No balance data available. Please fetch data first.")

        elif choice == '4':
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
