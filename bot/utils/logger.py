import logging
import traceback
from inspect import trace

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a file handler
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.DEBUG)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)

# Create a formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Custom function to log exceptions with traceback
def log_exception(e):

    tb = traceback.extract_tb(e.__traceback__)
    last_entry = tb[-1]
    line_number = last_entry.lineno

    logger.error('Code was unsuccessful: %s', e)
    logger.error('Error occurred at line: %d', line_number)