from abc import ABC, abstractmethod
import pandas as pd
import subprocess
import sys
import click
import os
from pathlib import Path
from typing import List, Optional, Any
from ..utils.envs import get_env_bin_path, get_python_path
from ..utils.logger import logger

class BaseAdapter(ABC):
    """
    Base class for all metaLncRNA tool adapters.
    """
    def __init__(self, tool_name: Optional[str] = None, env_name: Optional[str] = None, use_mamba: bool = True):
        self.tool_name = tool_name
        self.env_name = env_name
        self.use_mamba = use_mamba
        if self.use_mamba and self.env_name:
            self.tool_path = get_env_bin_path(self.env_name, self.tool_name)
            self.python_path = get_python_path(self.env_name)
        else:
            self.tool_path = tool_name
            self.python_path = "python"

    def run_command(self, cmd: List[str], log_file: Optional[Path] = None, cwd: Optional[Any] = None) -> str:
        """
        Executes a command with optional working directory.
        Captures stdout and stderr and logs them.
        """
        # Set environment variables to silence underlying tools (e.g. TensorFlow)
        env = os.environ.copy()
        env["TF_CPP_MIN_LOG_LEVEL"] = "3"
        env["PYTHONWARNINGS"] = "ignore"

        if self.use_mamba and self.env_name:
            full_cmd = ["mamba", "run", "-n", self.env_name] + cmd
        else:
            full_cmd = cmd
            
        logger.debug(f"Executing in {cwd or 'CWD'}: {' '.join(full_cmd)}")
        
        process = subprocess.Popen(
            full_cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            text=True,
            cwd=str(cwd) if cwd else None,
            env=env
        )
        stdout, _ = process.communicate()
        
        if log_file:
            with open(log_file, "a") as f:
                f.write(f"\n--- TOOL START: {self.tool_name} ---\n")
                f.write(f"COMMAND: {' '.join(full_cmd)}\n")
                f.write(f"CWD: {cwd}\n")
                f.write(f"EXIT CODE: {process.returncode}\n")
                f.write(f"OUTPUT:\n{stdout}\n")
                f.write(f"\n--- TOOL END: {self.tool_name} ---\n")
        
        if process.returncode != 0:
            if process.returncode == 1 and "plek" in self.tool_name.lower():
                logger.warning(f"PLEK exited with 1 but may have finished. Check log.")
            else:
                raise subprocess.CalledProcessError(process.returncode, full_cmd, output=stdout)
            
        return stdout

    @abstractmethod
    def run(self, input_fasta: str, output_dir: str, log_file: Optional[Path] = None) -> Path:
        pass

    @abstractmethod
    def parse_results(self, raw_output_path: Path) -> pd.DataFrame:
        pass

    def get_standardized_results(self, input_fasta: str, output_dir: str, log_file: Optional[Path] = None) -> pd.DataFrame:
        """Standard high-level entry point for prediction."""
        raw_output = self.run(input_fasta, output_dir, log_file=log_file)
        return self.parse_results(raw_output)
