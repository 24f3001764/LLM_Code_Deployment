# Test Suite

This directory contains comprehensive unit tests for the LLM Code Deployment API using **pytest** and **Hypothesis**.

## Test Files

### Unit Tests (pytest)
- **test_models.py** - Tests for Pydantic models (TaskRequest, EvaluationPayload, APIResponse, Attachment)
- **test_utils.py** - Tests for utility functions (decode_and_save_attachments, sanitize_repo_name, get_mit_license)
- **test_config.py** - Tests for configuration validation
- **test_evaluator.py** - Tests for evaluation notifier with retry logic
- **test_main.py** - Tests for FastAPI endpoints and background task processing

### Property-Based Tests (Hypothesis)
- **test_models_hypothesis.py** - Property-based tests for models with random data generation
- **test_utils_hypothesis.py** - Property-based tests for utilities with edge case discovery

### Integration Tests
- **test_client.py** - Integration test client for manual testing

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements.txt
```

This will install pytest, pytest-asyncio, pytest-mock, and hypothesis along with other dependencies.

### Run Property-Based Tests (Hypothesis)

```bash
# Run all Hypothesis tests
pytest test/test_models_hypothesis.py test/test_utils_hypothesis.py

# Run with statistics
pytest test/test_models_hypothesis.py --hypothesis-show-statistics

# Run more examples (default is 100)
pytest test/test_models_hypothesis.py --hypothesis-examples=1000

# Run with specific seed for reproducibility
pytest test/test_models_hypothesis.py --hypothesis-seed=12345
```

### Run All Tests

```bash
# From project root
pytest

# Or use the batch file (Windows)
run_tests.bat
```

### Run Specific Test Files

```bash
# Test models only
pytest test/test_models.py

# Test utilities only
pytest test/test_utils.py

# Test configuration only
pytest test/test_config.py

# Test evaluator only
pytest test/test_evaluator.py

# Test main API only
pytest test/test_main.py
```

### Run Specific Test Classes or Functions

```bash
# Run a specific test class
pytest test/test_models.py::TestTaskRequest

# Run a specific test function
pytest test/test_models.py::TestTaskRequest::test_valid_task_request_round1
```

### Run with Coverage

```bash
# Install coverage
pip install pytest-cov

# Run tests with coverage report
pytest --cov=src --cov-report=html --cov-report=term

# View HTML report
# Open htmlcov/index.html in your browser
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Only Fast Tests (Skip Async)

```bash
pytest -m "not asyncio"
```

## Test Configuration

The test suite uses `pytest.ini` for configuration:
- Automatic test discovery for files matching `test_*.py`
- Async test support via `pytest-asyncio`
- Short traceback format for cleaner output
- Custom markers for test categorization

## Writing New Tests

When adding new tests:

1. **Follow naming conventions**: `test_*.py` for files, `Test*` for classes, `test_*` for functions
2. **Use fixtures**: Define reusable test data and mocks as pytest fixtures
3. **Mock external dependencies**: Use `unittest.mock` or `pytest-mock` for external APIs
4. **Test async functions**: Use `@pytest.mark.asyncio` decorator for async tests
5. **Keep tests isolated**: Each test should be independent and not rely on others

### Example Test Structure

```python
import pytest
from unittest.mock import AsyncMock, patch

class TestMyFeature:
    """Test MyFeature functionality"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample test data"""
        return {"key": "value"}
    
    def test_sync_function(self, sample_data):
        """Test synchronous function"""
        result = my_function(sample_data)
        assert result == expected_value
    
    @pytest.mark.asyncio
    async def test_async_function(self, sample_data):
        """Test asynchronous function"""
        with patch('module.external_call', new_callable=AsyncMock) as mock:
            mock.return_value = "mocked_value"
            result = await my_async_function(sample_data)
            assert result == expected_value
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines. Ensure:
- All environment variables are properly mocked
- External API calls are mocked
- Tests don't require actual GitHub or OpenAI credentials
- Tests complete within reasonable time limits

## Troubleshooting

### Import Errors

If you get import errors, ensure you're running pytest from the project root:
```bash
cd /path/to/LLM_Code_Deployment
pytest
```

### Async Test Warnings

If you see warnings about async tests, ensure `pytest-asyncio` is installed:
```bash
pip install pytest-asyncio
```

### Environment Variable Issues

Some tests mock environment variables. If tests fail due to config issues:
1. Check that `.env` file exists (copy from `.env.example`)
2. Ensure test mocks are properly applied
3. Run tests in isolation to identify the problematic test

## Test Coverage Goals

- **Models**: 100% coverage (all validation paths)
- **Utils**: 95%+ coverage (all utility functions)
- **Config**: 100% coverage (all validation scenarios)
- **Evaluator**: 90%+ coverage (all retry scenarios)
- **Main**: 85%+ coverage (core API endpoints and workflows)

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio documentation](https://pytest-asyncio.readthedocs.io/)
- [FastAPI testing guide](https://fastapi.tiangolo.com/tutorial/testing/)
