# Testing Guide for Finance RL Trading Environment

## Quick Start - Fix for "Not Found" Error

If you're getting a "not found" error when clicking "step" in the web UI, follow these steps:

### 1. Make sure the server is running on the correct port

The server must be running on **port 8000** for the web interface to work correctly.

```bash
cd /Users/MansiMehta/Desktop/Finance_RL_environment
source finance_rl_env/bin/activate
uvicorn finance_rl_proj.server.app:app --host 0.0.0.0 --port 8000
```

### 2. Access the Web Interface

Open your browser and go to: **`http://localhost:8000/web/`**

### 3. Enter Your Trade Details

Fill in the form with:
- **Stock Symbol**: `AAPL` (or any valid ticker like MSFT, GOOGL, etc.)
- **Action Type**: `BUY` or `SELL`
- **Quantity**: Number of shares (e.g., `12`)
- **Price**: Price per share (e.g., `1200`)
