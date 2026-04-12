import logging
import sys
from pathlib import Path
from rich.logging import RichHandler

def setup_logger(output_dir=None, silent_console=False):
    """
    Configures logging. If silent_console is True, NO logs will be printed to terminal.
    """
    logger = logging.getLogger("metalncrna")
    logger.setLevel(logging.DEBUG)
    
    # Clear all existing handlers to prevent duplication
    while logger.handlers:
        logger.removeHandler(logger.handlers[0])

    # 1. Terminal Handler (only if NOT silent)
    if not silent_console:
        rich_handler = RichHandler(rich_tracebacks=True, markup=True)
        rich_handler.setLevel(logging.INFO)
        logger.addHandler(rich_handler)

    # 2. File Handler (Always active if output_dir is provided)
    if output_dir:
        log_file = Path(output_dir) / "metalncrna.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

logger = logging.getLogger("metalncrna")
