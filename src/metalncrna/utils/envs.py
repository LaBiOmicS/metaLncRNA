import subprocess
import json
import os
from pathlib import Path

def get_env_prefix(env_name):
    """
    Finds the absolute prefix path of a Mamba/Conda environment.
    """
    try:
        # Try to get the prefix directly via mamba
        result = subprocess.run(["mamba", "env", "list", "--json"], capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        for env_path in data.get("envs", []):
            p = Path(env_path)
            if p.name == env_name:
                return p
        return None
    except:
        return None

def get_env_bin_path(env_name, tool_name):
    """
    Returns the absolute path of a tool inside a Mamba environment.
    """
    prefix = get_env_prefix(env_name)
    if prefix:
        # Check standard bin location
        bin_path = prefix / "bin" / tool_name
        if bin_path.exists():
            return str(bin_path)
        
        # Check if it exists without .py extension
        if tool_name.endswith(".py"):
            alt_path = prefix / "bin" / tool_name[:-3]
            if alt_path.exists():
                return str(alt_path)
                
    return tool_name

def get_python_path(env_name):
    """
    Returns the absolute path of the python interpreter in a Mamba environment.
    """
    prefix = get_env_prefix(env_name)
    if prefix:
        py_path = prefix / "bin" / "python"
        if py_path.exists():
            return str(py_path)
    return "python"
