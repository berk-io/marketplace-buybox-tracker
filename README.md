# Marketplace Buybox Tracker & Management Dashboard  

## Overview
The **Marketplace Buybox Tracker** is an enterprise-grade automation pipeline designed for SMEs and e-commerce merchants. It provides real-time **data point analysis** to monitor competitive pricing, ensure data integrity, and maintain the **success_event** (Buybox ownership) across highly competitive digital marketplaces.

This solution integrates a robust backend data pipeline with a secure, session-based UI dashboard, enabling business owners to seamlessly manage target assets and enforce strict stop-loss (margin) protections.

## Core Architecture & Business Value
* **Robust Architecture:** Modular design separating configuration (`core_config.py`), logic processing (`data_analyzer.py`), and user interface (`ui_dashboard.py`).
* **Compliance & Reliability:** Implements sophisticated **rate-limit handling**, request throttling, and **human-like behavior simulation** to maintain uninterrupted data flow without violating platform integrities.
* **Stop-Loss Protection:** Algorithmically calculates competitive thresholds while strictly adhering to user-defined minimum margin limits, preventing catastrophic underpricing.
* **Real-Time Alerting:** Integrates with the Telegram API to deliver instantaneous, actionable localized alerts to stakeholders when a success_event is compromised.

## Technologies Used
* **Python 3.x** (Core Backend)
* **Playwright** (Dynamic DOM Rendering & Data Point Analysis)
* **Streamlit** (Secure UI Dashboard Application)
* **Requests** (API Integration)
* **Dotenv** (Environment Variable Security)

## Installation & Deployment

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/berk-io/Marketplace-Buybox-Tracker.git](https://github.com/berk-io/Marketplace-Buybox-Tracker.git)
   cd Marketplace-Buybox-Tracker
   ```

2. **Establish a secure virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install core dependencies & browser binaries:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Environment Configuration:**
   Create a `.env` file in the root directory and define the secure API keys:
   ```env
   TELEGRAM_BOT_TOKEN=your_secure_bot_token_here
   ```

## Operation Protocol
**To initialize the Management Dashboard (UI):**
```bash
streamlit run ui_dashboard.py
```
*Access the local web interface to configure store profiles, add target URLs, and set dynamic stop-loss margins.*

**To execute the Autonomous Pipeline:**
```bash
python main_orchestrator.py
```
*The orchestrator will commence background monitoring, executing scheduled analysis cycles and dispatching alerts based on the database parameters.*

## Security Notice
For production environments, ensure that `products.json`, `profile.json`, and `.env` files are strictly excluded from version control to protect client data integrity.
