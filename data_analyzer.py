"""
Marketplace Buybox Tracker - Data Analyzer Module

This module is responsible for the core data point analysis. 
It ingests raw scraped data, compares target business metrics 
against competitor values, and calculates the required actions 
to maintain the success_event (winning the buybox) while enforcing 
strict stop-loss (margin) protections.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class BuyboxAnalyzer:
    """Performs comparative data point analysis for marketplace strategy with margin protection."""

    def __init__(self, client_store_name: str) -> None:
        """
        Initializes the analyzer with the target client's store name.
        """
        self.client_store_name: str = client_store_name

    def analyze_competition(self, scraped_data: Dict[str, Any], min_price: float) -> Optional[Dict[str, Any]]:
        """
        Evaluates the scraped marketplace data to determine buybox status and calculates
        safe pricing strategies without violating the client's minimum price threshold.

        Args:
            scraped_data (Dict[str, Any]): The raw data extracted by the scraper engine.
            min_price (float): The absolute minimum price (stop-loss) the client can afford.

        Returns:
            Optional[Dict[str, Any]]: A structured analysis report or None if data is invalid.
        """
        logger.info(f"Starting data point analysis for client: {self.client_store_name} | Stop-Loss: {min_price} TL")

        try:
            if not scraped_data or "buybox_winner" not in scraped_data:
                logger.warning("Invalid data provided for analysis. Skipping evaluation.")
                return None

            current_winner: str = scraped_data.get("buybox_winner", "")
            current_price: float = float(scraped_data.get("buybox_price", 0.0))
            
            # Check if our client holds the success_event
            has_buybox: bool = (self.client_store_name.lower() == current_winner.lower())
            
            analysis_result: Dict[str, Any] = {
                "client_name": self.client_store_name,
                "has_buybox": has_buybox,
                "current_buybox_winner": current_winner,
                "current_buybox_price": current_price,
                "action_required": False,
                "suggested_price": None,
                "margin_warning": False
            }

            if has_buybox:
                logger.info("Success event confirmed: Client currently holds the buybox.")
            else:
                logger.info("Client does not hold the buybox. Calculating competitive threshold.")
                analysis_result["action_required"] = True
                
                # Target strategy: 1 TL below the current winner
                target_price: float = current_price - 1.0
                
                # Stop-loss (margin) protection check
                if target_price >= min_price:
                    analysis_result["suggested_price"] = target_price
                    logger.info(f"Suggested safe competitive price: {target_price}")
                else:
                    # Competitor is selling below our safe limit!
                    analysis_result["suggested_price"] = min_price
                    analysis_result["margin_warning"] = True
                    logger.warning(
                        f"Competitor price ({current_price}) forces target below stop-loss ({min_price}). "
                        "Recommending absolute minimum."
                    )

            return analysis_result

        except ValueError:
            logger.error("Data type conversion error during price evaluation.", exc_info=True)
            return None
        except Exception:
            logger.error("Unexpected error encountered during data point analysis.", exc_info=True)
            return None