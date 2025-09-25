# Test Structure

This directory contains the test files for the Netflix Autovalidator.

## Test Files

### `test_functionality.py`
- Contains all test functions for the application
- Tests logging, email connection, Telegram connection, etc.
- Can be imported and used by other modules

### `run_tests.py`
- Standalone test runner
- Sets up test environment and runs all tests
- Used by main application for pre-startup testing
- Can be run independently: `python run_tests.py`

## Test Flow

1. **Pre-Startup**: `main.py` runs `run_tests.py` before starting the application
2. **Test Execution**: `run_tests.py` calls functions from `test_functionality.py`
3. **Result**: If tests fail, the application exits; if they pass, the application starts

## Running Tests

### Standalone
```bash
python run_tests.py
```

### As part of main application
```bash
python main.py  # Tests run automatically before startup
```

## Test Requirements

- Email credentials (EMAIL, PASSWORD, IMAP_SERVER, IMAP_PORT)
- Telegram credentials (optional - TELEGRAM_API_KEY, etc.)
- Environment file: `config.env` or `test.env`

## Test Results

- ✅ **Success**: All tests pass, application starts
- ❌ **Failure**: Tests fail, application exits with error code 1
