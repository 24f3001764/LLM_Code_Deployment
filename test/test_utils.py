"""
Unit tests for utility functions
"""
import pytest
import asyncio
import base64
from pathlib import Path
import tempfile
import shutil
from src.utils import decode_and_save_attachments, sanitize_repo_name, get_mit_license
from src.models import Attachment


class TestDecodeAndSaveAttachments:
    """Test decode_and_save_attachments function"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for tests"""
        temp = tempfile.mkdtemp()
        yield temp
        # Cleanup
        shutil.rmtree(temp, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_decode_single_attachment(self, temp_dir, monkeypatch):
        """Test decoding a single attachment"""
        # Mock the config
        from src import config as config_module
        monkeypatch.setattr(config_module.config, 'TEMP_ATTACHMENTS_DIR', temp_dir)
        
        # Create a simple base64 encoded image (1x1 red pixel PNG)
        image_data = base64.b64encode(
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf'
            b'\xc0\x00\x00\x00\x00\xff\xff\x03\x00\x00\x05\x00\x01\x0d\n-\xb4'
            b'\x00\x00\x00\x00IEND\xaeB`\x82'
        ).decode('utf-8')
        
        attachments = [
            Attachment(
                name="test.png",
                url=f"data:image/png;base64,{image_data}"
            )
        ]
        
        saved_paths = await decode_and_save_attachments(attachments, "test-task-001")
        
        assert len(saved_paths) == 1
        assert saved_paths[0].name == "test.png"
        assert saved_paths[0].exists()
    
    @pytest.mark.asyncio
    async def test_decode_multiple_attachments(self, temp_dir, monkeypatch):
        """Test decoding multiple attachments"""
        from src import config as config_module
        monkeypatch.setattr(config_module.config, 'TEMP_ATTACHMENTS_DIR', temp_dir)
        
        # Simple base64 data
        data1 = base64.b64encode(b"file1 content").decode('utf-8')
        data2 = base64.b64encode(b"file2 content").decode('utf-8')
        
        attachments = [
            Attachment(name="file1.txt", url=f"data:text/plain;base64,{data1}"),
            Attachment(name="file2.txt", url=f"data:text/plain;base64,{data2}")
        ]
        
        saved_paths = await decode_and_save_attachments(attachments, "test-task-002")
        
        assert len(saved_paths) == 2
        assert all(path.exists() for path in saved_paths)
    
    @pytest.mark.asyncio
    async def test_decode_empty_attachments(self, temp_dir, monkeypatch):
        """Test with empty attachments list"""
        from src import config as config_module
        monkeypatch.setattr(config_module.config, 'TEMP_ATTACHMENTS_DIR', temp_dir)
        
        saved_paths = await decode_and_save_attachments([], "test-task-003")
        
        assert len(saved_paths) == 0
    
    @pytest.mark.asyncio
    async def test_decode_invalid_data_uri(self, temp_dir, monkeypatch):
        """Test with invalid data URI format"""
        from src import config as config_module
        monkeypatch.setattr(config_module.config, 'TEMP_ATTACHMENTS_DIR', temp_dir)
        
        attachments = [
            Attachment(name="invalid.txt", url="not-a-valid-data-uri")
        ]
        
        saved_paths = await decode_and_save_attachments(attachments, "test-task-004")
        
        # Should skip invalid attachments
        assert len(saved_paths) == 0


class TestSanitizeRepoName:
    """Test sanitize_repo_name function"""
    
    def test_simple_task_id(self):
        """Test with simple alphanumeric task ID"""
        result = sanitize_repo_name("task123")
        assert result == "task123"
    
    def test_task_id_with_hyphens(self):
        """Test task ID that already has hyphens"""
        result = sanitize_repo_name("task-123-abc")
        assert result == "task-123-abc"
    
    def test_task_id_with_underscores(self):
        """Test task ID with underscores"""
        result = sanitize_repo_name("task_123_abc")
        assert result == "task_123_abc"
    
    def test_task_id_with_dots(self):
        """Test task ID with dots"""
        result = sanitize_repo_name("task.123.abc")
        assert result == "task.123.abc"
    
    def test_task_id_with_spaces(self):
        """Test task ID with spaces (should be replaced)"""
        result = sanitize_repo_name("task 123 abc")
        assert result == "task-123-abc"
    
    def test_task_id_with_special_chars(self):
        """Test task ID with special characters"""
        result = sanitize_repo_name("task@123#abc!")
        assert result == "task-123-abc-"
    
    def test_task_id_with_leading_trailing_hyphens(self):
        """Test task ID that would have leading/trailing hyphens"""
        result = sanitize_repo_name("@task123@")
        assert result == "task123"
    
    def test_task_id_with_mixed_case(self):
        """Test task ID with mixed case (should be preserved)"""
        result = sanitize_repo_name("TaskABC123")
        assert result == "TaskABC123"
    
    def test_task_id_with_unicode(self):
        """Test task ID with unicode characters"""
        result = sanitize_repo_name("task-café-123")
        assert "-" in result  # Unicode chars should be replaced


class TestGetMitLicense:
    """Test get_mit_license function"""
    
    def test_returns_string(self):
        """Test that function returns a string"""
        license_text = get_mit_license()
        assert isinstance(license_text, str)
    
    def test_contains_mit_license(self):
        """Test that returned text contains MIT License"""
        license_text = get_mit_license()
        assert "MIT License" in license_text
    
    def test_contains_copyright(self):
        """Test that license contains copyright notice"""
        license_text = get_mit_license()
        assert "Copyright" in license_text
    
    def test_contains_permission_text(self):
        """Test that license contains permission text"""
        license_text = get_mit_license()
        assert "Permission is hereby granted" in license_text
    
    def test_contains_warranty_disclaimer(self):
        """Test that license contains warranty disclaimer"""
        license_text = get_mit_license()
        assert "WITHOUT WARRANTY OF ANY KIND" in license_text
    
    def test_not_empty(self):
        """Test that license text is not empty"""
        license_text = get_mit_license()
        assert len(license_text) > 0
    
    def test_multiline(self):
        """Test that license text has multiple lines"""
        license_text = get_mit_license()
        assert "\n" in license_text
        assert len(license_text.split("\n")) > 5
