import pytest
import pandas as pd
import tempfile
from pathlib import Path
from unittest.mock import patch
from src.personal_finance_tracker.data_manager import DataManager


class TestDataManager:
    """Unit tests for DataManager"""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary directory for test data files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            yield temp_path
    
    @pytest.fixture
    def data_manager_with_temp_dir(self, temp_data_dir):
        """DataManager instance using temporary directory"""
        transactions_file = temp_data_dir / 'transactions.tsv'
        balances_file = temp_data_dir / 'balances.tsv'
        
        with patch('src.personal_finance_tracker.data_manager.config.DATA_DIR', temp_data_dir):
            with patch('src.personal_finance_tracker.data_manager.config.TRANSACTIONS_FILE', transactions_file):
                with patch('src.personal_finance_tracker.data_manager.config.BALANCES_FILE', balances_file):
                    return DataManager()
    
    def test_init_creates_files(self, data_manager_with_temp_dir, temp_data_dir):
        """Test that DataManager creates TSV files on initialization"""
        transactions_file = temp_data_dir / 'transactions.tsv'
        balances_file = temp_data_dir / 'balances.tsv'
        
        assert transactions_file.exists()
        assert balances_file.exists()
        
        # Check that files have correct headers
        tx_df = pd.read_csv(transactions_file, sep='\t')
        balance_df = pd.read_csv(balances_file, sep='\t')
        
        expected_tx_headers = [
            'transaction_id', 'account_id', 'account_name', 'amount',
            'date', 'description', 'category', 'merchant_name'
        ]
        expected_balance_headers = [
            'account_id', 'account_name', 'account_type', 'balance_current',
            'balance_available', 'last_updated'
        ]
        
        assert list(tx_df.columns) == expected_tx_headers
        assert list(balance_df.columns) == expected_balance_headers
    
    def test_save_transactions(self, data_manager_with_temp_dir, sample_transactions, sample_accounts, temp_data_dir):
        """Test saving transactions to TSV file"""
        data_manager_with_temp_dir.save_transactions(sample_transactions, sample_accounts)
        
        # Read the saved data
        transactions_file = temp_data_dir / 'transactions.tsv'
        df = pd.read_csv(transactions_file, sep='\t')
        
        assert len(df) == 1
        assert df.iloc[0]['transaction_id'] == 'txn_456'
        assert df.iloc[0]['account_id'] == 'acc_123'
        assert df.iloc[0]['account_name'] == 'Sample Checking'
        assert df.iloc[0]['amount'] == 45.67  # Should be positive (negated from -45.67)
        assert df.iloc[0]['date'] == '2024-01-10'
        assert df.iloc[0]['description'] == 'Restaurant Purchase'
        assert 'Food and Drink' in df.iloc[0]['category']
        assert df.iloc[0]['merchant_name'] == 'Pizza Palace'
    
    def test_save_transactions_no_duplicates(self, data_manager_with_temp_dir, sample_transactions, sample_accounts, temp_data_dir):
        """Test that duplicate transactions are not saved"""
        # Save transactions twice
        data_manager_with_temp_dir.save_transactions(sample_transactions, sample_accounts)
        data_manager_with_temp_dir.save_transactions(sample_transactions, sample_accounts)
        
        # Should still only have one transaction
        transactions_file = temp_data_dir / 'transactions.tsv'
        df = pd.read_csv(transactions_file, sep='\t')
        assert len(df) == 1
    
    def test_save_balances(self, data_manager_with_temp_dir, sample_accounts, temp_data_dir):
        """Test saving account balances"""
        data_manager_with_temp_dir.save_balances(sample_accounts)
        
        # Read the saved data
        balances_file = temp_data_dir / 'balances.tsv'
        df = pd.read_csv(balances_file, sep='\t')
        
        assert len(df) == 1
        assert df.iloc[0]['account_id'] == 'acc_123'
        assert df.iloc[0]['account_name'] == 'Sample Checking'
        assert df.iloc[0]['account_type'] == 'depository'
        assert df.iloc[0]['balance_current'] == 2500.00
        assert df.iloc[0]['balance_available'] == 2450.00
        assert pd.notna(df.iloc[0]['last_updated'])  # Should have timestamp
    
    def test_get_latest_balances(self, data_manager_with_temp_dir, sample_accounts):
        """Test retrieving latest balance data"""
        # Save some balances first
        data_manager_with_temp_dir.save_balances(sample_accounts)
        
        # Retrieve them
        df = data_manager_with_temp_dir.get_latest_balances()
        
        assert len(df) == 1
        assert df.iloc[0]['account_name'] == 'Sample Checking'
        assert df.iloc[0]['balance_current'] == 2500.00
    
    def test_get_latest_balances_empty(self, temp_data_dir):
        """Test retrieving balances when no data exists"""
        # Create DataManager but don't save any data, and remove the created file
        with patch('src.personal_finance_tracker.data_manager.config.DATA_DIR', temp_data_dir):
            with patch('src.personal_finance_tracker.data_manager.config.TRANSACTIONS_FILE', temp_data_dir / 'transactions.tsv'):
                with patch('src.personal_finance_tracker.data_manager.config.BALANCES_FILE', temp_data_dir / 'balances.tsv'):
                    data_manager = DataManager()
                    # Remove the file that was created during init
                    (temp_data_dir / 'balances.tsv').unlink()
                    df = data_manager.get_latest_balances()
                    assert len(df) == 0