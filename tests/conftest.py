import pytest
import os
from unittest.mock import Mock
from src.personal_finance_tracker.plaid_client import PlaidClient


@pytest.fixture
def mock_plaid_client():
    """Mock Plaid client for testing with correct response structure"""
    client = Mock(spec=PlaidClient)
    client.create_link_token.return_value = "link-sandbox-test-token"
    client.exchange_public_token.return_value = "access-sandbox-test-token"
    
    # Mock account data - matches your code's field access patterns
    client.get_accounts.return_value = [
        {
            'account_id': 'test_account_1',
            'name': 'Test Checking Account',
            'type': 'depository',
            'subtype': 'checking',
            'balances': {
                'current': 1250.75,
                'available': 1200.00
            }
        },
        {
            'account_id': 'test_account_2', 
            'name': 'Test Credit Card',
            'type': 'credit',
            'subtype': 'credit card',
            'balances': {
                'current': -450.25,
                'available': 2549.75
            }
        }
    ]
    
    # Mock transaction data - matches your code's field access patterns
    client.get_transactions.return_value = [
        {
            'transaction_id': 'test_tx_1',
            'account_id': 'test_account_1',
            'amount': -12.50,  # negative for expenses (as per your code comment)
            'date': '2024-01-15',
            'name': 'Local Coffee Shop',
            'category': ['Food and Drink', 'Coffee Shops'],
            'merchant_name': 'Local Coffee'
        },
        {
            'transaction_id': 'test_tx_2',
            'account_id': 'test_account_1', 
            'amount': -85.00,
            'date': '2024-01-14',
            'name': 'Grocery Store Purchase',
            'category': ['Food and Drink', 'Groceries'],
            'merchant_name': 'SuperMart'
        },
        {
            'transaction_id': 'test_tx_3',
            'account_id': 'test_account_2',
            'amount': -25.99,
            'date': '2024-01-13', 
            'name': 'Online Subscription',
            'category': ['Service', 'Subscription'],
            'merchant_name': 'StreamingService'
        }
    ]
    
    return client


@pytest.fixture
def test_env_vars(monkeypatch):
    """Set test environment variables"""
    monkeypatch.setenv("PLAID_CLIENT_ID", "test_client_id")
    monkeypatch.setenv("PLAID_SECRET", "test_secret")
    monkeypatch.setenv("PLAID_ENV", "sandbox")


@pytest.fixture
def sample_accounts():
    """Sample account data for testing"""
    return [
        {
            'account_id': 'acc_123',
            'name': 'Sample Checking',
            'type': 'depository',
            'subtype': 'checking',
            'balances': {
                'current': 2500.00,
                'available': 2450.00
            }
        }
    ]


@pytest.fixture  
def sample_transactions():
    """Sample transaction data for testing"""
    return [
        {
            'transaction_id': 'txn_456',
            'account_id': 'acc_123',
            'amount': -45.67,
            'date': '2024-01-10',
            'name': 'Restaurant Purchase',
            'category': ['Food and Drink', 'Restaurants'],
            'merchant_name': 'Pizza Palace'
        }
    ]