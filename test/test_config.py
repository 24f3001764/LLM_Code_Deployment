"""
Unit tests for configuration
"""
import pytest
import os
from unittest.mock import patch


class TestConfig:
    """Test Config class"""
    
    def test_config_defaults(self):
        """Test default configuration values"""
        from src.config import Config
        
        # Test default values
        assert Config.API_HOST == os.getenv("API_HOST", "0.0.0.0")
        assert Config.API_PORT == int(os.getenv("PORT", "7860"))
        assert Config.GENERATED_APPS_DIR == "generated_apps"
        assert Config.TEMP_ATTACHMENTS_DIR == "temp_attachments"
        assert Config.EVALUATION_TIMEOUT == 600
        assert Config.RETRY_DELAYS == [1, 2, 4, 8, 16]
    
    def test_config_from_env(self):
        """Test loading configuration from environment variables"""
        with patch.dict(os.environ, {
            'STUDENT_SECRET': 'test-secret',
            'OPENAI_API_KEY': 'test-openai-key',
            'GITHUB_TOKEN': 'test-github-token',
            'GITHUB_USERNAME': 'test-user',
            'API_HOST': '127.0.0.1',
            'PORT': '8080'
        }):
            # Re-import to get fresh config with new env vars
            import importlib
            from src import config as config_module
            importlib.reload(config_module)
            
            assert config_module.config.STUDENT_SECRET == 'test-secret'
            assert config_module.config.OPENAI_API_KEY == 'test-openai-key'
            assert config_module.config.GITHUB_TOKEN == 'test-github-token'
            assert config_module.config.GITHUB_USERNAME == 'test-user'
            assert config_module.config.API_HOST == '127.0.0.1'
            assert config_module.config.API_PORT == 8080
    
    def test_validate_success(self):
        """Test successful validation with all required fields"""
        from src.config import Config
        
        with patch.dict(os.environ, {
            'STUDENT_SECRET': 'test-secret',
            'OPENAI_API_KEY': 'test-openai-key',
            'GITHUB_TOKEN': 'test-github-token',
            'GITHUB_USERNAME': 'test-user'
        }):
            import importlib
            from src import config as config_module
            importlib.reload(config_module)
            
            # Should not raise any exception
            config_module.config.validate()
    
    def test_validate_missing_student_secret(self):
        """Test validation fails when STUDENT_SECRET is missing"""
        from src.config import Config
        
        with patch.dict(os.environ, {
            'STUDENT_SECRET': '',
            'OPENAI_API_KEY': 'test-openai-key',
            'GITHUB_TOKEN': 'test-github-token',
            'GITHUB_USERNAME': 'test-user'
        }, clear=True):
            import importlib
            from src import config as config_module
            importlib.reload(config_module)
            
            with pytest.raises(ValueError) as exc_info:
                config_module.config.validate()
            assert "STUDENT_SECRET not set" in str(exc_info.value)
    
    def test_validate_missing_openai_key(self):
        """Test validation fails when OPENAI_API_KEY is missing"""
        from src.config import Config
        
        with patch.dict(os.environ, {
            'STUDENT_SECRET': 'test-secret',
            'OPENAI_API_KEY': '',
            'GITHUB_TOKEN': 'test-github-token',
            'GITHUB_USERNAME': 'test-user'
        }, clear=True):
            import importlib
            from src import config as config_module
            importlib.reload(config_module)
            
            with pytest.raises(ValueError) as exc_info:
                config_module.config.validate()
            assert "OPENAI_API_KEY not set" in str(exc_info.value)
    
    def test_validate_missing_github_token(self):
        """Test validation fails when GITHUB_TOKEN is missing"""
        from src.config import Config
        
        with patch.dict(os.environ, {
            'STUDENT_SECRET': 'test-secret',
            'OPENAI_API_KEY': 'test-openai-key',
            'GITHUB_TOKEN': '',
            'GITHUB_USERNAME': 'test-user'
        }, clear=True):
            import importlib
            from src import config as config_module
            importlib.reload(config_module)
            
            with pytest.raises(ValueError) as exc_info:
                config_module.config.validate()
            assert "GITHUB_TOKEN not set" in str(exc_info.value)
    
    def test_validate_missing_github_username(self):
        """Test validation fails when GITHUB_USERNAME is missing"""
        from src.config import Config
        
        with patch.dict(os.environ, {
            'STUDENT_SECRET': 'test-secret',
            'OPENAI_API_KEY': 'test-openai-key',
            'GITHUB_TOKEN': 'test-github-token',
            'GITHUB_USERNAME': ''
        }, clear=True):
            import importlib
            from src import config as config_module
            importlib.reload(config_module)
            
            with pytest.raises(ValueError) as exc_info:
                config_module.config.validate()
            assert "GITHUB_USERNAME not set" in str(exc_info.value)
    
    def test_validate_multiple_missing_fields(self):
        """Test validation fails with multiple missing fields"""
        from src.config import Config
        
        with patch.dict(os.environ, {
            'STUDENT_SECRET': '',
            'OPENAI_API_KEY': '',
            'GITHUB_TOKEN': '',
            'GITHUB_USERNAME': ''
        }, clear=True):
            import importlib
            from src import config as config_module
            importlib.reload(config_module)
            
            with pytest.raises(ValueError) as exc_info:
                config_module.config.validate()
            error_msg = str(exc_info.value)
            assert "STUDENT_SECRET not set" in error_msg
            assert "OPENAI_API_KEY not set" in error_msg
            assert "GITHUB_TOKEN not set" in error_msg
            assert "GITHUB_USERNAME not set" in error_msg
    
    def test_port_conversion_to_int(self):
        """Test that PORT environment variable is converted to int"""
        with patch.dict(os.environ, {'PORT': '9000'}):
            import importlib
            from src import config as config_module
            importlib.reload(config_module)
            
            assert isinstance(config_module.config.API_PORT, int)
            assert config_module.config.API_PORT == 9000
    
    def test_retry_delays_exponential(self):
        """Test that retry delays follow exponential backoff pattern"""
        from src.config import Config
        
        delays = Config.RETRY_DELAYS
        assert len(delays) > 0
        # Check exponential pattern (each should be roughly double the previous)
        for i in range(1, len(delays)):
            assert delays[i] >= delays[i-1]
