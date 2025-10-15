# Testing Guide

This project uses **pytest** and **Hypothesis** for comprehensive testing.

## 📚 Test Types

### 1. **Unit Tests** (pytest)
Traditional example-based tests that verify specific behaviors.

**Files:**
- `test_models.py` - Pydantic model validation
- `test_utils.py` - Utility function tests
- `test_config.py` - Configuration validation
- `test_evaluator.py` - Evaluation notifier tests
- `test_main.py` - FastAPI endpoint tests

### 2. **Property-Based Tests** (Hypothesis)
Generates random test data to find edge cases automatically.

**Files:**
- `test_models_hypothesis.py` - Property-based tests for models
- `test_utils_hypothesis.py` - Property-based tests for utilities

### 3. **Integration Tests**
End-to-end tests with the test client.

**Files:**
- `test_client.py` - Manual integration testing

## 🚀 Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest test/test_models.py
pytest test/test_models_hypothesis.py
```

### Run Tests by Marker
```bash
# Run only property-based tests
pytest -m hypothesis

# Run only async tests
pytest -m asyncio

# Skip slow tests
pytest -m "not slow"
```

### Run with Coverage
```bash
pytest --cov=src --cov-report=html
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Specific Test Class or Function
```bash
pytest test/test_models.py::TestTaskRequest
pytest test/test_models.py::TestTaskRequest::test_valid_task_request_round1
```

## 🎲 Hypothesis-Specific Commands

### Show Statistics
```bash
pytest test/test_models_hypothesis.py --hypothesis-show-statistics
```

### Run More Examples (default is 100)
```bash
pytest test/test_models_hypothesis.py --hypothesis-examples=1000
```

### Use Specific Seed (for reproducibility)
```bash
pytest test/test_models_hypothesis.py --hypothesis-seed=12345
```

### Run in Verbose Mode
```bash
pytest test/test_models_hypothesis.py --hypothesis-verbosity=verbose
```

## 📊 Understanding Hypothesis Output

When you run Hypothesis tests, you'll see output like:

```
test_models_hypothesis.py::TestTaskRequestHypothesis::test_task_request_with_random_valid_data 
  - 100 passed in 0.5s
  
Hypothesis Statistics:
  - test_task_request_with_random_valid_data:
    - Typical runtimes: 0-1ms
    - Tried 100 examples
    - Passed 100 examples
```

### What Hypothesis Does:
1. **Generates random test data** based on strategies
2. **Runs your test** with each generated example
3. **Shrinks failing examples** to find the minimal failing case
4. **Reports statistics** about test execution

## 🔍 Test Coverage

### Check Coverage
```bash
pytest --cov=src --cov-report=term-missing
```

### Generate HTML Coverage Report
```bash
pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

## 🐛 Debugging Tests

### Run with Print Statements
```bash
pytest -s
```

### Run with Debugger
```bash
pytest --pdb
```

### Run Last Failed Tests Only
```bash
pytest --lf
```

### Run Failed Tests First
```bash
pytest --ff
```

## 📝 Writing New Tests

### Example: Standard pytest Test
```python
import pytest
from src.models import TaskRequest

def test_task_request_creation():
    """Test creating a task request"""
    request = TaskRequest(
        email="test@example.com",
        secret="secret",
        task="task-001",
        round=1,
        nonce="nonce",
        brief="Test brief",
        checks=["Check 1"],
        evaluation_url="https://example.com"
    )
    assert request.email == "test@example.com"
```

### Example: Hypothesis Property-Based Test
```python
from hypothesis import given, strategies as st
from src.models import TaskRequest

@given(
    email=st.emails(),
    round=st.integers(min_value=1, max_value=2)
)
def test_task_request_with_random_data(email, round):
    """Test with randomly generated data"""
    request = TaskRequest(
        email=email,
        secret="secret",
        task="task-001",
        round=round,
        nonce="nonce",
        brief="Test brief",
        checks=["Check 1"],
        evaluation_url="https://example.com"
    )
    assert request.round in [1, 2]
    assert "@" in request.email
```

## 🎯 Test Strategies

### Common Hypothesis Strategies

```python
from hypothesis import strategies as st

# Basic types
st.text()                    # Random strings
st.integers()                # Random integers
st.floats()                  # Random floats
st.booleans()                # True or False

# Constrained types
st.text(min_size=1, max_size=100)
st.integers(min_value=1, max_value=10)
st.emails()                  # Valid email addresses

# Collections
st.lists(st.text())          # Lists of strings
st.dictionaries(keys=st.text(), values=st.integers())

# Custom strategies
@st.composite
def valid_task_id(draw):
    return draw(st.text(
        alphabet=st.characters(whitelist_categories=('Ll', 'Nd')),
        min_size=1,
        max_size=50
    ))
```

## 🔧 Continuous Integration

### GitHub Actions Example
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 📈 Best Practices

### 1. **Test Naming**
- Use descriptive names: `test_task_request_rejects_invalid_rounds`
- Follow pattern: `test_<what>_<condition>_<expected>`

### 2. **Test Organization**
- Group related tests in classes
- One test file per module
- Keep tests focused and independent

### 3. **Assertions**
- Use specific assertions: `assert x == 5` not `assert x`
- Add helpful messages: `assert x > 0, f"Expected positive, got {x}"`

### 4. **Fixtures**
```python
@pytest.fixture
def sample_request():
    return TaskRequest(
        email="test@example.com",
        secret="secret",
        task="task-001",
        round=1,
        nonce="nonce",
        brief="Test",
        checks=["Check"],
        evaluation_url="https://example.com"
    )

def test_with_fixture(sample_request):
    assert sample_request.round == 1
```

### 5. **Parametrize Tests**
```python
@pytest.mark.parametrize("round,expected", [
    (1, True),
    (2, True),
    (3, False),
])
def test_valid_rounds(round, expected):
    # Test logic here
    pass
```

## 🚨 Common Issues

### Issue: "No module named 'src'"
**Solution:** Make sure you're running pytest from the project root

### Issue: Hypothesis tests are slow
**Solution:** Reduce examples: `pytest --hypothesis-examples=10`

### Issue: Tests fail randomly
**Solution:** Use seed for reproducibility: `pytest --hypothesis-seed=12345`

### Issue: Import errors in tests
**Solution:** Check that `__init__.py` exists in test directory

## 📚 Resources

- [pytest documentation](https://docs.pytest.org/)
- [Hypothesis documentation](https://hypothesis.readthedocs.io/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)

## 🎓 Quick Reference

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific file
pytest test/test_models.py

# Run with Hypothesis statistics
pytest --hypothesis-show-statistics

# Run more examples
pytest --hypothesis-examples=1000

# Debug mode
pytest -s --pdb

# Verbose output
pytest -v

# Run last failed
pytest --lf

# Run specific marker
pytest -m hypothesis
```

---

**Happy Testing! 🧪**
