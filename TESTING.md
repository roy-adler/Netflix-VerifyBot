# Testing Guide for Netflix Autovalidator

This document explains how to run comprehensive tests for the Netflix Autovalidator application using Docker Compose.

## Test Types

### 1. Functionality Tests
- **Purpose**: Tests all core functionality without running the main application
- **What it tests**:
  - Logging functionality (file and console)
  - Email IMAP connection
  - Telegram API connection
  - Email logging functions
  - Configuration validation

### 2. Integration Tests
- **Purpose**: Tests the main application startup and initialization
- **What it tests**:
  - Application startup process
  - Configuration loading
  - Service initialization
  - Error handling during startup

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Test credentials configured

### 1. Setup Test Environment

```bash
# Copy the example test configuration
cp test.env.example test.env

# Edit test.env with your test credentials
nano test.env
```

### 2. Run All Tests

**Linux/macOS:**
```bash
chmod +x run-docker-tests.sh
./run-docker-tests.sh
```

**Windows:**
```cmd
run-docker-tests.bat
```

**Manual Docker Compose:**
```bash
# Run functionality tests
docker-compose -f docker-compose.test.yml run --rm netflix-autovalidator-test

# Run integration tests
docker-compose -f docker-compose.test.yml run --rm netflix-autovalidator-integration-test
```

## Test Configuration

### Required Environment Variables

```bash
# Email Configuration (Required)
EMAIL=your-email@example.com
PASSWORD=your-email-password
IMAP_SERVER=imap.example.com
IMAP_PORT=993

# Logging Configuration
LOG_PATH=test-results.log

# Telegram Configuration (Optional)
TELEGRAM_API_KEY=your_telegram_api_key
TELEGRAM_API_URL=http://localhost:5000/api/broadcast-to-channel
TELEGRAM_CHANNEL_NAME=test_channel
TELEGRAM_CHANNEL_SECRET=your_channel_secret
```

## Test Services

### 1. `netflix-autovalidator-test`
- **Image**: Pre-built image from GitHub Container Registry
- **Purpose**: Functionality testing with production image
- **Command**: `python run_tests.py`

### 2. `netflix-autovalidator-test-local`
- **Image**: Built from local Dockerfile
- **Purpose**: Functionality testing with local build
- **Command**: `python run_tests.py`

### 3. `netflix-autovalidator-integration-test`
- **Image**: Pre-built image from GitHub Container Registry
- **Purpose**: Integration testing with main application
- **Command**: `timeout 30s python main.py`

## Test Results

### Output Files
- `test-results.log` - Detailed test logs
- `test-results/` - Directory containing test artifacts

### Expected Output
```
🧪 Netflix Autovalidator Docker Test Suite
==========================================
[INFO] Starting Docker test suite...
[INFO] Test 1: Functionality tests (pre-built image)
[SUCCESS] Functionality Test (pre-built) completed successfully
[INFO] Test 2: Functionality tests (local build)
[SUCCESS] Functionality Test (local) completed successfully
[INFO] Test 3: Integration test (main application)
[SUCCESS] Integration Test completed successfully
==========================================
🧪 Test Results Summary
==========================================
Functionality Test (pre-built): PASS
Functionality Test (local):     PASS
Integration Test:               PASS
[SUCCESS] All tests passed! 🎉
```

## Troubleshooting

### Common Issues

1. **Email Connection Failed**
   - Check email credentials in `test.env`
   - Verify IMAP server settings
   - Ensure email account allows IMAP access

2. **Telegram Connection Failed**
   - Check Telegram API credentials
   - Verify API URL is accessible
   - This is optional - tests will continue if Telegram fails

3. **Docker Build Failed**
   - Ensure Docker is running
   - Check Dockerfile syntax
   - Verify all dependencies are available

4. **Permission Denied (Linux/macOS)**
   - Make script executable: `chmod +x run-docker-tests.sh`

### Debug Mode

Run tests with verbose output:
```bash
docker-compose -f docker-compose.test.yml run --rm netflix-autovalidator-test --verbose
```

### View Test Logs

```bash
# View test results
cat test-results.log

# Follow logs in real-time
tail -f test-results.log
```

## CI/CD Integration

### GitHub Actions
The repository includes a GitHub Actions workflow (`.github/workflows/test.yml`) that runs:
- Functionality tests on Python
- Integration tests on Python
- Docker-based tests

### Custom CI/CD
You can integrate these tests into any CI/CD system by:
1. Using the Docker Compose files
2. Running the test scripts
3. Parsing the test results

## Test Customization

### Adding New Tests
1. Add test functions to `test_functionality.py`
2. Update `run_all_tests()` function
3. Add new test services to `docker-compose.test.yml`

### Modifying Test Environment
1. Update `test.env.example` with new variables
2. Modify Docker Compose environment sections
3. Update test scripts as needed

## Best Practices

1. **Always test with real credentials** - Use actual email and Telegram credentials for accurate testing
2. **Test both scenarios** - Test with and without optional services (Telegram)
3. **Clean up after tests** - The test scripts automatically clean up containers
4. **Monitor test results** - Check logs for any warnings or errors
5. **Update tests regularly** - Keep tests in sync with application changes

## Support

If you encounter issues with the testing setup:
1. Check the troubleshooting section above
2. Review the test logs for specific error messages
3. Ensure all prerequisites are installed
4. Verify your test configuration is correct
