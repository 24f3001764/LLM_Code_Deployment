"""
Property-based tests for utility functions using Hypothesis
"""
import pytest
from hypothesis import given, strategies as st, assume, example
from pathlib import Path
import re
from src.utils import sanitize_repo_name, get_mit_license


class TestSanitizeRepoNameHypothesis:
    """Property-based tests for sanitize_repo_name function"""
    
    @given(task_id=st.text(min_size=1, max_size=100))
    def test_sanitize_always_returns_valid_github_name(self, task_id):
        """Test that sanitize_repo_name always returns a valid GitHub repo name"""
        result = sanitize_repo_name(task_id)
        
        # GitHub repo name requirements:
        # - Can only contain alphanumeric characters, hyphens, and underscores
        # - Cannot start or end with hyphen
        # - Max length 100 characters
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert len(result) <= 100
        
        # Check valid characters
        assert re.match(r'^[a-zA-Z0-9_-]+$', result), f"Invalid characters in: {result}"
        
        # Check doesn't start or end with hyphen
        assert not result.startswith('-'), f"Starts with hyphen: {result}"
        assert not result.endswith('-'), f"Ends with hyphen: {result}"
    
    @given(
        task_id=st.text(
            alphabet=st.characters(whitelist_categories=('Ll', 'Nd'), whitelist_characters='-_'),
            min_size=1,
            max_size=100
        )
    )
    def test_sanitize_preserves_valid_names(self, task_id):
        """Test that already valid names are mostly preserved"""
        # Skip if starts/ends with hyphen
        assume(not task_id.startswith('-') and not task_id.endswith('-'))
        
        result = sanitize_repo_name(task_id)
        
        # Should be similar to original (lowercase version)
        assert result.lower() == task_id.lower() or result.replace('-', '') == task_id.replace('-', '')
    
    @given(task_id=st.text(min_size=1, max_size=200))
    @example(task_id="test@#$%task")
    @example(task_id="---test---")
    @example(task_id="UPPERCASE_TASK")
    @example(task_id="task with spaces")
    @example(task_id="task/with/slashes")
    def test_sanitize_handles_special_characters(self, task_id):
        """Test that special characters are handled correctly"""
        result = sanitize_repo_name(task_id)
        
        # Should not contain special characters
        assert '@' not in result
        assert '#' not in result
        assert '$' not in result
        assert '%' not in result
        assert ' ' not in result
        assert '/' not in result
        assert '\\' not in result
    
    @given(task_id=st.text(alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ', min_size=1, max_size=50))
    def test_sanitize_converts_to_lowercase(self, task_id):
        """Test that uppercase letters are converted to lowercase"""
        result = sanitize_repo_name(task_id)
        
        # Should be all lowercase
        assert result.islower() or result.replace('-', '').replace('_', '').islower()
    
    @given(task_id=st.text(min_size=101, max_size=500))
    def test_sanitize_truncates_long_names(self, task_id):
        """Test that long names are truncated to 100 characters"""
        result = sanitize_repo_name(task_id)
        
        assert len(result) <= 100
    
    @given(
        prefix=st.text(min_size=0, max_size=10),
        middle=st.text(
            alphabet=st.characters(whitelist_categories=('Ll', 'Nd')),
            min_size=1,
            max_size=20
        ),
        suffix=st.text(min_size=0, max_size=10)
    )
    def test_sanitize_idempotent(self, prefix, middle, suffix):
        """Test that sanitizing twice gives the same result"""
        task_id = prefix + middle + suffix
        
        result1 = sanitize_repo_name(task_id)
        result2 = sanitize_repo_name(result1)
        
        # Sanitizing an already sanitized name should not change it
        assert result1 == result2
    
    @given(task_id=st.text(alphabet='!@#$%^&*()', min_size=1, max_size=50))
    def test_sanitize_handles_only_special_chars(self, task_id):
        """Test handling of strings with only special characters"""
        result = sanitize_repo_name(task_id)
        
        # Should return a valid fallback name
        assert len(result) > 0
        assert re.match(r'^[a-zA-Z0-9_-]+$', result)


class TestGetMITLicenseHypothesis:
    """Property-based tests for get_mit_license function"""
    
    def test_license_is_consistent(self):
        """Test that license text is consistent across calls"""
        license1 = get_mit_license()
        license2 = get_mit_license()
        
        assert license1 == license2
    
    def test_license_contains_required_text(self):
        """Test that license contains required MIT license text"""
        license_text = get_mit_license()
        
        # MIT License must contain these key phrases
        assert "MIT License" in license_text or "MIT" in license_text
        assert "Permission is hereby granted" in license_text
        assert "free of charge" in license_text
        assert "THE SOFTWARE IS PROVIDED" in license_text
        assert "AS IS" in license_text
        assert "WITHOUT WARRANTY OF ANY KIND" in license_text
    
    def test_license_is_string(self):
        """Test that license is returned as a string"""
        license_text = get_mit_license()
        
        assert isinstance(license_text, str)
        assert len(license_text) > 100  # MIT license should be substantial
    
    def test_license_has_proper_structure(self):
        """Test that license has proper line breaks and structure"""
        license_text = get_mit_license()
        
        # Should have multiple lines
        lines = license_text.split('\n')
        assert len(lines) > 5
        
        # Should not have excessive blank lines
        blank_lines = [line for line in lines if line.strip() == '']
        assert len(blank_lines) < len(lines) / 2


class TestDataURIHandling:
    """Property-based tests for data URI patterns"""
    
    @given(
        mime_type=st.sampled_from(['image/png', 'image/jpeg', 'image/gif', 'text/plain', 'application/json']),
        data=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='+/='),
            min_size=10,
            max_size=1000
        )
    )
    def test_data_uri_pattern_recognition(self, mime_type, data):
        """Test that we can recognize valid data URI patterns"""
        data_uri = f"data:{mime_type};base64,{data}"
        
        # Pattern that should match data URIs
        pattern = r'^data:([a-zA-Z0-9]+/[a-zA-Z0-9+.-]+);base64,(.+)$'
        match = re.match(pattern, data_uri)
        
        assert match is not None
        assert match.group(1) == mime_type
        assert match.group(2) == data
    
    @given(
        mime_type=st.sampled_from(['image/png', 'image/jpeg']),
        data_length=st.integers(min_value=100, max_value=10000)
    )
    def test_data_uri_size_estimation(self, mime_type, data_length):
        """Test that data URI size can be estimated"""
        # Base64 encoding increases size by ~33%
        # data URI format: "data:mime/type;base64,ENCODED_DATA"
        
        prefix_length = len(f"data:{mime_type};base64,")
        total_length = prefix_length + data_length
        
        # Verify our size calculation is reasonable
        assert total_length > data_length
        assert total_length < data_length * 2  # Should not double the size


class TestRepoNameEdgeCases:
    """Test edge cases for repository naming"""
    
    @example(task_id="")
    @example(task_id="   ")
    @example(task_id="---")
    @example(task_id="___")
    @example(task_id="a")
    @example(task_id="A" * 200)
    @given(task_id=st.text(max_size=300))
    def test_sanitize_edge_cases(self, task_id):
        """Test edge cases that might break sanitization"""
        try:
            result = sanitize_repo_name(task_id)
            
            # If it succeeds, result must be valid
            assert isinstance(result, str)
            if len(result) > 0:
                assert len(result) <= 100
                assert re.match(r'^[a-zA-Z0-9_-]+$', result)
                assert not result.startswith('-')
                assert not result.endswith('-')
        except Exception as e:
            # If it fails, it should be a specific expected error
            pytest.fail(f"Unexpected error for input '{task_id}': {e}")


# Run with: pytest test/test_utils_hypothesis.py -v
# Run with statistics: pytest test/test_utils_hypothesis.py -v --hypothesis-show-statistics
# Run with more examples: pytest test/test_utils_hypothesis.py -v --hypothesis-examples=1000
