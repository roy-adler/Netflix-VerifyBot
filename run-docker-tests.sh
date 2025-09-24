#!/bin/bash

# Docker Compose Test Runner for Netflix Autovalidator
# This script runs comprehensive tests using Docker Compose

set -e  # Exit on any error

echo "🧪 Netflix Autovalidator Docker Test Suite"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if test.env exists
if [ ! -f "test.env" ]; then
    print_warning "test.env not found. Creating from example..."
    if [ -f "test.env.example" ]; then
        cp test.env.example test.env
        print_warning "Please edit test.env with your test credentials before running tests"
        exit 1
    else
        print_error "test.env.example not found. Cannot create test.env"
        exit 1
    fi
fi

# Create test results directory
print_status "Creating test results directory..."
mkdir -p test-results

# Function to run a specific test
run_test() {
    local test_name=$1
    local service_name=$2
    local description=$3
    
    print_status "Running $test_name: $description"
    
    if docker-compose -f docker-compose.test.yml run --rm $service_name; then
        print_success "$test_name completed successfully"
        return 0
    else
        print_error "$test_name failed"
        return 1
    fi
}

# Function to clean up containers
cleanup() {
    print_status "Cleaning up test containers..."
    docker-compose -f docker-compose.test.yml down --remove-orphans 2>/dev/null || true
}

# Set trap to cleanup on exit
trap cleanup EXIT

# Main test execution
print_status "Starting Docker test suite..."

# Test 1: Functionality tests with pre-built image
print_status "Test 1: Functionality tests (pre-built image)"
if run_test "Functionality Test" "netflix-autovalidator-test" "Tests all core functionality with pre-built image"; then
    test1_result="PASS"
else
    test1_result="FAIL"
fi

# Test 2: Functionality tests with local build
print_status "Test 2: Functionality tests (local build)"
if run_test "Local Build Test" "netflix-autovalidator-test-local" "Tests all core functionality with local build"; then
    test2_result="PASS"
else
    test2_result="FAIL"
fi

# Test 3: Integration test (runs main application briefly)
print_status "Test 3: Integration test (main application)"
if run_test "Integration Test" "netflix-autovalidator-integration-test" "Tests main application startup and initialization"; then
    test3_result="PASS"
else
    test3_result="FAIL"
fi

# Cleanup
cleanup

# Print test results summary
echo ""
echo "=========================================="
echo "🧪 Test Results Summary"
echo "=========================================="
echo -e "Functionality Test (pre-built): ${test1_result:+$GREEN}PASS${NC:-$RED}FAIL${NC}"
echo -e "Functionality Test (local):     ${test2_result:+$GREEN}PASS${NC:-$RED}FAIL${NC}"
echo -e "Integration Test:               ${test3_result:+$GREEN}PASS${NC:-$RED}FAIL${NC}"

# Check if all tests passed
if [ "$test1_result" = "PASS" ] && [ "$test2_result" = "PASS" ] && [ "$test3_result" = "PASS" ]; then
    print_success "All tests passed! 🎉"
    exit 0
else
    print_error "Some tests failed. Check the logs above for details."
    exit 1
fi
