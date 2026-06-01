import os
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

import pandas as pd

from ..utils.logger import logger


class BaseAdapter(ABC):
    def __init__(self, tool_name, env_name, use_mamba=True):
        self.tool_name = tool_name
        self.env_name = env_name
        self.use_mamba = use_mamba

    def run_command(self, cmd, log_file=None, cwd=None, env=None):
        """
        Executes a command using subprocess with mamba integration and logging.
        """
        # Prepare environment
        current_env = os.environ.copy()
        # Set environment variables to silence underlying tools (e.g. TensorFlow)
        current_env["TF_CPP_MIN_LOG_LEVEL"] = "3"
        current_env["PYTHONWARNINGS"] = "ignore"
        if env:
            current_env.update(env)

        if self.use_mamba:
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
            env=current_env
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
                logger.warning("PLEK exited with 1 but may have finished. Check log.")
            else:
                raise subprocess.CalledProcessError(process.returncode, full_cmd, output=stdout)

        return stdout

    @abstractmethod
    def run(self, input_fasta: str, output_dir: str, log_file: Optional[Path] = None) -> Path:
        pass

    @abstractmethod
    def parse_results(self, raw_output_path: Path) -> pd.DataFrame:
        pass

    def get_standardized_results(self, input_fasta, output_dir, log_file=None):
        raw_output = self.run(input_fasta, output_dir, log_file=log_file)
        return self.parse_results(raw_output)
