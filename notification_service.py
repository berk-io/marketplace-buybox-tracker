"""
Marketplace Buybox Tracker - Notification Service Module

This module handles the delivery of real-time alerts to the client via
the Telegram API. It ensures robust architecture by managing connection
timeouts and HTTP errors gracefully, sending critical business alerts
when a success_event is lost, including stop-loss margin warnings.
"""

import logging
import requests
from typing import Dict, Any

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """Manages the transmission of data point analysis alerts via Telegram."""

    def __init__(self, bot_token: str, chat_id: str) -> None:
        """Initializes the notification service with API credentials."""
        self.bot_token: str = bot_token
        self.chat_id: str = chat_id
        self.api_url: str = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def send_buybox_alert(
        self, 
        product_url: str, 
        current_winner: str, 
        current_price: float, 
        suggested_price: float,
        margin_warning: bool = False
    ) -> bool:
        """
        Dispatches a localized alert, dynamically adapting if a stop-loss is hit.
        """
        # Constructing the base message for the SME demographic
        message_text: str = (
            "🚨 *DİKKAT: Buybox Kaybedildi!*\n\n"
            f"🛒 *Rakip Satıcı:* {current_winner}\n"
            f"💰 *Rakip Fiyatı:* {current_price} TL\n"
        )

        # Adapting message if the competitor price breaks our safe margin
        if margin_warning:
            message_text += (
                f"⚠️ *KRİTİK UYARI:* Rakip fiyatı zarar sınırınızın altına indi!\n"
                f"🛡️ *Dip Fiyat Koruması Aktif:* {suggested_price:.2f} TL (Daha fazla inmeyin)\n\n"
            )
        else:
            message_text += f"🎯 *Önerilen Fiyat:* {suggested_price:.2f} TL\n\n"

        message_text += f"🔗 [Ürüne Git ve Fiyatı Güncelle]({product_url})"

        payload: Dict[str, Any] = {
            "chat_id": self.chat_id,
            "text": message_text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }

        try:
            response: requests.Response = requests.post(self.api_url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Alert successfully dispatched to the client's Telegram channel.")
            return True
        except requests.exceptions.Timeout:
            logger.error("Telegram API connection timed out during alert dispatch.")
            return False
        except requests.exceptions.RequestException:
            logger.error("Failed to deliver Telegram alert due to network error.", exc_info=True)
            return False