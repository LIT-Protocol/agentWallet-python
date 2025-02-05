# example_usage.py
from agent_wallet_python.client import AgentWalletClient
import os

from dotenv import load_dotenv
from lit_python_sdk import connect
from datetime import datetime, timedelta, timezone

def print_tool_info(tool, indent=""):
    """Helper to print tool information consistently"""
    if tool is None:
        print(f"{indent}No tool found")
        return
        
    print(f"{indent}- Tool: {tool.name}")
    print(f"{indent}  Network: {tool.network}")
    print(f"{indent}  IPFS CID: {tool.ipfs_cid}")
    print(f"{indent}  Description: {tool.description}")
    print(f"{indent}  Parameter Descriptions:")
    for param, desc in tool.parameter_descriptions.items():
        print(f"{indent}    - {param}: {desc}")

def main():
    try:
        client = AgentWalletClient()
        
        # 1. List available tools
        tool_names = client.get_available_tool_names()
        print(f"\nAvailable tools: {', '.join(tool_names)}")
        
        # 2. List all tools and networks
        print("\nListing all tools:")
        all_tools = client.list_all_tools()
        for tool in all_tools:
            print_tool_info(tool)
        print(f"\nTotal tools found: {len(all_tools)}")
        
        # 3. Show tools by network
        networks = ["datil", "datil-dev", "datil-test"]
        for network in networks:
            tools = client.list_tools_by_network(network)
            print(f"\nTools on {network} network: {len(tools)}")
            for tool in tools:
                print_tool_info(tool, "  ")
        
        # 4. Look up specific tools
        print("\nLooking up specific tools:")
        
        # ERC20Transfer on datil network
        print("\nLooking up ERC20Transfer on datil-dev network:")
        tool = client.get_tool_by_name("ERC20Transfer", network="datil-dev")
        print_tool_info(tool, "  ")
        
        # UniswapSwap by IPFS CID
        print("\nLooking up first UniswapSwap tool by IPFS CID:")
        uniswap_tools = [t for t in all_tools if t.name == "UniswapSwap"]
        if uniswap_tools:
            tool = client.get_tool_by_ipfs_cid(uniswap_tools[0].ipfs_cid)
            print_tool_info(tool, "  ")
            
        # 5 example erc20 transfer
        client = connect()
        load_dotenv()
        client.set_auth_token(os.getenv("LIT_PRIVATE_KEY"))
        client.new(lit_network="datil-dev", debug=True)
        client.connect()
        # Get session signatures
        expiration = (datetime.now(timezone.utc) + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
        session_sigs_result = client.get_session_sigs(
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
        session_sigs = session_sigs_result["sessionSigs"]

        # Execute the code
        js_code = """
            (async () => {
                console.log("Testing executeJs endpoint");
                Lit.Actions.setResponse({response: "Test successful"});
            })()
        """

        result = client.execute_js(
            code=js_code,
            js_params={},
            session_sigs=session_sigs
        )
        print(result)

        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
