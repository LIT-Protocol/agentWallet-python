import json
from datetime import datetime, timedelta, timezone
from eth_typing import Address
from eth_utils import to_checksum_address
from web3 import Web3
from agent_wallet_python.client import AgentWalletClient
from lit_python_sdk import connect
from dotenv import load_dotenv
import os

class LitERC20Transfer:
    def __init__(self, network: str = "datil-dev"):
        self.network = network
        self.client = None
        self.agent_wallet = AgentWalletClient()
        self.tool = None
        
    def connect(self) -> None:
        """Initialize and connect to Lit Protocol"""
        self.client = connect()
        load_dotenv()
        private_key = os.getenv("LIT_PRIVATE_KEY")
        if not private_key:
            raise ValueError("LIT_PRIVATE_KEY not found in environment variables")
            
        self.client.set_auth_token(private_key)
        self.client.new(lit_network=self.network, debug=True)
        self.client.connect()
        
        # Fetch the tool information
        self.tool = self.agent_wallet.get_tool_by_name("ERC20Transfer", network=self.network)
        if not self.tool:
            raise ValueError(f"ERC20Transfer tool not found for network {self.network}")

    def get_session_signatures(self) -> dict:
        """Get session signatures for Lit Protocol"""
        expiration = (datetime.now(timezone.utc) + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        session_sigs_result = self.client.get_session_sigs(
            chain="ethereum",
            expiration=expiration,
            resource_ability_requests=[{
                "resource": {
                    "resource": "*",
                    "resourcePrefix": "lit-litaction",
                },
                "ability": "lit-action-execution",
            }]
        )
        return session_sigs_result.get("sessionSigs", {})

    def validate_address(self, address: str) -> str:
        """Validate and return checksum address"""
        try:
            return to_checksum_address(address)
        except Exception as e:
            raise ValueError(f"Invalid Ethereum address: {address}") from e

    def validate_amount(self, amount: str) -> str:
        """Validate amount string"""
        try:
            float_amount = float(amount)
            if float_amount <= 0:
                raise ValueError
            return amount
        except ValueError:
            raise ValueError(f"Invalid amount: {amount}. Must be a positive number.")

    def execute_transfer(
        self,
        pkp_eth_address: str,
        token_address: str,
        recipient_address: str,
        amount: str,
        rpc_url: str,
        chain_id: int,
        decimals: int = 18
    ) -> dict:
        """Execute an ERC20 token transfer using Lit Protocol"""
        # Input validation
        pkp_eth_address = self.validate_address(pkp_eth_address)
        token_address = self.validate_address(token_address)
        recipient_address = self.validate_address(recipient_address)
        amount = self.validate_amount(amount)

        # Create policy object
        policy = {
            "type": "ERC20Transfer",
            "version": "1.0.0",
            "erc20Decimals": str(decimals),
            "maxAmount": amount,
            "allowedTokens": [token_address],
            "allowedRecipients": [recipient_address]
        }

        # Prepare parameters
        js_params = {
            "params": {
                "pkpEthAddress": pkp_eth_address,
                "tokenIn": token_address,
                "recipientAddress": recipient_address,
                "amountIn": amount,
                "chainId": str(chain_id),
                "rpcUrl": rpc_url
            }
        }

        try:
            # Get session signatures
            session_sigs = self.get_session_signatures()
            
            print(f"Executing Lit Action with IPFS ID: {self.tool.ipfs_cid}")
            result = self.client.execute_js(
                ipfs_id=self.tool.ipfs_cid,
                js_params=js_params,
                session_sigs=session_sigs
            )
            return result
        except Exception as e:
            raise Exception(f"Failed to execute transfer: {str(e)}")

def main():
    try:
        transfer_client = LitERC20Transfer(network="datil-dev")
        transfer_client.connect()
        
        # Test transfer
        result = transfer_client.execute_transfer(
            pkp_eth_address="0xc8BB61FB32cbfDc0534136798099709d779086b4",
            token_address="0x00cdfea7e11187BEB4a0CE835fea1745b124B26e",
            recipient_address="0xDFdC570ec0586D5c00735a2277c21Dcc254B3917",
            amount="1.0",
            rpc_url="https://base-sepolia-rpc.publicnode.com",
            chain_id=84532
        )
        
        print("Transfer result:", json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Error executing transfer: {str(e)}")

if __name__ == "__main__":
    main()
