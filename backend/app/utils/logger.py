import logging
import sys
from app.config import settings

def setup_logger():
    """Configure application logger"""
    logger = logging.getLogger("krib_superadmin")
    logger.setLevel(logging.DEBUG if settings.ENVIRONMENT == "development" else logging.INFO)
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG if settings.ENVIRONMENT == "development" else logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger

logger = setup_logger()

