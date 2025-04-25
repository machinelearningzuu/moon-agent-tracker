Microservices API Test Suite

This test suite provides comprehensive testing for the microservices architecture, including individual service testing and integration testing.

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Ensure all microservices are running either locally or in your EKS cluster.

## Running Tests

You can run tests using the `run_tests.py` script with various options:

### Basic Usage

```bash
# Run all tests against local environment
python run_tests.py

# Run all tests against EKS environment
python run_tests.py --env eks

# Run specific service tests
python run_tests.py --service agent
python run_tests.py --service sales
python run_tests.py --service notification
python run_tests.py --service integration

# Generate HTML report
python run_tests.py --html

# Show verbose output
python run_tests.py -v
```

### Options

- `--env`: Specify the environment to test against (`local` or `eks`)
- `--service`: Specify which service to test (`agent`, `sales`, `notification`, `integration`, or `all`)
- `--html`: Generate an HTML report
- `--verbose`, `-v`: Show verbose output

## Test Structure

The test suite includes:

- `test_agent_service.py`: Tests for the Agent Service API
- `test_sales_service.py`: Tests for the Sales Service API
- `test_notification_service.py`: Tests for the Notification Service API
- `test_integration.py`: Integration tests for the microservices

## Reports

When using the `--html` flag, test reports are generated in the `reports/{env}/{timestamp}/report.html` directory.

## Configuration

- Default service URLs are configured in `conftest.py`
- Test data fixtures are defined in `conftest.py`

## Continuous Integration

These tests can be integrated into a CI/CD pipeline by running:

```bash
python run_tests.py --env eks --html
```
