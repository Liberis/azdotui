# config/logger.py

import logging
import os

# Get the log file path from an environment variable or default to 'app.log'
LOG_FILE = os.getenv('LOG_FILE', 'app.log')

# Remove all handlers associated with the root logger object.
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Configure logging to write to a file
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG level
    filename=LOG_FILE,
    filemode='a',  # Append mode
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Get the logger instance
logger = logging.getLogger(__name__)

