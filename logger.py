# logger.py
import logging
import os
from datetime import datetime


LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


log_filename = datetime.now().strftime("log_%Y-%m-%d_%H-%M-%S.log")
log_path = os.path.join(LOG_DIR, log_filename)

class ColorFormatter(logging.Formatter):
    # Simplified ANSI escape codes for colors
    COLORS = {
        'INFO': '\033[92m',    # Green
        'WARNING': '\033[93m', # Yellow
        'ERROR': '\033[91m',   # Red
        'DEBUG': '\033[96m',   # Cyan
        'CRITICAL': '\033[91m', # Red
    }
    RESET = '\033[0m'

    def format(self, record):
        colored_levelname = self.COLORS.get(record.levelname, self.RESET) + record.levelname + self.RESET
        record.levelname = colored_levelname
        return super().format(record)

# Base logger configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()  # also outputs to terminal
    ]
)

# Apply color formatting to the stream handler
for handler in logging.getLogger().handlers:
    if isinstance(handler, logging.StreamHandler):
        handler.setFormatter(ColorFormatter("%(asctime)s [%(levelname)s] %(message)s"))

logger = logging.getLogger("AIPyCraftLogger")