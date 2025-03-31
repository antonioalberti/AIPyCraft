# logger.py
import logging
import os
from datetime import datetime
import sys # Required for StreamHandler target

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# --- Color Formatter (Keep as is, but ensure it doesn't modify the record directly) ---
class ColorFormatter(logging.Formatter):
    COLORS = {
        'INFO': '\033[92m',    # Green
        'WARNING': '\033[93m', # Yellow
        'ERROR': '\033[91m',   # Red
        'DEBUG': '\033[96m',   # Cyan
        'CRITICAL': '\033[91m', # Red
    }
    RESET = '\033[0m'

    def format(self, record):
        # Format the message using the base class formatter
        log_message = super().format(record)
        # Apply color to the levelname part within the formatted string if possible
        # This is a simplified approach; more robust coloring might involve parsing the format string
        levelname_colored = self.COLORS.get(record.levelname, '') + record.levelname + self.RESET
        # Replace the plain levelname in the formatted string (assuming default format)
        # This might break if the format string is changed significantly
        return log_message.replace(f"[{record.levelname}]", f"[{levelname_colored}]", 1)


# --- Logger Setup ---
# Get the root logger instance ONCE
logger = logging.getLogger("AIPyCraftLogger")
logger.setLevel(logging.INFO) # Set level here

# Keep track of handlers to avoid adding duplicates
_stream_handler = None
_file_handler = None

def setup_logging(run_id=None):
    """Configures logging handlers and formatters. Call this early."""
    global _stream_handler, _file_handler

    # --- Stream Handler (Console Output) ---
    # Add stream handler only if it doesn't exist
    if _stream_handler is None and not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        _stream_handler = logging.StreamHandler(sys.stdout)
        color_formatter = ColorFormatter("%(asctime)s [%(levelname)s] %(message)s")
        _stream_handler.setFormatter(color_formatter)
        logger.addHandler(_stream_handler)

    # --- File Handler (Log File Output) ---
    # Remove existing file handler before adding a new one
    if _file_handler is not None:
        logger.removeHandler(_file_handler)
        _file_handler.close()
        _file_handler = None
    # Find and remove any other FileHandlers that might have been added inadvertently
    for handler in logger.handlers[:]: # Iterate over a copy
        if isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)
            handler.close()


    # Create new filename with timestamp and optional run_id
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S") # Use YYYYMMDD format
    run_id_str = f"_run{run_id}" if run_id is not None else ""
    # Use a distinct prefix for main logs
    log_filename = f"AIPyCraft_main_{timestamp_str}{run_id_str}.log"
    log_path = os.path.join(LOG_DIR, log_filename)

    # Create and add the new file handler
    _file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s") # Standard formatter for file
    _file_handler.setFormatter(file_formatter)
    logger.addHandler(_file_handler)

    # Use the logger instance directly now
    logger.info(f"AIPyCraft logging configured. Log file: {log_path}")

# Note: No initial logging setup here anymore.
# main.py MUST call setup_logging().
