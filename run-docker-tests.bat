@echo off
REM Docker Compose Test Runner for Netflix Autovalidator (Windows)
REM This script runs comprehensive tests using Docker Compose

echo 🧪 Netflix Autovalidator Docker Test Suite
echo ==========================================

REM Check if test.env exists
if not exist "test.env" (
    echo [WARNING] test.env not found. Creating from example...
    if exist "test.env.example" (
        copy test.env.example test.env
        echo [WARNING] Please edit test.env with your test credentials before running tests
        pause
        exit /b 1
    ) else (
        echo [ERROR] test.env.example not found. Cannot create test.env
        pause
        exit /b 1
    )
)

REM Create test results directory
echo [INFO] Creating test results directory...
if not exist "test-results" mkdir test-results

echo [INFO] Starting Docker test suite...

REM Test 1: Functionality tests with pre-built image
echo [INFO] Test 1: Functionality tests (pre-built image)
docker-compose -f docker-compose.test.yml run --rm netflix-autovalidator-test
if %errorlevel% equ 0 (
    echo [SUCCESS] Functionality Test (pre-built) completed successfully
    set test1_result=PASS
) else (
    echo [ERROR] Functionality Test (pre-built) failed
    set test1_result=FAIL
)

REM Test 2: Functionality tests with local build
echo [INFO] Test 2: Functionality tests (local build)
docker-compose -f docker-compose.test.yml run --rm netflix-autovalidator-test-local
if %errorlevel% equ 0 (
    echo [SUCCESS] Functionality Test (local) completed successfully
    set test2_result=PASS
) else (
    echo [ERROR] Functionality Test (local) failed
    set test2_result=FAIL
)

REM Test 3: Integration test
echo [INFO] Test 3: Integration test (main application)
docker-compose -f docker-compose.test.yml run --rm netflix-autovalidator-integration-test
if %errorlevel% equ 0 (
    echo [SUCCESS] Integration Test completed successfully
    set test3_result=PASS
) else (
    echo [ERROR] Integration Test failed
    set test3_result=FAIL
)

REM Cleanup
echo [INFO] Cleaning up test containers...
docker-compose -f docker-compose.test.yml down --remove-orphans

REM Print test results summary
echo.
echo ==========================================
echo 🧪 Test Results Summary
echo ==========================================
echo Functionality Test (pre-built): %test1_result%
echo Functionality Test (local):     %test2_result%
echo Integration Test:               %test3_result%

REM Check if all tests passed
if "%test1_result%"=="PASS" if "%test2_result%"=="PASS" if "%test3_result%"=="PASS" (
    echo [SUCCESS] All tests passed! 🎉
    exit /b 0
) else (
    echo [ERROR] Some tests failed. Check the logs above for details.
    pause
    exit /b 1
)
