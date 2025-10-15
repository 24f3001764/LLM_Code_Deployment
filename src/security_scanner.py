import re
import logging
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)


class SecurityScanner:
    """Scan code for potential secrets and sensitive information"""
    
    # Common patterns for secrets
    SECRET_PATTERNS = [
        (r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', 'API Key'),
        (r'(?i)(secret[_-]?key|secretkey)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', 'Secret Key'),
        (r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']([^"\']{8,})["\']', 'Password'),
        (r'(?i)(token)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', 'Token'),
        (r'(?i)(github[_-]?token)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', 'GitHub Token'),
        (r'(?i)(openai[_-]?api[_-]?key)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', 'OpenAI API Key'),
        (r'sk-[a-zA-Z0-9]{20,}', 'OpenAI API Key (sk- prefix)'),
        (r'ghp_[a-zA-Z0-9]{36,}', 'GitHub Personal Access Token'),
        (r'gho_[a-zA-Z0-9]{36,}', 'GitHub OAuth Token'),
        (r'ghs_[a-zA-Z0-9]{36,}', 'GitHub App Token'),
        (r'(?i)bearer\s+[a-zA-Z0-9_\-\.]{20,}', 'Bearer Token'),
        (r'(?i)(aws[_-]?access[_-]?key[_-]?id)\s*[:=]\s*["\']([A-Z0-9]{20})["\']', 'AWS Access Key'),
        (r'(?i)(aws[_-]?secret[_-]?access[_-]?key)\s*[:=]\s*["\']([a-zA-Z0-9/+=]{40})["\']', 'AWS Secret Key'),
        (r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----', 'Private Key'),
        (r'(?i)(database[_-]?url|db[_-]?url)\s*[:=]\s*["\']([^"\']+)["\']', 'Database URL'),
    ]
    
    # Whitelist patterns (things that look like secrets but aren't)
    WHITELIST_PATTERNS = [
        r'example\.com',
        r'your-.*-here',
        r'placeholder',
        r'dummy',
        r'test[_-]?key',
        r'fake[_-]?token',
        r'xxx+',
        r'\*\*\*+',
    ]
    
    def scan_file(self, file_path: Path) -> List[Tuple[str, str, int]]:
        """
        Scan a file for potential secrets
        Returns: List of (secret_type, matched_text, line_number)
        """
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                # Skip comments
                if line.strip().startswith(('#', '//', '/*', '*')):
                    continue
                
                for pattern, secret_type in self.SECRET_PATTERNS:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        matched_text = match.group(0)
                        
                        # Check if it's whitelisted
                        if not self._is_whitelisted(matched_text):
                            findings.append((secret_type, matched_text, line_num))
        
        except Exception as e:
            logger.warning(f"Error scanning {file_path}: {e}")
        
        return findings
    
    def _is_whitelisted(self, text: str) -> bool:
        """Check if text matches whitelist patterns"""
        for pattern in self.WHITELIST_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def scan_directory(self, directory: Path) -> dict:
        """
        Scan all files in a directory
        Returns: Dict mapping file paths to findings
        """
        results = {}
        
        # File extensions to scan
        extensions = ['.html', '.js', '.css', '.py', '.json', '.yaml', '.yml', '.env', '.txt', '.md']
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix in extensions:
                findings = self.scan_file(file_path)
                if findings:
                    results[str(file_path.relative_to(directory))] = findings
        
        return results
    
    def scan_and_report(self, directory: Path) -> bool:
        """
        Scan directory and log findings
        Returns: True if no secrets found, False if secrets detected
        """
        logger.info(f"Scanning {directory} for secrets...")
        results = self.scan_directory(directory)
        
        if not results:
            logger.info("✓ No secrets detected")
            return True
        
        logger.warning(f"⚠ Found potential secrets in {len(results)} file(s):")
        for file_path, findings in results.items():
            logger.warning(f"  {file_path}:")
            for secret_type, matched_text, line_num in findings:
                # Mask the secret for logging
                masked = self._mask_secret(matched_text)
                logger.warning(f"    Line {line_num}: {secret_type} - {masked}")
        
        return False
    
    def _mask_secret(self, text: str) -> str:
        """Mask secret for safe logging"""
        if len(text) <= 8:
            return '*' * len(text)
        return text[:4] + '*' * (len(text) - 8) + text[-4:]
    
    def sanitize_file(self, file_path: Path) -> bool:
        """
        Remove detected secrets from a file
        Returns: True if file was modified, False otherwise
        """
        findings = self.scan_file(file_path)
        if not findings:
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Replace secrets with placeholders
            for secret_type, matched_text, _ in findings:
                if not self._is_whitelisted(matched_text):
                    placeholder = f"[REDACTED_{secret_type.upper().replace(' ', '_')}]"
                    content = content.replace(matched_text, placeholder)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Sanitized {file_path}")
                return True
        
        except Exception as e:
            logger.error(f"Error sanitizing {file_path}: {e}")
        
        return False
