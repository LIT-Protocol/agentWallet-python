# agent_wallet_python/client.py
from typing import List, Optional, Dict, Any
import subprocess
import json
from .models import AwTool
from .exceptions import ServerError

class AgentWalletClient:
    def __init__(self):
        """Initialize the Agent Wallet SDK client"""
        self._verify_setup()

    def _verify_setup(self):
        """Verify that Node.js and required packages are installed"""
        try:
            subprocess.run(["node", "--version"], check=True, capture_output=True)
            subprocess.run(["npm", "list", "@lit-protocol/agent-wallet"], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Required packages not installed. Please run: npm install @lit-protocol/agent-wallet")
        except FileNotFoundError:
            raise RuntimeError("Node.js is not installed. Please install Node.js and npm first.")

    def _wrap_tool_data(self, tool_data: dict, network: str = None) -> dict:
        """Wrap tool data in the expected format if needed"""
        if 'tool' in tool_data and 'network' in tool_data:
            return tool_data
        return {
            'tool': tool_data,
            'network': network or tool_data.get('network', 'unknown')
        }

    def _run_node_script(self, script: str) -> Any:
        """Run a Node.js script and return its output"""
        # Wrap the script in an async function
        full_script = f"""
        const {{ getToolByIpfsCid, getToolByName, listAllTools, listToolsByNetwork }} = require('@lit-protocol/aw-tool-registry');
        
        const params = {json.dumps({
            'script': script
        })};
        
        async function run() {{
            try {{
                console.error(`Running: ${{params.script}}`);
                const result = await eval(params.script);
                // Handle undefined/null results explicitly
                if (result === undefined || result === null) {{
                    console.log(JSON.stringify(null));
                }} else {{
                    console.log(JSON.stringify(result));
                }}
            }} catch (error) {{
                console.error(JSON.stringify({{ 
                    error: error.message, 
                    stack: error.stack,
                    script: params.script 
                }}));
                process.exit(1);
            }}
        }}
        
        process.on('unhandledRejection', (error) => {{
            console.error('Unhandled promise rejection:', error);
            process.exit(1);
        }});
        
        run().catch(error => {{
            console.error('Error in run:', error);
            process.exit(1);
        }});
        """
        
        try:
            result = subprocess.run(
                ["node", "-e", full_script],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.stderr and not result.stderr.startswith('Running:'):
                print(f"Node.js stderr: {result.stderr}")
                
            if result.returncode != 0:
                raise RuntimeError(f"Script failed with exit code {result.returncode}: {result.stderr}")
                
            if not result.stdout:
                return None
                
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError as e:
                if "undefined" in result.stdout:
                    return None
                print(f"JSON parse error on: {result.stdout}")
                raise RuntimeError(f"Failed to parse response: {str(e)}")
                
        except subprocess.CalledProcessError as e:
            try:
                error_data = json.loads(e.stderr)
                raise RuntimeError(error_data.get('error', 'Unknown error occurred'))
            except json.JSONDecodeError:
                raise RuntimeError(f"Error running Node script: {e.stderr}")

    def list_all_tools(self) -> List[AwTool]:
        """Get all available tools
        
        Returns:
            List of all available tools across all networks
        """
        result = self._run_node_script("listAllTools()")
        if not isinstance(result, list):
            raise ValueError("Unexpected response format from listAllTools")
        return [AwTool.model_validate(item) for item in result]

    def list_tools_by_network(self, network: str) -> List[AwTool]:
        """Get tools filtered by network
        
        Args:
            network: Network name to filter by (e.g., 'datil', 'datil-dev', 'datil-test')
            
        Returns:
            List of tools available on the specified network
        """
        result = self._run_node_script(f"listToolsByNetwork({json.dumps(network)})")
        if not isinstance(result, list):
            raise ValueError("Unexpected response format from listToolsByNetwork")
        
        wrapped_tools = [self._wrap_tool_data(tool, network) for tool in result]
        return [AwTool.model_validate(tool) for tool in wrapped_tools]

    def get_tool_by_ipfs_cid(self, cid: str) -> Optional[AwTool]:
        """Get a tool by its IPFS CID
        
        Args:
            cid: IPFS CID of the tool to find
            
        Returns:
            AwTool if found, None if not found
        """
        try:
            result = self._run_node_script(f"getToolByIpfsCid({json.dumps(cid)})")
            if not result:
                return None
            wrapped_result = self._wrap_tool_data(result)
            return AwTool.model_validate(wrapped_result)
        except RuntimeError:
            return None

    def get_tool_by_name(self, name: str, network: Optional[str] = None) -> Optional[AwTool]:
        """Get a tool by its name
        
        Args:
            name: Name of the tool to find (e.g., 'ERC20Transfer', 'UniswapSwap', 'SignEcdsa')
            network: Optional network to filter by
            
        Returns:
            AwTool if found, None if not found
        """
        try:
            # First try to get all tools and filter
            all_tools = self.list_all_tools()
            matching_tools = [t for t in all_tools if t.name == name]
            
            # If network is specified, filter by network too
            if network:
                matching_tools = [t for t in matching_tools if t.network == network]
                
            # Return first matching tool or None
            return matching_tools[0] if matching_tools else None
                
        except Exception as e:
            print(f"Error in get_tool_by_name: {str(e)}")
            return None

    def get_available_tool_names(self) -> List[str]:
        """Get a list of all available tool names
        
        Returns:
            List of unique tool names
        """
        try:
            tools = self.list_all_tools()
            return sorted(set(tool.name for tool in tools))
        except Exception as e:
            print(f"Error getting tool names: {str(e)}")
            return []
