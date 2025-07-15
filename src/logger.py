
import logging
import os

def setup_logger(name: str) -> logging.Logger:
    """Ρύθμιση logger για την καταγραφή γεγονότων."""
    logger: logging.Logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    os.makedirs("logs", exist_ok=True)
    
    # File handler with UTF-8 encoding
    file_handler: logging.FileHandler = logging.FileHandler(f"logs/{name}.log", encoding='utf-8')
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    
    # Console handler with UTF-8 encoding
    console_handler: logging.StreamHandler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    )
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
