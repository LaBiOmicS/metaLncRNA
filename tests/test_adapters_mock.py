import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
import pandas as pd
from metalncrna.adapters.cpc2 import CPC2Adapter
from metalncrna.engine.dispatcher import Dispatcher

def test_adapter_run_mocked():
    """Test that the adapter logic calls the correct command without running it."""
    adapter = CPC2Adapter(use_mamba=False)
    
    # Mock the run_command method to avoid actual subprocess call
    with patch.object(adapter, 'run_command') as mock_run:
        mock_run.return_value = "Mocked Output"
        
        # Mock Path.exists to pretend output was created
        with patch('pathlib.Path.exists', return_value=True):
            # Mock parse_results to return a dummy df
            adapter.parse_results = MagicMock(return_value=pd.DataFrame({"id": [1]}))
            
            res = adapter.get_standardized_results("input.fasta", "out_dir")
            
            assert not res.empty
            mock_run.assert_called_once()

def test_dispatcher_integration_mocked():
    """Test that Dispatcher correctly orchestrates multiple (mocked) tools."""
    config = {
        "cpc2": {"env_name": "test_env"},
        "lgc": {"env_name": "test_env"}
    }
    dispatcher = Dispatcher(config, use_mamba=False)
    
    # Mock run_tool_safe to return different names based on inputs
    def side_effect(name, *args, **kwargs):
        return name, pd.DataFrame({"id": [1]})
        
    with patch.object(dispatcher, 'run_tool_safe') as mock_safe:
        mock_safe.side_effect = side_effect
        
        results = dispatcher.run_all("input.fasta", "output", parallel=False)
        
        assert len(results) == 2
        assert "cpc2" in results
        assert "lgc" in results
