import pytest
import os
from unittest.mock import Mock, patch
from src.personal_finance_tracker.plaid_client import PlaidClient


class TestPlaidClient:
    """Unit tests for PlaidClient methods"""
    
    def test_create_link_token(self, mock_plaid_client):
        """Test link token creation"""
        token = mock_plaid_client.create_link_token()
        assert token == "link-sandbox-test-token"
        mock_plaid_client.create_link_token.assert_called_once()
    
    def test_create_link_token_with_user_id(self, mock_plaid_client):
        """Test link token creation with custom user ID"""
        mock_plaid_client.create_link_token("custom_user_123")
        mock_plaid_client.create_link_token.assert_called_with("custom_user_123")
    
    def test_exchange_public_token(self, mock_plaid_client):
        """Test public token exchange"""
        access_token = mock_plaid_client.exchange_public_token("public-test-token")
        assert access_token == "access-sandbox-test-token"
        mock_plaid_client.exchange_public_token.assert_called_once_with("public-test-token")
    
    def test_get_accounts(self, mock_plaid_client):
        """Test account retrieval"""
        accounts = mock_plaid_client.get_accounts("access-token-123")
        
        assert len(accounts) == 2
        assert accounts[0]['account_id'] == 'test_account_1'
        assert accounts[0]['name'] == 'Test Checking Account'
        assert accounts[0]['type'] == 'depository'
        assert accounts[0]['balances']['current'] == 1250.75
        
        assert accounts[1]['account_id'] == 'test_account_2'
        assert accounts[1]['type'] == 'credit'
        
    def test_get_transactions(self, mock_plaid_client):
        """Test transaction retrieval"""
        transactions = mock_plaid_client.get_transactions("access-token-123")
        
        assert len(transactions) == 3
        
        # Test first transaction
        tx1 = transactions[0]
        assert tx1['transaction_id'] == 'test_tx_1'
        assert tx1['account_id'] == 'test_account_1'
        assert tx1['amount'] == -12.50  # negative for expense
        assert tx1['date'] == '2024-01-15'
        assert tx1['name'] == 'Local Coffee Shop'
        assert 'Food and Drink' in tx1['category']
        assert tx1['merchant_name'] == 'Local Coffee'
        
        # Test transaction with different account
        tx3 = transactions[2]
        assert tx3['account_id'] == 'test_account_2'
        assert tx3['merchant_name'] == 'StreamingService'


@patch('src.personal_finance_tracker.plaid_client.plaid_api.PlaidApi')
@patch('src.personal_finance_tracker.plaid_client.ApiClient')
@patch('src.personal_finance_tracker.plaid_client.Configuration')
class TestPlaidClientReal:
    """Tests for actual PlaidClient initialization and configuration"""
    
    def test_plaid_client_init_sandbox(self, mock_config, mock_api_client, mock_plaid_api):
        """Test PlaidClient initialization with sandbox environment"""
        with patch('src.personal_finance_tracker.plaid_client.config.PLAID_CLIENT_ID', 'test_client_id'):
            with patch('src.personal_finance_tracker.plaid_client.config.PLAID_SECRET', 'test_secret'):
                with patch('src.personal_finance_tracker.plaid_client.config.PLAID_ENV', 'sandbox'):
                    client = PlaidClient()
                    
                    # Verify Configuration was called with correct parameters
                    mock_config.assert_called_once()
                    call_args = mock_config.call_args
                    assert 'host' in call_args.kwargs
                    assert 'api_key' in call_args.kwargs
                    assert call_args.kwargs['api_key']['clientId'] == 'test_client_id'
                    assert call_args.kwargs['api_key']['secret'] == 'test_secret'