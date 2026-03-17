"""
Marketplace Buybox Tracker - Core Configuration Module

This module establishes the foundational configuration parameters, 
logging standards, and target environment variables for the 
data point analysis pipeline. It ensures a robust architecture 
by dynamically loading targets from a local JSON database.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tracker_pipeline.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_product_database() -> List[Dict[str, Any]]:
    """Reads the dynamic product list from the local JSON database."""
    try:
        with open("products.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error("Database file 'products.json' not found.")
        return []
    except json.JSONDecodeError:
        logger.error("Database file 'products.json' contains invalid JSON structure.")
        return []
    except Exception as e:
        logger.error("Unexpected error accessing the database.", exc_info=True)
        return []

@dataclass
class ScraperConfig:
    """Centralized configuration for human-like behavior simulation and request throttling."""
    
    products: List[Dict[str, Any]] = field(default_factory=load_product_database)
    
    # Cooldown ranges for rate-limit handling (in seconds)
    min_cooldown: int = 5
    max_cooldown: int = 15
    request_timeout: int = 30
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

TRACKER_CONFIG = ScraperConfig()

logger.info("Core configuration and database module successfully initialized.")