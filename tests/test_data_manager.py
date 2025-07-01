import pytest
import pandas as pd
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.personal_finance_tracker.data_manager import DataManager


class TestDataManager:
    """Unit tests for DataManager"""

    @pytest.fixture
    def sample_accounts(self):
        return [{
            'account_id': 'acc_123',
            'name': 'Sample Checking',
            'type': 'depository',
            'balances': {
                'current': 2500.00,
                'available': 2450.00
            }
        }]

    @pytest.fixture
    def sample_transactions(self):
        return [{
            'transaction_id': 'txn_456',
            'account_id': 'acc_123',
            'date': '2024-01-10',
            'name': 'Restaurant Purchase',
            'amount': 45.67,
            'category': ['Food and Drink'],
            'merchant_name': 'Pizza Palace'
        }]

    @pytest.fixture
    def temp_transaction_files(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            transactions_file = tmp_path / 'transactions.tsv'
            balances_file = tmp_path / 'balances.tsv'

            transactions_file.touch(exist_ok=True)
            balances_file.touch(exist_ok=True)

            yield tmp_path, transactions_file, balances_file

    @pytest.fixture
    def mock_config(self, temp_transaction_files):
        tmp_dir, transactions_file, balances_file = temp_transaction_files

        class MockConfig:
            DATA_DIR = tmp_dir
            TRANSACTIONS_FILE = transactions_file
            BALANCES_FILE = balances_file

        with patch('src.personal_finance_tracker.data_manager.config', MockConfig):
            yield MockConfig

    @pytest.fixture
    def data_manager(self, mock_config):
        # When calling data manager, mock config is already being transmitted
        with patch('src.personal_finance_tracker.data_manager.config', mock_config):
            yield DataManager()

    @patch('src.personal_finance_tracker.data_manager.config.TRANSACTIONS_FILE', new_callable=MagicMock)
    @patch('src.personal_finance_tracker.data_manager.config.BALANCES_FILE', new_callable=MagicMock)
    def test_data_manager_init(self, mock_balances_file, mock_transactions_file):
        def run_test_case(trans_exists, bal_exists, expected_tx_call, expected_bal_call):
            """
            var trans_exists: bool - transaction file existence flag
            var bal_exists: bool - balances file existence flag
            var expected_tx_call: int - expected number of calls to init_transactions_file
            var expected_bal_call: int - expected number of calls to init_balances_file
            """
            mock_transactions_file.exists.return_value = trans_exists
            mock_balances_file.exists.return_value = bal_exists

            with patch.object(DataManager, 'init_transactions_file') as mock_init_tx, \
                    patch.object(DataManager, 'init_balances_file') as mock_init_balance:
                dm = DataManager()

                assert mock_init_tx.call_count == expected_tx_call
                assert mock_init_balance.call_count == expected_bal_call

        # Scenario 1: Files exist
        run_test_case(True, True, 0, 0)

        # Scenario 2: Files are missing
        run_test_case(False, False, 1, 1)

        # Scenario 3: Only one file is missing (TRANSACTIONS_FILE)
        run_test_case(False, True, 1, 0)

        # Scenario 4: Only one file is missing (BALANCES_FILE)
        run_test_case(True, False, 0, 1)

    def test_save_transactions(self, sample_transactions, sample_accounts, mock_config, data_manager):
        """Test saving transactions to TSV file"""

        # Because of the patch, we need to call init_transactions_file manually
        data_manager.init_transactions_file()
        data_manager.save_transactions(sample_transactions, sample_accounts)

        df = pd.read_csv(mock_config.TRANSACTIONS_FILE, sep='\t')

        assert len(df) == 1
        assert df.iloc[0]['transaction_id'] == 'txn_456'
        assert df.iloc[0]['account_id'] == 'acc_123'
        assert df.iloc[0]['account_name'] == 'Sample Checking'
        assert df.iloc[0]['amount'] == -45.67  # Should be positive (negated from -45.67)
        assert df.iloc[0]['date'] == '2024-01-10'
        assert df.iloc[0]['description'] == 'Restaurant Purchase'
        assert 'Food and Drink' in df.iloc[0]['category']
        assert df.iloc[0]['merchant_name'] == 'Pizza Palace'

    def test_save_transactions_no_duplicates(self, mock_config, data_manager, sample_transactions, sample_accounts):
        """Test that duplicate transactions are not saved"""

        # Because of the patch, we need to call init_transactions_file manually
        data_manager.init_transactions_file()

        data_manager.save_transactions(sample_transactions, sample_accounts)
        data_manager.save_transactions(sample_transactions, sample_accounts)

        df = pd.read_csv(mock_config.TRANSACTIONS_FILE, sep='\t')

        assert len(df) == 1

    def test_save_balances(self, mock_config, data_manager, sample_accounts):
        """Test saving account balances"""
        data_manager.save_balances(sample_accounts)

        df = pd.read_csv(mock_config.BALANCES_FILE, sep='\t')

        assert len(df) == 1
        assert df.iloc[0]['account_id'] == 'acc_123'
        assert df.iloc[0]['account_name'] == 'Sample Checking'
        assert df.iloc[0]['account_type'] == 'depository'
        assert df.iloc[0]['balance_current'] == 2500.00
        assert df.iloc[0]['balance_available'] == 2450.00
        assert pd.notna(df.iloc[0]['last_updated'])  # Should have timestamp

    def test_get_latest_balances(self, mock_config, data_manager, sample_accounts):
        """Test retrieving latest balance data"""

        # Save some balances first
        data_manager.save_balances(sample_accounts)

        df = data_manager.get_latest_balances()

        assert not df.empty
        assert len(df) == 1
        assert df.iloc[0]['account_name'] == 'Sample Checking'
        assert df.iloc[0]['balance_current'] == 2500.00

    def test_get_latest_balances_empty(self, mock_config, data_manager):
        """Test retrieving balances when no data exists"""
        # Delete the files if they exist
        if mock_config.BALANCES_FILE.exists():
            mock_config.BALANCES_FILE.unlink()

        df = data_manager.get_latest_balances()
        assert len(df) == 0  # or assert df.empty
        assert df.empty

