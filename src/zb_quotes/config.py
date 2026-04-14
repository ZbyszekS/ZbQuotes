import logging
import os
from datetime import datetime as dt
from pathlib import Path

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Generate log filename with current date and time
TIMESTAMP = dt.now().strftime("%Y%m%d_%H%M%S")
LOG_FILENAME = f"quote_import_{TIMESTAMP}.log"
LOG_FILE_PATH = LOGS_DIR / LOG_FILENAME

# Configure logger
def setup_logger(name: str = "quote_importer", with_file_handler: bool = True, level: int = logging.INFO) -> logging.Logger:
    """
    Setup logger with optional file handler.
    
    Args:
        name: Logger name (default: "quote_importer")
        with_file_handler: Whether to add file handler (default: True)
        level: Logging level (default: logging.INFO)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler (always added)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if with_file_handler:
        file_handler = logging.FileHandler(LOG_FILE_PATH, mode='w', encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# Function to temporarily change file handler level
def set_file_handler_level(temp_level: int, original_level: int = logging.INFO):
    """
    Temporarily change file handler level and return function to restore it.
    
    Args:
        temp_level: Temporary level (e.g., logging.DEBUG, logging.ERROR)
        original_level: Level to restore to (default: logging.INFO)
        
    Returns:
        Function to restore original level
    """
    # Find the file handler
    file_handler = None
    for handler in IMPORT_LOGGER.handlers:
        if isinstance(handler, logging.FileHandler):
            file_handler = handler
            break
    
    if file_handler:
        # Store original level
        original = file_handler.level
        # Set temporary level
        file_handler.setLevel(temp_level)
        
        # Return function to restore
        def restore():
            file_handler.setLevel(original)
        
        return restore
    
    return lambda: None  # No-op if no file handler found    

# Create logger instances
IMPORT_LOGGER = setup_logger("quote_importer", with_file_handler=True)
LOGGER = setup_logger("general", with_file_handler=False)

# Export logger and log file path for use in other modules
__all__ = ['IMPORT_LOGGER', 'LOGGER', 'setup_logger', 'LOG_FILE_PATH', 'set_file_handler_level']


# # Usage examples:
# if __name__ == "__main__":
#     # Normal logging (INFO level to file)
#     IMPORT_LOGGER.info("This will go to both console and file")
#     IMPORT_LOGGER.debug("This DEBUG message won't go to file (default INFO level)")
    
#     # Temporarily enable DEBUG level for file
#     restore_file_level = set_file_handler_level(logging.DEBUG)
    
#     IMPORT_LOGGER.debug("Now this DEBUG message will go to file too!")
#     IMPORT_LOGGER.info("This still goes to both")
    
#     # Restore original level
#     restore_file_level()
    
#     IMPORT_LOGGER.debug("This DEBUG message won't go to file anymore")
    
#     # Another example: temporarily set only ERROR level to file
#     restore_error_level = set_file_handler_level(logging.ERROR)
    
#     IMPORT_LOGGER.info("This INFO goes to console but NOT to file")
#     IMPORT_LOGGER.error("This ERROR goes to both")
    
#     restore_error_level()