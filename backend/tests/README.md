# RegGuard Backend Test Suite

Comprehensive pytest test suite for RegGuard backend covering research, payments, error handling, performance, and data accuracy.

## Overview

This test suite contains **105 tests** across 6 test modules, providing comprehensive coverage of:

- **Core Research** (16 tests): ZIP lookups, cost estimates, timelines, error handling
- **Payment Flow** (21 tests): Stripe integration, webhooks, email notifications, failure handling
- **Error Handling** (25 tests): Database timeouts, missing env vars, invalid JSON, API errors
- **Performance** (11 tests): Response times, concurrent requests, throughput
- **Data Persistence** (14 tests): Database operations, transaction safety, concurrent writes
- **Data Accuracy** (18 tests): Texas/California regulations, CAISO data, cost realism

## Quick Start

### Installation

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Or install directly
pip install pytest pytest-cov pytest-mock pytest-asyncio
```

### Running Tests

```bash
# Run all tests
./test_runner.sh

# Or use pytest directly
pytest tests/ -v

# Run specific test file
pytest tests/test_core_research.py -v

# Run specific test class
pytest tests/test_payment_flow.py::TestStripeWebhook -v

# Run specific test
pytest tests/test_payment_flow.py::TestStripeWebhook::test_webhook_signature_verification_valid -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run only fast tests (skip slow marker)
pytest tests/ -m "not slow"
```

## Test Organization

### conftest.py
Shared pytest fixtures and configuration:
- Mock services (Stripe, Firecrawl, Email, Anthropic, Database)
- Test data fixtures (Texas/California ZIP codes, sample payloads)
- Environment setup
- Custom pytest markers

### test_core_research.py
Research and lookup functionality:
- `TestZIPLookup`: Valid/invalid ZIP codes, jurisdiction resolution
- `TestCostEstimates`: Cost estimate generation and accuracy
- `TestTimelines`: Timeline generation and realism
- `TestErrorHandling`: Error scenarios in research

**Tests:** 16

### test_payment_flow.py
Payment processing and Stripe integration:
- `TestPaymentSubmission`: Checkout session creation, tier validation
- `TestStripeWebhook`: Webhook signature verification, event processing
- `TestResearchTrigger`: Payment-triggered research
- `TestEmailNotification`: Confirmation and memo emails
- `TestPaymentFailureHandling`: Declined cards, timeouts, refunds

**Tests:** 21

### test_error_handling.py
Comprehensive error scenario testing:
- `TestDatabaseTimeout`: Connection and query timeouts
- `TestMissingEnvironmentVariables`: Missing API keys, invalid URLs
- `TestInvalidJSON`: Malformed payloads, missing fields, null values
- `TestEmptyFirecrawlResponse`: Empty results, errors, timeouts
- `TestAPIResponseErrors`: 500/429/401/404 errors, network issues

**Tests:** 25

### test_performance.py
Performance requirements validation:
- `TestResponseTime`: Response time SLAs (<2 seconds)
- `TestConcurrentRequests`: Concurrent request handling
- `TestThroughput`: Requests per second capacity
- Response time consistency under load

**Tests:** 11

### test_data_persistence.py
Data integrity and safety:
- `TestDataSavedToDatabase`: Research, payments, trials, emails saved
- `TestNoDataLoss`: Crash recovery, error handling, duplicates
- `TestConcurrentWriteSafety`: Concurrent operations, transaction isolation

**Tests:** 14

### test_data_accuracy.py
Domain-specific accuracy validation:
- `TestTexasSolarAccuracy`: NEC codes, timelines, fees, inspections
- `TestCaliforniaCAISO`: CAISO zone identification, solar potential, utilities
- `TestCostEstimateRealism`: Component itemization, jurisdiction variance, contingencies

**Tests:** 18

## Markers

Run tests by category:

```bash
# Research tests
pytest tests/ -m research

# Payment tests
pytest tests/ -m payment

# Database tests
pytest tests/ -m database

# Email tests
pytest tests/ -m email

# Performance tests (slow)
pytest tests/ -m "slow"

# Error handling tests
pytest tests/ -m error_handling

# Skip slow tests
pytest tests/ -m "not slow"
```

## Test Fixtures

Available fixtures in conftest.py:

### Mocks
- `mock_stripe`: Stripe API client
- `mock_firecrawl`: Firecrawl API client
- `mock_email_service`: Email sending service
- `mock_anthropic`: Claude AI client
- `mock_database`: Database connection
- `mock_google_geocoding`: Geocoding API

### Test Data
- `texas_zip_data`: Sample Texas ZIP codes
- `california_zip_data`: Sample California ZIP codes with CAISO data
- `sample_research_request`: Research request payload
- `sample_payment_request`: Payment request payload
- `sample_stripe_webhook_event`: Webhook event data
- `sample_research_memo`: Markdown memo template
- `sample_cost_estimate`: Cost estimate data
- `sample_payment_confirmation`: Payment confirmation data

### Utilities
- `mock_env_vars`: Backup/restore environment variables
- `generate_test_id`: Generate unique test IDs

## Running the Test Suite

### Using the Shell Script (Recommended)

```bash
cd backend/tests
./test_runner.sh
```

This generates:
- Formatted console output with pass/fail summary
- HTML coverage report (`coverage/html/index.html`)
- JUnit XML report (`coverage/junit.xml`)
- Test report text file (`TEST_REPORT.txt`)

### Using pytest Directly

```bash
# All tests with coverage
pytest tests/ -v --cov=.. --cov-report=html --cov-report=term-missing

# Fast tests only
pytest tests/ -v -m "not slow"

# Specific category
pytest tests/test_payment_flow.py -v

# Verbose with durations
pytest tests/ -v --durations=10

# Stop on first failure
pytest tests/ -x

# Run only tests with "research" in name
pytest tests/ -k "research" -v
```

## Coverage Reports

After running tests, view coverage:

```bash
# Text coverage in terminal (already shown in output)
pytest tests/ --cov=.. --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ --cov=.. --cov-report=html
open htmlcov/index.html

# Generate XML for CI/CD
pytest tests/ --cov=.. --cov-report=xml
```

## Launch Readiness Checklist

✓ **Before launching to production, verify:**

- [ ] All 105 tests pass: `./test_runner.sh`
- [ ] Coverage meets threshold: `>80%` for critical paths
- [ ] Performance tests pass: Response times `<2 seconds`
- [ ] Payment flow tests pass: Stripe integration verified
- [ ] Error handling tests pass: Graceful degradation confirmed
- [ ] Data persistence tests pass: No data loss scenarios
- [ ] Data accuracy tests pass: Domain regulations verified

### Running Pre-Launch Validation

```bash
# Run all tests and generate reports
cd backend/tests
./test_runner.sh

# Check coverage threshold
coverage report --fail-under=80

# Generate CI-friendly reports
pytest tests/ --junitxml=junit.xml --cov=.. --cov-report=xml
```

## Test Execution Times

Typical execution times:

| Command | Time |
|---------|------|
| All tests | ~30 seconds |
| Fast tests only (`-m "not slow"`) | ~5 seconds |
| Single test file | ~2-5 seconds |
| Single test | <100ms |

## Continuous Integration

For CI/CD pipelines, use:

```bash
# Run tests, generate reports, exit with proper code
pytest tests/ \
  --junitxml=test-results.xml \
  --cov=.. \
  --cov-report=xml \
  --cov-report=term-missing \
  -v

# Only run fast tests to speed up CI
pytest tests/ -m "not slow" -v
```

## Troubleshooting

### Import Errors
If you get import errors like `No module named 'stripe'`:
```bash
pip install -r requirements-test.txt
```

### Fixture Not Found
Ensure you're running from the backend directory:
```bash
cd backend
pytest tests/ -v
```

### Tests Skip with "Async"
Install pytest-asyncio:
```bash
pip install pytest-asyncio
```

### Coverage Not Showing
Ensure pytest-cov is installed:
```bash
pip install pytest-cov
```

## Test Philosophy

These tests follow best practices:

1. **Independence**: Each test is isolated and can run in any order
2. **Clarity**: Test names clearly describe what they verify
3. **Realism**: Mock data and scenarios reflect production usage
4. **Performance**: Tests are fast (< 30 seconds total)
5. **Coverage**: Both happy paths and error cases tested
6. **Documentation**: Each test includes docstring explaining purpose

## Adding New Tests

When adding new tests:

1. Add to appropriate test file (or create new one)
2. Use descriptive test name: `test_<feature>_<scenario>`
3. Include docstring explaining test purpose
4. Add appropriate pytest marker (`@pytest.mark.<category>`)
5. Use fixtures from conftest.py when possible
6. Keep tests independent (no dependencies between tests)
7. Verify test runs: `pytest tests/test_newfile.py -v`

Example:

```python
@pytest.mark.research
async def test_new_feature_success(self, mock_firecrawl):
    """Test new feature handles successful response."""
    mock_firecrawl.new_method.return_value = {"status": "success"}
    
    result = await mock_firecrawl.new_method()
    
    assert result["status"] == "success"
```

## Test Statistics

- **Total Tests**: 105
- **Test Files**: 6
- **Fixture Types**: 15+
- **Mock Services**: 6
- **Test Markers**: 6
- **Expected Coverage**: 80%+
- **Execution Time**: ~30 seconds

## Documentation

For more information:
- See individual test file docstrings
- Review conftest.py for fixture details
- Check pytest documentation: https://docs.pytest.org/
