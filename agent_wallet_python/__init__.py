from .client import AgentWalletClient
from .models import AwTool

__all__ = ["AgentWalletClient", "AwTool"]

# agent_wallet_python/exceptions.py
class AgentWalletError(Exception):
    """Base exception for agent wallet errors"""
    pass

class ApiError(AgentWalletError):
    """Raised when the API returns an error"""
    pass

class ConnectionError(AgentWalletError):
    """Raised when there's an error connecting to the API"""
    pass
