# agent_wallet_python/models.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any

class PolicySchema(BaseModel):
    type: Dict = {}
    version: str
    schema_def: Dict[str, Any] = dict()  # renamed from schema

class Parameters(BaseModel):
    type: Dict = {}
    schema_def: Dict[str, Any] = dict()  # renamed from schema
    descriptions: Dict[str, str]

class Tool(BaseModel):
    name: str
    description: str
    ipfsCid: str
    defaultPolicyIpfsCid: str
    parameters: Parameters
    policy: PolicySchema

class AwTool(BaseModel):
    """
    Represents an Agent Wallet Tool with its associated network
    """
    tool: Tool
    network: str
    
    model_config = ConfigDict(from_attributes=True)

    def __str__(self) -> str:
        """String representation of the tool"""
        return f"{self.tool.name} ({self.network})"
    
    @property
    def name(self) -> str:
        """Convenience accessor for tool name"""
        return self.tool.name
    
    @property
    def ipfs_cid(self) -> str:
        """Convenience accessor for IPFS CID"""
        return self.tool.ipfsCid
    
    @property
    def description(self) -> str:
        """Convenience accessor for description"""
        return self.tool.description
    
    @property
    def parameter_descriptions(self) -> Dict[str, str]:
        """Convenience accessor for parameter descriptions"""
        return self.tool.parameters.descriptions
