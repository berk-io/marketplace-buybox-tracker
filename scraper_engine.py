"""
Marketplace Buybox Tracker - Scraper Engine Module

This module handles the core data extraction logic utilizing human-like
behavior simulation. It navigates to target marketplace URLs and performs
data point analysis to retrieve current pricing, buybox ownership, and
competitor metrics while strictly adhering to rate-limit handling principles.
"""

import logging
import time
import random
from typing import Optional, List, Dict, Any
from core_config import TRACKER_CONFIG
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError, Page, Locator

logger = logging.getLogger(__name__)

class MarketplaceParser:
    """Handles parsing logic for dynamic marketplace product pages."""

    @staticmethod
    def extract_main_price(page: Page) -> Optional[float]:
        """
        Attempts to extract the main buybox price using fallback selectors.
        
        Args:
            page (Page): The active Playwright page object.
            
        Returns:
            Optional[float]: The extracted price, or None if extraction fails.
        """
        price_selectors: List[str] = [
            ".ty-plus-price-discounted-price",
            ".campaign-price-wrapper .new-price",
            ".lowest-price .discounted",
            ".price-container .discounted",
            ".price-current-price"
        ]

        for selector in price_selectors:
            try:
                locator: Locator = page.locator(selector).first
                if locator.is_visible(timeout=1000):
                    raw_text: str = locator.inner_text()
                    # Clean the text (e.g., "1.022,07 TL" -> 1022.07)
                    clean_price: str = raw_text.replace("TL", "").replace(".", "").replace(",", ".").strip()
                    logger.info(f"Main price successfully extracted using selector: {selector}")
                    return float(clean_price)
            except Exception:
                continue
                
        logger.warning("Failed to extract main price with all fallback selectors.")
        return None

    @staticmethod
    def extract_main_seller(page: Page) -> str:
        """Extracts the name of the current success_event (Buybox) owner."""
        try:
            locator: Locator = page.locator(".merchant-name").first
            if locator.is_visible(timeout=2000):
                return locator.inner_text().strip()
        except Exception:
            logger.error("Could not extract main seller name.", exc_info=True)
            
        return "Unknown Seller"

    @staticmethod
    def extract_other_sellers(page: Page) -> List[Dict[str, Any]]:
        """
        Performs data point analysis on the competitor list.
        
        Returns:
            List[Dict[str, Any]]: A list containing dictionaries of competitor names and prices.
        """
        competitors: List[Dict[str, Any]] = []
        try:
            # Locate all seller containers in the side panel
            items: List[Locator] = page.locator(".other-seller-item-total-container").all()
            
            for item in items:
                seller_name: str = "Unknown"
                price: Optional[float] = None

                # 1. Extract Competitor Name
                name_loc: Locator = item.locator(".other-seller-header-merchant-name").first
                if name_loc.is_visible(timeout=500):
                    seller_name = name_loc.inner_text().strip()

                # 2. Extract Competitor Price (Fallback logic for side panel)
                price_selectors: List[str] = [
                    ".campaign-price-wrapper .new-price",
                    ".price-current-price",
                    ".price-container .discounted"
                ]
                
                for sel in price_selectors:
                    p_loc: Locator = item.locator(sel).first
                    if p_loc.is_visible(timeout=500):
                        raw_price: str = p_loc.inner_text()
                        clean_price: str = raw_price.replace("TL", "").replace(".", "").replace(",", ".").strip()
                        price = float(clean_price)
                        break

                # Only add to list if we successfully parsed a price
                if price is not None:
                    competitors.append({
                        "seller_name": seller_name,
                        "price": price
                    })
                    
        except Exception:
            logger.error("Unexpected error during competitor data point analysis.", exc_info=True)

        return competitors


class MarketplaceScraper:
    """Executes data point analysis on target URLs with robust error handling."""

    def __init__(self) -> None:
        """Initializes the scraper engine state and compliance protocols."""
        self.user_agent: str = TRACKER_CONFIG.user_agent

    def _simulate_human_delay(self) -> None:
        """Applies request throttling by sleeping for a randomized duration."""
        delay: float = random.uniform(TRACKER_CONFIG.min_cooldown, TRACKER_CONFIG.max_cooldown)
        logger.info(f"Applying request throttling: sleeping for {delay:.2f} seconds.")
        time.sleep(delay)

    def fetch_product_data(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Navigates to the specified URL and extracts key business metrics.

        Args:
            url (str): The target marketplace product URL.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing data points if successful, None otherwise.
        """
        logger.info(f"Initiating data point analysis for URL: {url}")
        self._simulate_human_delay()

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(user_agent=self.user_agent)
                page: Page = context.new_page()
                
                # Enforcing strict timeout configurations to prevent resource hanging
                page.goto(url, timeout=TRACKER_CONFIG.request_timeout * 1000)
                
                # Wait for the main seller container to ensure page is reasonably loaded
                try:
                    page.wait_for_selector(".merchant-name", timeout=5000)
                except PlaywrightTimeoutError:
                    logger.warning(f"Timeout waiting for main seller element on URL: {url}")
                
                # Execute parsing logic
                buybox_winner: str = MarketplaceParser.extract_main_seller(page)
                buybox_price: Optional[float] = MarketplaceParser.extract_main_price(page)
                other_sellers: List[Dict[str, Any]] = MarketplaceParser.extract_other_sellers(page)
                
                browser.close()
                
                if buybox_price is None:
                    logger.warning("Data integrity failure: Main price could not be extracted.")
                    return None
                
                logger.info("Successfully completed data point analysis.")
                return {
                    "target_url": url,
                    "buybox_winner": buybox_winner,
                    "buybox_price": buybox_price,
                    "other_sellers": other_sellers,
                    "status": "success_event"
                }

        except PlaywrightTimeoutError:
            logger.error(f"Navigation timeout reached for URL: {url}", exc_info=True)
            return None
        except Exception:
            logger.error(f"Unexpected error during data extraction for URL: {url}", exc_info=True)
            return None