

"""
FastAPI application for the Finance Rl Proj Environment.
"""
import uvicorn
from openenv.core.env_server import create_web_interface_app
from finance_rl_proj.server.finance_rl_proj_environment import TradingEnv
from finance_rl_proj.models import TradingAction, TradingObservation

app = create_web_interface_app(TradingEnv, TradingAction, TradingObservation)

# The validator requires this specific function name
def main():
    """Entry point for the OpenEnv server."""
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    main()