#!/usr/bin/env python3
"""
Serveur MCP simple pour exécuter du code Python
"""

import asyncio
import json
import sys
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Any, Dict

# Configuration du serveur MCP
SERVER_INFO = {
    "name": "python-executor",
    "version": "1.0.0"
}

class MCPServer:
    def __init__(self):
        self.tools = {
            "execute_python": {
                "name": "execute_python",
                "description": "Exécute du code Python et retourne le résultat ou l'erreur",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Le code Python à exécuter"
                        },
                        "timeout": {
                            "type": "number",
                            "description": "Timeout en secondes (défaut: 10)",
                            "default": 10
                        }
                    },
                    "required": ["code"]
                }
            }
        }

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Traite une requête MCP"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")

        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {
                                "listChanged": False
                            }
                        },
                        "serverInfo": SERVER_INFO
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": list(self.tools.values())
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "execute_python":
                    result = await self.execute_python_code(
                        arguments.get("code", ""),
                        arguments.get("timeout", 10)
                    )
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": result
                                }
                            ]
                        }
                    }
                else:
                    raise ValueError(f"Outil inconnu: {tool_name}")
            
            else:
                raise ValueError(f"Méthode non supportée: {method}")
                
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }

    async def execute_python_code(self, code: str, timeout: float = 10) -> str:
        """Exécute du code Python dans un environnement sécurisé"""
        if not code.strip():
            return "Erreur: Code vide"

        # Créer un fichier temporaire pour le code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            # Exécuter le code Python
            process = await asyncio.create_subprocess_exec(
                sys.executable, temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                return f"Erreur: Timeout après {timeout} secondes"

            # Préparer le résultat
            result_parts = []
            
            if stdout:
                result_parts.append(f"Sortie:\n{stdout.decode('utf-8', errors='replace')}")
            
            if stderr:
                result_parts.append(f"Erreur:\n{stderr.decode('utf-8', errors='replace')}")
            
            if process.returncode != 0:
                result_parts.append(f"Code de sortie: {process.returncode}")
            
            if not result_parts:
                return "Exécution réussie (aucune sortie)"
            
            return "\n\n".join(result_parts)

        finally:
            # Nettoyer le fichier temporaire
            try:
                os.unlink(temp_file)
            except:
                pass

    async def run(self):
        """Lance le serveur MCP"""
        while True:
            try:
                # Lire une ligne depuis stdin
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    break
                
                # Parser la requête JSON-RPC
                try:
                    request = json.loads(line.strip())
                except json.JSONDecodeError:
                    continue
                
                # Traiter la requête
                response = await self.handle_request(request)
                
                # Envoyer la réponse
                print(json.dumps(response), flush=True)
                
            except Exception as e:
                # Envoyer une erreur générique
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Erreur serveur: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)

async def main():
    """Point d'entrée principal"""
    server = MCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())

