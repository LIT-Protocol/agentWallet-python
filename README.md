# Lit Protocol Agent Wallet Python SDK

A Python SDK for interacting with Lit Protocol's Agent Wallet and executing ERC20 transfers. This SDK provides a wrapper around Lit Protocol's tools and Agent Wallet functionality.

## Prerequisites

- Python 3.7+
- Node.js and npm
- `@lit-protocol/agent-wallet` npm package
- Required Python packages (install via pip):
  - web3
  - eth-utils
  - eth-typing
  - python-dotenv
  - lit-python-sdk

## Installation

1. First, install the required Node.js package:
```bash
npm install @lit-protocol/agent-wallet
```
Install the Python dependencies:

```bash
pip install web3 eth-utils eth-typing python-dotenv lit-python-sdk
```
Set up your environment variables:
Create a .env file in your project root and add:

```bash
LIT_PRIVATE_KEY=your_lit_private_key_here
```
Features

ERC20 token transfers using Lit Protocol
Tool management (listing, searching, and retrieving tool information)
Session signature management
Address validation
Network-specific tool queries

Usage Examples
Basic Tool Management
pythonCopyfrom agent_wallet_python.client import AgentWalletClient

# Initialize the client
client = AgentWalletClient()

# List available tools
```bash
tool_names = client.get_available_tool_names()
print(f"Available tools: {', '.join(tool_names)}")
```
# Get specific tool
```bash
tool = client.get_tool_by_name("ERC20Transfer", network="datil-dev")
ERC20 Token Transfer
pythonCopyfrom lit_erc20_transfer import LitERC20Transfer
```
# Initialize transfer client
```bash
transfer_client = LitERC20Transfer(network="datil-dev")
transfer_client.connect()
```
# Execute transfer
result = transfer_client.execute_transfer(
    pkp_eth_address="0xYourPKPAddress",
    token_address="0xTokenAddress",
    recipient_address="0xRecipientAddress",
    amount="1.0",
    rpc_url="https://your-rpc-url",
    chain_id=84532
)
API Reference
LitERC20Transfer
Methods

connect(): Initialize and connect to Lit Protocol
execute_transfer(pkp_eth_address, token_address, recipient_address, amount, rpc_url, chain_id, decimals=18): Execute an ERC20 token transfer
get_session_signatures(): Get session signatures for Lit Protocol
validate_address(address): Validate Ethereum addresses
validate_amount(amount): Validate transfer amounts

AgentWalletClient
Methods

list_all_tools(): Get all available tools across networks
list_tools_by_network(network): Get tools filtered by network
get_tool_by_ipfs_cid(cid): Get a tool by its IPFS CID
get_tool_by_name(name, network=None): Get a tool by its name
get_available_tool_names(): Get a list of all available tool names

Error Handling
The SDK includes comprehensive error handling for:

Invalid addresses
Invalid amounts
Network connection issues
Tool retrieval failures
Session signature errors

Network Support
The SDK supports multiple networks:

datil
datil-dev
datil-test

Security Considerations

Always keep your LIT_PRIVATE_KEY secure and never commit it to version control
Validate all addresses and amounts before executing transfers
Use appropriate session expiration times
Implement proper error handling in production environments

Contributing
Contributions are welcome! Please submit pull requests with any improvements or bug fixes.
License
[MIT]
Copy
You can now copy this entire code block and use it as your README.md file. The formatting will be preserved exactly as shown.
