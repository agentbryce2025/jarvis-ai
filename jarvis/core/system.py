"""
System Interface for JARVIS
Provides secure command execution and system interaction capabilities
"""

import logging
import subprocess
import shlex
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import asyncio
import signal
from datetime import datetime

class SecurityViolation(Exception):
    """Raised when a security violation is detected"""
    pass

class SystemCore:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.command_history: List[Dict[str, Any]] = []
        self._load_security_rules()
        
    def _load_security_rules(self):
        """Load security rules from configuration"""
        self.blocklist = set(self.config.get("command_blocklist", []))
        self.allowed_paths = set(self.config.get("allowed_paths", ["/tmp"]))
        self.max_runtime = self.config.get("max_runtime", 300)  # 5 minutes default
        
    async def execute_command(self, 
                            command: str, 
                            context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a system command securely
        
        Args:
            command: Command to execute
            context: Optional execution context
            
        Returns:
            Dictionary containing execution results
        """
        try:
            # Validate command
            self._validate_command(command)
            
            # Prepare command execution
            cmd_args = shlex.split(command)
            
            # Record command
            cmd_record = {
                "timestamp": datetime.now(),
                "command": command,
                "context": context,
                "status": "pending"
            }
            self.command_history.append(cmd_record)
            
            # Execute command with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.max_runtime
                )
                
                result = {
                    "status": "success" if process.returncode == 0 else "error",
                    "return_code": process.returncode,
                    "stdout": stdout.decode() if stdout else "",
                    "stderr": stderr.decode() if stderr else ""
                }
                
            except asyncio.TimeoutError:
                process.send_signal(signal.SIGTERM)
                result = {
                    "status": "timeout",
                    "error": f"Command execution timed out after {self.max_runtime} seconds"
                }
                
            # Update command record
            cmd_record.update({
                "status": result["status"],
                "result": result
            })
            
            return result
            
        except SecurityViolation as e:
            error_result = {
                "status": "security_violation",
                "error": str(e)
            }
            self.logger.warning(f"Security violation: {e}")
            return error_result
            
        except Exception as e:
            error_result = {
                "status": "error",
                "error": str(e)
            }
            self.logger.error(f"Command execution failed: {e}")
            return error_result
            
    def _validate_command(self, command: str) -> None:
        """
        Validate command against security rules
        
        Args:
            command: Command to validate
            
        Raises:
            SecurityViolation: If command violates security rules
        """
        # Check for blocked commands
        cmd_parts = shlex.split(command)
        if not cmd_parts:
            raise SecurityViolation("Empty command")
            
        base_cmd = Path(cmd_parts[0]).name
        if base_cmd in self.blocklist:
            raise SecurityViolation(f"Command '{base_cmd}' is blocked")
            
        # Check for dangerous patterns
        dangerous_patterns = [
            r"[;&|]",  # Command chaining
            r">[>&]",  # Output redirection
            r"<",      # Input redirection
            r"\$\(",   # Command substitution
            r"`",      # Backtick substitution
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, command):
                raise SecurityViolation(f"Dangerous pattern detected: {pattern}")
                
        # Validate paths
        for arg in cmd_parts[1:]:
            if arg.startswith("/"):
                path = Path(arg)
                if not any(str(path).startswith(str(allowed)) 
                          for allowed in self.allowed_paths):
                    raise SecurityViolation(f"Path not allowed: {path}")
                    
    def get_command_history(self, 
                          limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get command execution history
        
        Args:
            limit: Optional limit on number of records to return
            
        Returns:
            List of command execution records
        """
        if limit is None:
            return self.command_history
        return self.command_history[-limit:]
        
    def clear_command_history(self) -> None:
        """Clear command execution history"""
        self.command_history = []
        
    async def check_system_status(self) -> Dict[str, Any]:
        """
        Check system status
        
        Returns:
            Dictionary containing system status information
        """
        try:
            # Get system information
            cpu_info = await self.execute_command("top -bn1 | grep 'Cpu(s)'")
            mem_info = await self.execute_command("free -m")
            disk_info = await self.execute_command("df -h")
            
            return {
                "status": "success",
                "cpu": cpu_info.get("stdout", ""),
                "memory": mem_info.get("stdout", ""),
                "disk": disk_info.get("stdout", ""),
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to check system status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now()
            }