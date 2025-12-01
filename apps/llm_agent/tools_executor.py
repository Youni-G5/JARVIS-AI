from typing import List, Dict, Any
import aiohttp
import os

class ToolsExecutor:
    """Exécuteur de tools (actions externes)."""
    
    def __init__(self):
        self.action_exec_host = os.getenv("ACTION_EXEC_HOST", "localhost:8001")
        self.memory_host = os.getenv("MEMORY_HOST", "localhost:8003")
        self.notify_host = os.getenv("NOTIFY_HOST", "localhost:8004")
    
    async def execute_tools(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Exécute une liste de tool calls et retourne les résultats."""
        results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call.get('tool')
            call_data = tool_call.get('call', {})
            
            result = await self._execute_single_tool(tool_name, call_data)
            results.append({
                'tool': tool_name,
                'input': call_data,
                'output': result
            })
        
        return results
    
    async def _execute_single_tool(self, tool: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute un tool spécifique."""
        
        if tool == "action_exec":
            return await self._call_action_exec(data)
        
        elif tool == "memory":
            return await self._call_memory(data)
        
        elif tool == "notify":
            return await self._call_notify(data)
        
        else:
            return {"error": f"Unknown tool: {tool}"}
    
    async def _call_action_exec(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Appelle le service Action Exec."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://{self.action_exec_host}/run",
                    json=data
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        return {"error": f"Action exec failed: {resp.status}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def _call_memory(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Appelle le service Memory."""
        try:
            method = data.get('method', 'write')
            endpoint = '/write' if method == 'write' else '/query'
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://{self.memory_host}{endpoint}",
                    json=data
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        return {"error": f"Memory service failed: {resp.status}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def _call_notify(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Appelle le service de notifications."""
        # TODO: Implémenter service notifications
        return {"status": "notification_sent", "message": data.get('message', '')}