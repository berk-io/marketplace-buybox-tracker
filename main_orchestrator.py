"""
Marketplace Buybox Tracker - Main Orchestrator

This module serves as the central command architecture. It orchestrates
the human-like behavior simulation for data extraction, integrates with 
the analytical engine, and triggers external notifications securely 
using dynamic multi-client data.
"""

import os
import logging
import time
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

from core_config import TRACKER_CONFIG, load_product_database
from scraper_engine import MarketplaceScraper
from data_analyzer import BuyboxAnalyzer
from notification_service import TelegramNotifier

logger = logging.getLogger(__name__)

class PipelineOrchestrator:
    """Manages the end-to-end data point analysis workflow for multiple clients."""

    def __init__(self) -> None:
        """Initializes the orchestrator and shared sub-modules."""
        self.telegram_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.scraper: MarketplaceScraper = MarketplaceScraper()

    def execute_pipeline(self) -> None:
        """Executes the scheduled scraping, analysis, and notification operations."""
        logger.info("Initializing dynamic tracker pipeline for all clients...")
        products: List[Dict[str, Any]] = TRACKER_CONFIG.products

        if not products:
            logger.warning("No products found in the database. Standing by.")
            return

        for item in products:
            url: str = item.get("url", "")
            client_name: str = item.get("client_name", "Unknown")
            min_price: float = float(item.get("min_price", 0.0))
            chat_id: str = item.get("chat_id", "")

            if not url:
                continue

            logger.info(f"Processing target endpoint for client [{client_name}]: {url}")
            
            try:
                # 1. Execute Data Extraction
                scraped_data: Optional[Dict[str, Any]] = self.scraper.fetch_product_data(url)
                if not scraped_data:
                    continue

                # 2. Execute Business Logic Analysis (Dynamically instantiated per client)
                analyzer = BuyboxAnalyzer(client_name)
                # Note: In the next phase, we will pass min_price to this analyzer
                analysis_result: Optional[Dict[str, Any]] = analyzer.analyze_competition(scraped_data, min_price)

                if not analysis_result:
                    continue

                # 3. Process Results and Dispatch Alerts
                self._process_results(url, analysis_result, chat_id)

            except Exception:
                logger.error(f"Critical failure during pipeline execution for URL: {url}", exc_info=True)
                continue

        logger.info("Pipeline execution cycle completed successfully.")

    def _process_results(self, url: str, result: Dict[str, Any], chat_id: str) -> None:
        """Evaluates the analysis output and triggers dynamic Telegram alerts."""
        if result.get("has_buybox"):
            logger.info(f"[SUCCESS EVENT] Client holds the buybox for {url}.")
        else:
            current_winner: str = result.get("current_buybox_winner", "Unknown")
            current_price: float = result.get("current_buybox_price", 0.0)
            sugg_price: float = result.get("suggested_price", 0.0)
            
            logger.warning(f"Buybox lost to '{current_winner}' on {url}. Triggering notification.")
            
            # Dynamically dispatch the alert to the specific client's chat_id
            if self.telegram_token and chat_id:
                notifier = TelegramNotifier(bot_token=self.telegram_token, chat_id=chat_id)
                notifier.send_buybox_alert(
                    product_url=url,
                    current_winner=current_winner,
                    current_price=current_price,
                    suggested_price=sugg_price
                )

if __name__ == "__main__":
    orchestrator = PipelineOrchestrator()
    
    try:
        while True:
            # Refresh the database each cycle so new additions to JSON are picked up automatically
            TRACKER_CONFIG.products = load_product_database()
            
            orchestrator.execute_pipeline()
            
            logger.info("Entering standby mode to respect rate-limit handling...")
            time.sleep(900) 
            
    except KeyboardInterrupt:
        logger.info("Pipeline execution manually terminated by the system administrator.")