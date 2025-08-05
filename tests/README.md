# 🧪 Test Suite for Random Text API

This directory contains comprehensive tests for the Random Text API functionality.

## 📁 Test Files

### `test_random_text_api.py`
Comprehensive test suite with mocked services and integration tests:
- **Unit Tests**: Test individual API endpoints with mocked services
- **Integration Tests**: Test with live API (requires running server)
- **Error Handling**: Test various error scenarios
- **Parameter Validation**: Test input validation and constraints

### `run_random_text_tests.py`
Simple test runner script for quick API validation:
- Easy-to-use test runner
- Clear output with emojis and status
- Tests all major endpoints
- Good for development and debugging

## 🚀 Running Tests

### Prerequisites
1. Install test dependencies:
```bash
pip install pytest pytest-asyncio httpx
```

2. Start the API server:
```bash
python main.py
```

### Running the Simple Test Runner
```bash
python tests/run_random_text_tests.py
```

### Running Comprehensive Tests
```bash
# Run all tests
pytest tests/test_random_text_api.py -v

# Run only unit tests (no server required)
pytest tests/test_random_text_api.py::TestRandomTextAPI -v

# Run only integration tests (requires server)
pytest tests/test_random_text_api.py::TestRandomTextAPIIntegration -v

# Run with coverage
pytest tests/test_random_text_api.py --cov=app --cov-report=html
```

## 🧪 Test Coverage

### Unit Tests (Mocked)
- ✅ Health check endpoint
- ✅ Dataset info endpoint
- ✅ Random text retrieval
- ✅ Multiple random texts
- ✅ Parameter validation
- ✅ Error handling scenarios
- ✅ Service availability checks

### Integration Tests (Live API)
- ✅ Health check with live server
- ✅ Dataset info with live server
- ✅ Random text with live server
- ✅ Multiple texts with live server

## 📊 Test Scenarios

### Success Scenarios
1. **Basic Random Text**: Get a single random text
2. **Constrained Random Text**: Get text with length constraints
3. **Multiple Random Texts**: Get 1-10 random texts
4. **Dataset Info**: Get dataset statistics
5. **Health Check**: Check service status

### Error Scenarios
1. **Service Unavailable**: When RACE dataset is not loaded
2. **No Suitable Text**: When no text matches constraints
3. **Invalid Parameters**: Test parameter validation
4. **Network Errors**: Handle connection issues

### Parameter Validation
1. **Length Constraints**: min_length and max_length validation
2. **Count Limits**: Ensure count is between 1-10
3. **Parameter Swapping**: Handle min_length > max_length
4. **Boundary Values**: Test edge cases

## 🔧 Test Configuration

### Environment Variables
- `BASE_URL`: API base URL (default: http://localhost:8000)
- `RANDOM_TEXT_BASE`: Random text API base path

### Test Data
- Sample random text responses
- Mock RACE dataset service
- Test fixtures for consistent testing

## 📈 Test Results

### Expected Output (Simple Runner)
```
🚀 Starting Random Text API Tests...
==================================================

📋 Running: Health Check
🔍 Testing health check...
✅ Health check passed: {'service': 'random-text', 'status': 'healthy', ...}

📋 Running: Dataset Info
🔍 Testing dataset info...
✅ Dataset info: {'is_loaded': True, 'total_articles': 27827, ...}

...

==================================================
📊 Test Results Summary:
==================================================
✅ PASS: Health Check
✅ PASS: Dataset Info
✅ PASS: Random Text
✅ PASS: Random Text with Constraints
✅ PASS: Multiple Random Texts
✅ PASS: Error Handling

🎯 Overall: 6/6 tests passed
🎉 All tests passed! Random Text API is working correctly.
```

## 🐛 Troubleshooting

### Common Issues

1. **Server Not Running**
   ```
   ❌ Health check error: [Errno 111] Connection refused
   ```
   **Solution**: Start the API server with `python main.py`

2. **Dataset Not Loaded**
   ```
   ❌ Random text failed: 503
   ```
   **Solution**: Wait for the RACE dataset to load on startup

3. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'app'
   ```
   **Solution**: Run tests from project root directory

4. **Network Timeout**
   ```
   ❌ Random text error: ConnectTimeout
   ```
   **Solution**: Check server is running and accessible

### Debug Mode
Run tests with verbose output:
```bash
pytest tests/test_random_text_api.py -v -s
```

## 📝 Adding New Tests

### Unit Test Template
```python
async def test_new_feature(self, client, mock_race_service):
    """Test new feature"""
    # Setup
    mock_race_service.some_method.return_value = expected_value
    
    # Execute
    response = await client.get(f"{RANDOM_TEXT_BASE}/new-endpoint")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert 'expected_field' in data
```

### Integration Test Template
```python
@pytest.mark.integration
async def test_live_new_feature(self, client):
    """Test new feature with live API"""
    try:
        response = await client.get(f"{RANDOM_TEXT_BASE}/new-endpoint")
        assert response.status_code == 200
        # Add more assertions
    except httpx.ConnectError:
        pytest.skip("API server not running")
```

## 🎯 Best Practices

1. **Mock External Dependencies**: Use mocks for RACE dataset service
2. **Test Error Scenarios**: Always test failure cases
3. **Validate Responses**: Check response structure and content
4. **Use Async/Await**: All API calls are async
5. **Handle Network Errors**: Gracefully handle connection issues
6. **Clear Test Names**: Use descriptive test method names
7. **Isolated Tests**: Each test should be independent

## 📚 Related Documentation

- [API Documentation](../API_DOCUMENTATION.md)
- [Main Application](../main.py)
- [Random Text Service](../app/services/race_dataset_service.py)
- [Random Text API](../app/api/random_text.py) 