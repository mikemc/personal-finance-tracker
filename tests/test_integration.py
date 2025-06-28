import pytest
import os
from unittest.mock import patch
from src.personal_finance_tracker.plaid_client import PlaidClient
from src.personal_finance_tracker.data_manager import DataManager


@pytest.mark.integration
class TestSandboxIntegration:
    """Integration tests for Plaid sandbox environment"""
    
    @pytest.fixture
    def real_plaid_client(self):
        """Real PlaidClient for sandbox testing"""
        # Only run if sandbox credentials are available
        if not (os.getenv('PLAID_CLIENT_ID') and os.getenv('PLAID_SECRET')):
            pytest.skip("Sandbox credentials not available")
        return PlaidClient()
    
    def test_create_link_token_sandbox(self, real_plaid_client):
        """Test creating a real link token with sandbox"""
        link_token = real_plaid_client.create_link_token("test_user_123")
        
        assert link_token is not None
        assert isinstance(link_token, str)
        assert link_token.startswith("link-sandbox-")
        assert len(link_token) > 20  # Reasonable token length
    
    @pytest.mark.skip(reason="Requires manual public token from Plaid Link demo")
    def test_full_sandbox_flow(self, real_plaid_client):
        """
        Test complete sandbox flow: link token -> public token -> access token -> data
        
        This test is skipped by default because it requires:
        1. Creating a link token
        2. Manually using Plaid Link demo to get public token
        3. Running this test with that public token
        
        To run manually:
        1. Get public token from Plaid Link demo
        2. Set environment variable: export PLAID_PUBLIC_TOKEN=<token>
        3. Remove @pytest.mark.skip decorator
        4. Run: pytest tests/test_integration.py::TestSandboxIntegration::test_full_sandbox_flow -v
        """
        public_token = os.getenv('PLAID_PUBLIC_TOKEN')
        if not public_token:
            pytest.skip("PLAID_PUBLIC_TOKEN environment variable not set")
        
        # Exchange public token for access token
        access_token = real_plaid_client.exchange_public_token(public_token)
        assert access_token is not None
        assert isinstance(access_token, str)
        
        # Get accounts
        accounts = real_plaid_client.get_accounts(access_token)
        assert len(accounts) > 0
        
        # Verify account structure
        account = accounts[0]
        assert 'account_id' in account
        assert 'name' in account
        assert 'type' in account
        assert 'balances' in account
        assert 'current' in account['balances']
        
        # Get transactions
        transactions = real_plaid_client.get_transactions(access_token)
        assert isinstance(transactions, list)  # May be empty, that's ok
        
        # If we have transactions, verify structure
        if transactions:
            tx = transactions[0]
            assert 'transaction_id' in tx
            assert 'account_id' in tx
            assert 'amount' in tx
            assert 'date' in tx
            assert 'name' in tx


@pytest.mark.integration 
class TestEndToEndFlow:
    """End-to-end tests with mocked Plaid responses"""
    
    def test_complete_data_flow(self, mock_plaid_client, temp_data_dir):
        """Test complete flow from Plaid client to data storage"""
        # Mock config to use temp directory
        with patch('src.personal_finance_tracker.config.DATA_DIR', temp_data_dir):
            with patch('src.personal_finance_tracker.config.TRANSACTIONS_FILE', temp_data_dir / 'transactions.tsv'):
                with patch('src.personal_finance_tracker.config.BALANCES_FILE', temp_data_dir / 'balances.tsv'):
                    
                    data_manager = DataManager()
                    
                    # Simulate the complete flow
                    # 1. Create link token
                    link_token = mock_plaid_client.create_link_token()
                    assert link_token == "link-sandbox-test-token"
                    
                    # 2. Exchange public token (simulated)
                    access_token = mock_plaid_client.exchange_public_token("public-test-token")
                    assert access_token == "access-sandbox-test-token"
                    
                    # 3. Get accounts and transactions
                    accounts = mock_plaid_client.get_accounts(access_token)
                    transactions = mock_plaid_client.get_transactions(access_token)
                    
                    # 4. Save data
                    data_manager.save_transactions(transactions, accounts)
                    data_manager.save_balances(accounts)
                    
                    # 5. Verify data was saved correctly
                    saved_balances = data_manager.get_latest_balances()
                    assert len(saved_balances) == 2  # Two accounts from mock
                    assert saved_balances.iloc[0]['account_name'] == 'Test Checking Account'
                    assert saved_balances.iloc[1]['account_name'] == 'Test Credit Card'
    
    @pytest.fixture
    def temp_data_dir(self):
        """Temporary directory for test data files"""
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)