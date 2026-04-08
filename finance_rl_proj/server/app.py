

"""
FastAPI application for the Finance Rl Proj Environment.

This module creates an HTTP server that exposes the FinanceRlProjEnvironment
over HTTP and WebSocket endpoints, compatible with EnvClient.

Endpoints:
    - POST /reset: Reset the environment
    - POST /step: Execute an action
    - GET /state: Get current environment state
    - GET /schema: Get action/observation schemas
    - WS /ws: WebSocket endpoint for persistent sessions

Usage:
    # Development (with auto-reload):
    uvicorn server.app:app --reload --host 0.0.0.0 --port 8000

    # Production:
    uvicorn server.app:app --host 0.0.0.0 --port 8000 --workers 4

    # Or run directly:
    python -m server.app
"""
from openenv.core.env_server import create_web_interface_app
from .finance_rl_proj_environment import TradingEnv
from finance_rl_proj.models import TradingAction, TradingObservation

app = create_web_interface_app(TradingEnv, TradingAction, TradingObservation)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    