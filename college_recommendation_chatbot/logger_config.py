"""
Logging Configuration Module
Centralized logging setup for the application
"""

import logging
import logging.handlers
import os
from datetime import datetime

# Create logs directory
LOGS_DIR = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# Log file paths
ERROR_LOG = os.path.join(LOGS_DIR, 'errors.log')
INFO_LOG = os.path.join(LOGS_DIR, 'info.log')
DEBUG_LOG = os.path.join(LOGS_DIR, 'debug.log')

# Log format
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def setup_logging(app=None):
    """
    Setup logging for the application
    
    Args:
        app (Flask): Flask application instance (optional)
    """
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Create formatters
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    
    # Error Handler - logs only errors
    error_handler = logging.handlers.RotatingFileHandler(
        ERROR_LOG,
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)
    
    # Info Handler - logs info and higher
    info_handler = logging.handlers.RotatingFileHandler(
        INFO_LOG,
        maxBytes=10485760,
        backupCount=10
    )
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)
    root_logger.addHandler(info_handler)
    
    # Debug Handler - logs everything
    debug_handler = logging.handlers.RotatingFileHandler(
        DEBUG_LOG,
        maxBytes=10485760,
        backupCount=5
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(formatter)
    root_logger.addHandler(debug_handler)
    
    # Console Handler - for development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Flask specific logging
    if app:
        app.logger.setLevel(logging.INFO)
    
    # Suppress verbose libraries
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('pymongo').setLevel(logging.WARNING)
    
    return root_logger


def get_logger(name):
    """
    Get a logger instance
    
    Args:
        name (str): Logger name (usually __name__)
        
    Returns:
        Logger: Configured logger instance
    """
    return logging.getLogger(name)
