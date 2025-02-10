"""
Self-Modification and Code Generation Module for JARVIS
Handles safe code modifications and generation with comprehensive validation
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import ast
import inspect
import astroid
from pylint import epylint
import git
import tempfile
import subprocess
from datetime import datetime

class SecurityCheckFailure(Exception):
    """Raised when code fails security checks"""
    pass

class ValidationFailure(Exception):
    """Raised when code fails validation"""
    pass

class CodeEvolver:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.repo = self._initialize_repo()
        self.modification_history: List[Dict[str, Any]] = []
        
    def _initialize_repo(self) -> git.Repo:
        """Initialize Git repository for version control"""
        try:
            return git.Repo(".")
        except git.InvalidGitRepositoryError:
            return git.Repo.init(".")
            
    async def generate_code(self,
                          specification: Dict[str, Any],
                          context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate code based on specification
        
        Args:
            specification: Code generation specification
            context: Optional generation context
            
        Returns:
            Dictionary containing generated code and metadata
        """
        try:
            # Generate code (placeholder for actual generation logic)
            generated_code = "# Generated code here\n"
            
            # Validate generated code
            self._validate_code(generated_code)
            
            return {
                "status": "success",
                "code": generated_code,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Code generation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
            
    async def modify_code(self,
                         file_path: Path,
                         modifications: Dict[str, Any],
                         description: str) -> Dict[str, Any]:
        """
        Safely modify existing code
        
        Args:
            file_path: Path to file to modify
            modifications: Requested modifications
            description: Description of modifications
            
        Returns:
            Dictionary containing modification results
        """
        try:
            # Create backup
            backup_path = self._create_backup(file_path)
            
            # Apply modifications
            modified_code = self._apply_modifications(file_path, modifications)
            
            # Validate modifications
            self._validate_code(modified_code)
            
            # Test changes
            test_result = self._test_modifications(modified_code)
            if not test_result["success"]:
                self._restore_backup(backup_path, file_path)
                raise ValidationFailure(f"Tests failed: {test_result['error']}")
                
            # Save changes
            file_path.write_text(modified_code)
            
            # Commit changes
            self._commit_changes(file_path, description)
            
            # Record modification
            self.modification_history.append({
                "file": str(file_path),
                "description": description,
                "timestamp": datetime.now(),
                "backup": str(backup_path)
            })
            
            return {
                "status": "success",
                "file": str(file_path),
                "backup": str(backup_path)
            }
            
        except Exception as e:
            self.logger.error(f"Code modification failed: {e}")
            if backup_path and backup_path.exists():
                self._restore_backup(backup_path, file_path)
            return {
                "status": "error",
                "error": str(e)
            }
            
    def _validate_code(self, code: str) -> None:
        """
        Validate code for security and correctness
        
        Args:
            code: Code to validate
            
        Raises:
            SecurityCheckFailure: If code fails security checks
            ValidationFailure: If code fails validation
        """
        # Parse AST
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise ValidationFailure(f"Syntax error: {e}")
            
        # Security checks
        self._check_security(tree)
        
        # Static analysis
        self._run_static_analysis(code)
        
    def _check_security(self, tree: ast.AST) -> None:
        """
        Perform security checks on AST
        
        Args:
            tree: AST to check
            
        Raises:
            SecurityCheckFailure: If security checks fail
        """
        class SecurityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.violations = []
                
            def visit_Call(self, node):
                # Check for dangerous function calls
                dangerous_functions = {
                    "eval", "exec", "open", "subprocess.call",
                    "subprocess.Popen", "os.system"
                }
                
                if isinstance(node.func, ast.Name):
                    if node.func.id in dangerous_functions:
                        self.violations.append(
                            f"Dangerous function call: {node.func.id}"
                        )
                self.generic_visit(node)
                
        visitor = SecurityVisitor()
        visitor.visit(tree)
        
        if visitor.violations:
            raise SecurityCheckFailure(
                f"Security violations found: {', '.join(visitor.violations)}"
            )
            
    def _run_static_analysis(self, code: str) -> None:
        """
        Run static analysis on code
        
        Args:
            code: Code to analyze
            
        Raises:
            ValidationFailure: If static analysis fails
        """
        # Create temporary file for analysis
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as temp_file:
            temp_file.write(code)
            temp_file.flush()
            
            # Run pylint
            (pylint_stdout, pylint_stderr) = epylint.py_run(
                return_std=True,
                command_options=[temp_file.name]
            )
            
            # Check results
            if pylint_stderr.getvalue():
                raise ValidationFailure(
                    f"Static analysis failed: {pylint_stderr.getvalue()}"
                )
                
    def _create_backup(self, file_path: Path) -> Path:
        """Create backup of file"""
        backup_path = file_path.with_suffix(f".bak_{datetime.now():%Y%m%d_%H%M%S}")
        backup_path.write_text(file_path.read_text())
        return backup_path
        
    def _restore_backup(self, backup_path: Path, file_path: Path) -> None:
        """Restore file from backup"""
        if backup_path.exists():
            file_path.write_text(backup_path.read_text())
            
    def _apply_modifications(self,
                           file_path: Path,
                           modifications: Dict[str, Any]) -> str:
        """Apply modifications to code"""
        # Implementation of code modification logic
        return file_path.read_text()  # Placeholder
        
    def _test_modifications(self, code: str) -> Dict[str, Any]:
        """Test modified code"""
        # Implementation of testing logic
        return {"success": True}
        
    def _commit_changes(self, file_path: Path, description: str) -> None:
        """Commit changes to version control"""
        try:
            self.repo.index.add([str(file_path)])
            self.repo.index.commit(
                f"[CodeEvolver] {description}"
            )
        except Exception as e:
            self.logger.error(f"Failed to commit changes: {e}")
            
    def get_modification_history(self) -> List[Dict[str, Any]]:
        """Get history of code modifications"""
        return self.modification_history
        
    def rollback_modification(self, timestamp: datetime) -> bool:
        """
        Rollback to specific point in modification history
        
        Args:
            timestamp: Timestamp to rollback to
            
        Returns:
            True if rollback successful, False otherwise
        """
        try:
            # Find modification entry
            for mod in self.modification_history:
                if mod["timestamp"] == timestamp:
                    backup_path = Path(mod["backup"])
                    file_path = Path(mod["file"])
                    
                    # Restore backup
                    self._restore_backup(backup_path, file_path)
                    
                    # Commit rollback
                    self._commit_changes(
                        file_path,
                        f"Rollback to {timestamp}"
                    )
                    
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Rollback failed: {e}")
            return False