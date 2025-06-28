from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from plaid import Environment
from . import config
from datetime import datetime, timedelta

class PlaidClient:
    def __init__(self):
        env_map = {
            'sandbox': Environment.Sandbox,
            'production': Environment.Production
        }
        configuration = Configuration(
            host=env_map.get(config.PLAID_ENV, Environment.Sandbox),
            api_key={
                'clientId': config.PLAID_CLIENT_ID,
                'secret': config.PLAID_SECRET,
            }
        )
        api_client = ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)

    def create_link_token(self, user_id="user_123"):
        """Create a link token for Plaid Link"""
        request = LinkTokenCreateRequest(
            products=[Products('transactions'), Products('auth')],
            client_name="Personal Finance Tracker",
            country_codes=[CountryCode('US')],
            language='en',
            user=LinkTokenCreateRequestUser(client_user_id=user_id)
        )
        response = self.client.link_token_create(request)
        return response['link_token']

    def exchange_public_token(self, public_token):
        """Exchange public token for access token"""
        request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = self.client.item_public_token_exchange(request)
        return response['access_token']

    def get_accounts(self, access_token):
        """Get account information"""
        request = AccountsGetRequest(access_token=access_token)
        response = self.client.accounts_get(request)
        return response['accounts']

    def get_transactions(self, access_token, start_date=None, end_date=None):
        """Get transactions for the past 30 days by default"""
        if not start_date:
            start_date = datetime.now().date() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now().date()

        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date
        )
        response = self.client.transactions_get(request)
        return response['transactions']
