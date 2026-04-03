from src.config import IMPORT_LOGGER
import logging

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

# Usage examples:
if __name__ == "__main__":
    # Normal logging (INFO level to file)
    IMPORT_LOGGER.info("This will go to both console and file")
    IMPORT_LOGGER.debug("This DEBUG message won't go to file (default INFO level)")
    
    # Temporarily enable DEBUG level for file
    restore_file_level = set_file_handler_level(logging.DEBUG)
    
    IMPORT_LOGGER.debug("Now this DEBUG message will go to file too!")
    IMPORT_LOGGER.info("This still goes to both")
    
    # Restore original level
    restore_file_level()
    
    IMPORT_LOGGER.debug("This DEBUG message won't go to file anymore")
    
    # Another example: temporarily set only ERROR level to file
    restore_error_level = set_file_handler_level(logging.ERROR)
    
    IMPORT_LOGGER.info("This INFO goes to console but NOT to file")
    IMPORT_LOGGER.error("This ERROR goes to both")
    
    restore_error_level()
