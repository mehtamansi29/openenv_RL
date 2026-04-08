import os
import asyncio
from typing import Any, Dict

from finance_rl_proj.models import TradingAction, TradingObservation

# Try to import the higher-level OpenEnv client; if it's not available, fall back
# to a small HTTP-based client implemented with `requests` so the script remains runnable.
_HAS_OPENENV = False
try:
    from openenv import OpenEnvClient  # type: ignore
    _HAS_OPENENV = True
except Exception:
    OpenEnvClient = None  # type: ignore


class FinanceRlProjClient:
    """Minimal client for interacting with the OpenEnv server.

    If `openenv.OpenEnvClient` is available it will be used; otherwise this class
    falls back to simple HTTP POSTs to `/reset` and `/step` using `requests`.
    """

    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip("/")
        if _HAS_OPENENV and OpenEnvClient is not None:
            # Wrap the library client so existing higher-level behavior is preserved.
            self._lib_client = OpenEnvClient(server_url, TradingAction, TradingObservation)
        else:
            self._lib_client = None

    # Async-compatible wrapper for reset
    async def reset(self) -> Any:
        if self._lib_client is not None:
            return await self._lib_client.reset()
        # fallback to synchronous requests in a thread
        return await asyncio.to_thread(self._sync_post, "/reset")

    # Async-compatible wrapper for step
    async def step(self, action: TradingAction) -> Any:
        if self._lib_client is not None:
            return await self._lib_client.step(action)
        return await asyncio.to_thread(self._sync_post, "/step", action.dict())

    def _sync_post(self, path: str, json: Dict | None = None) -> Dict[str, Any]:
        # Import locally so dependency is optional at package import time
        try:
            import requests
        except Exception as exc:  # pragma: no cover - runtime error path
            raise RuntimeError("'requests' is required for fallback client") from exc

        url = f"{self.server_url}{path}"
        resp = requests.post(url, json=json, timeout=30)
        resp.raise_for_status()
        try:
            return resp.json()
        except ValueError:
            return {"raw": resp.text}


async def _demo():
    client = FinanceRlProjClient(os.getenv("OPENENV_URL", "http://localhost:8000"))
    print("Resetting environment...")
    reset_resp = await client.reset()
    print("Reset response:", reset_resp)

    # If server returned a default action schema, try stepping with a simple action
    action = TradingAction(message="hello from client") if hasattr(TradingAction, "message") else TradingAction()
    step_resp = await client.step(action)
    print("Step response:", step_resp)


if __name__ == "__main__":
    try:
        asyncio.run(_demo())
    except KeyboardInterrupt:
        pass