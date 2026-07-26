"""
Pytest configuration and shared fixtures for RegGuard backend tests.
Provides mocking infrastructure for external services, database, and email.
"""

import pytest
import os
import json
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Ensure backend modules are importable
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


# ============================================================================
# SESSION-SCOPED FIXTURES (Setup/Teardown)
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Configure test environment variables for all tests."""
    os.environ["STRIPE_SECRET_KEY"] = "sk_test_51234567890abcdefghijklmnopqrstuvwxyz"
    os.environ["STRIPE_WEBHOOK_SECRET"] = "whsec_test_signature_secret_1234567890"
    os.environ["FIRECRAWL_API_KEY"] = "fc_test_key_12345"
    os.environ["RESEND_API_KEY"] = "re_test_key_12345"
    os.environ["RESEND_FROM_EMAIL"] = "test@regguard.com"
    os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test-key-12345"
    os.environ["GOOGLE_API_KEY"] = "AIzaSyTest1234567890abcdefghijklmnopqr"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["ENVIRONMENT"] = "test"
    yield
    # Cleanup after all tests
    for key in [
        "STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET", "FIRECRAWL_API_KEY",
        "RESEND_API_KEY", "RESEND_FROM_EMAIL", "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY", "DATABASE_URL", "ENVIRONMENT"
    ]:
        os.environ.pop(key, None)


# ============================================================================
# FUNCTION-SCOPED FIXTURES (Per-test isolation)
# ============================================================================

@pytest.fixture
def mock_stripe():
    """Mock Stripe API client."""
    with patch("stripe.Charge.create") as mock_create:
        with patch("stripe.Refund.create") as mock_refund:
            with patch("stripe.Customer.create") as mock_customer:
                mock_create.return_value = {
                    "id": "ch_test_charge_12345",
                    "amount": 1500000,
                    "currency": "usd",
                    "status": "succeeded",
                    "created": datetime.now().timestamp(),
                }
                mock_refund.return_value = {
                    "id": "re_test_refund_12345",
                    "charge": "ch_test_charge_12345",
                    "amount": 1500000,
                    "status": "succeeded",
                }
                mock_customer.return_value = {
                    "id": "cus_test_customer_12345",
                    "email": "test@example.com",
                }
                yield {
                    "create": mock_create,
                    "refund": mock_refund,
                    "customer": mock_customer,
                }


@pytest.fixture
def mock_firecrawl():
    """Mock Firecrawl API client."""
    mock_fc = AsyncMock()
    mock_fc.search = AsyncMock(return_value={
        "success": True,
        "data": [
            {
                "url": "https://example.com/permit",
                "title": "Building Permit Application",
                "markdown": "# Building Permit\n\nRequirements:\n- Foundation plan\n- Electrical plan",
            },
            {
                "url": "https://example.com/timeline",
                "title": "Typical Timeline",
                "markdown": "# Timeline\n\n- Intake: 3 days\n- Review: 7 days\n- Approval: 2 days",
            },
        ]
    })
    mock_fc.scrape_url = AsyncMock(return_value={
        "success": True,
        "data": {
            "markdown": "# Full Page Content\n\nDetailed regulations and procedures...",
            "metadata": {"title": "Page Title"}
        }
    })
    return mock_fc


@pytest.fixture
def mock_email_service():
    """Mock email service."""
    mock_email = AsyncMock()
    mock_email.send_research_memo = AsyncMock(return_value=True)
    mock_email.send_payment_confirmation = AsyncMock(return_value=True)
    mock_email.send_error_notification = AsyncMock(return_value=True)
    return mock_email


@pytest.fixture
def mock_anthropic():
    """Mock Anthropic Claude client."""
    mock_client = MagicMock()
    mock_message = MagicMock()
    mock_message.content = [
        MagicMock(text="""
# RegGuard Action Plan

## Key Requirements
- Obtain building permit
- Complete electrical inspection
- Submit utility interconnection

## Estimated Timeline
- Permit approval: 7-10 days
- Construction: 3-4 weeks

## Cost Estimate
- Permit fees: $1,200
- Electrical: $8,000
""")
    ]
    mock_client.messages.create.return_value = mock_message
    return mock_client


@pytest.fixture
def mock_database():
    """Mock database connection and operations."""
    mock_db = AsyncMock()
    mock_db.connect = AsyncMock()
    mock_db.disconnect = AsyncMock()
    mock_db.execute = AsyncMock()
    mock_db.fetch_one = AsyncMock(return_value={
        "id": "test_id_12345",
        "zip_code": "78704",
        "jurisdiction": "Austin, TX",
        "created_at": datetime.now().isoformat(),
    })
    mock_db.fetch_all = AsyncMock(return_value=[
        {
            "id": "test_id_12345",
            "zip_code": "78704",
            "jurisdiction": "Austin, TX",
        },
        {
            "id": "test_id_12346",
            "zip_code": "75202",
            "jurisdiction": "Dallas, TX",
        }
    ])
    return mock_db


@pytest.fixture
def mock_google_geocoding():
    """Mock Google Geocoding API."""
    mock_geo = AsyncMock()
    mock_geo.reverse_geocode = AsyncMock(return_value={
        "address": "123 Main St, Austin, TX 78704",
        "zip_code": "78704",
        "latitude": 30.2672,
        "longitude": -97.7431,
        "city": "Austin",
        "state": "TX",
    })
    mock_geo.geocode_address = AsyncMock(return_value={
        "address": "123 Main St, Austin, TX 78704",
        "latitude": 30.2672,
        "longitude": -97.7431,
        "zip_code": "78704",
    })
    return mock_geo


# ============================================================================
# REALISTIC TEST DATA FIXTURES
# ============================================================================

@pytest.fixture
def texas_zip_data():
    """Sample Texas ZIP code data."""
    return {
        "78704": {
            "zip_code": "78704",
            # Austin, TX (South Austin)
            "city": "Austin",
            "state": "TX",
            "county": "Travis",
            "latitude": 30.2672,
            "longitude": -97.7431,
            "jurisdiction": "City of Austin",
        },
        "75202": {
            "zip_code": "75202",
            # Dallas, TX (Downtown)
            "city": "Dallas",
            "state": "TX",
            "county": "Dallas",
            "latitude": 32.7767,
            "longitude": -96.7970,
            "jurisdiction": "City of Dallas",
        },
        "77002": {
            "zip_code": "77002",
            # Houston, TX (Downtown)
            "city": "Houston",
            "state": "TX",
            "county": "Harris",
            "latitude": 29.7604,
            "longitude": -95.3698,
            "jurisdiction": "City of Houston",
        },
        "75204": {
            "zip_code": "75204",
            # Dallas, TX (East Dallas)
            "city": "Dallas",
            "state": "TX",
            "county": "Dallas",
            "latitude": 32.7967,
            "longitude": -96.7767,
            "jurisdiction": "City of Dallas",
        },
    }


@pytest.fixture
def california_zip_data():
    """Sample California ZIP code data with solar/CAISO data."""
    return {
        "94105": {
            "zip_code": "94105",
            # San Francisco Bay Area
            "city": "Palo Alto",
            "state": "CA",
            "county": "Santa Clara",
            "latitude": 37.4419,
            "longitude": -122.1430,
            "jurisdiction": "City of Palo Alto",
            "caiso_zone": "PGE_Locational",
            "solar_potential_kwh_m2": 1850,
        },
        "90001": {
            "zip_code": "90001",
            # Los Angeles
            "city": "Los Angeles",
            "state": "CA",
            "county": "Los Angeles",
            "latitude": 33.9731,
            "longitude": -118.2479,
            "jurisdiction": "City of Los Angeles",
            "caiso_zone": "LADWP",
            "solar_potential_kwh_m2": 1950,
        },
        "92121": {
            "zip_code": "92121",
            # San Diego
            "city": "San Diego",
            "state": "CA",
            "county": "San Diego",
            "latitude": 32.9155,
            "longitude": -117.2023,
            "jurisdiction": "City of San Diego",
            "caiso_zone": "SDG&E",
            "solar_potential_kwh_m2": 2100,
        },
    }


@pytest.fixture
def sample_research_request():
    """Sample research request payload."""
    return {
        "site_address": "123 Main St, Austin, TX 78704",
        "zip_code": "78704",
        "project_type": "Commercial Solar",
        "jurisdiction": "Austin, TX",
        "latitude": 30.2672,
        "longitude": -97.7431,
    }


@pytest.fixture
def sample_payment_request():
    """Sample payment request payload."""
    return {
        "trial_id": "trial_test_12345",
        "email": "contractor@example.com",
        "tier": "premium",
        "amount_cents": 1500000,
        "success_url": "https://regguard.com/success",
        "cancel_url": "https://regguard.com/cancel",
    }


@pytest.fixture
def sample_stripe_webhook_event():
    """Sample Stripe webhook event payload."""
    return {
        "id": "evt_test_event_12345",
        "type": "checkout.session.completed",
        "created": int(datetime.now().timestamp()),
        "data": {
            "object": {
                "id": "cs_test_session_12345",
                "client_secret": "cs_test_secret_12345",
                "customer_email": "contractor@example.com",
                "payment_status": "paid",
                "session_id": "cs_test_session_12345",
                "metadata": {
                    "trial_id": "trial_test_12345",
                    "tier": "premium",
                },
            }
        }
    }


@pytest.fixture
def sample_research_memo():
    """Sample research memo markdown."""
    return """
# RegGuard Research Memo: 123 Main St, Austin, TX 78704

## Project Summary
Commercial solar installation at 123 Main St, Austin, TX 78704

## Key Regulatory Requirements

### Permits Required
- [ ] Building Permit
- [ ] Electrical Permit
- [ ] Utility Interconnection Agreement

### Timeline
- Application intake: 3 business days
- Technical review: 5-7 business days
- Final approval: 2-3 business days
- **Total expected: 10-15 business days**

### Estimated Costs
- City permit fees: $1,200
- Plan review fees: $400
- Electrical inspection: $150
- **Total estimated fees: $1,750**

## Action Plan
1. Prepare complete permit application per City of Austin guidelines
2. Obtain signed property owner authorization
3. Submit to Development Services division
4. Monitor for RFI (Request for Information)
5. Schedule final inspection

### The Bottom Line
Work with the City of Austin Development Services to ensure all documentation is complete before submission. Plan for 2-3 weeks from intake to final approval.
"""


@pytest.fixture
def sample_cost_estimate():
    """Sample cost estimate data."""
    return {
        "site_address": "123 Main St, Austin, TX 78704",
        "zip_code": "78704",
        "jurisdiction": "Austin, TX",
        "estimates": {
            "permit_fees": 1200,
            "plan_review_fees": 400,
            "inspection_fees": 150,
            "utility_fees": 800,
            "contingency": 500,
        },
        "total_estimated_cost": 3050,
        "estimated_timeline_days": 15,
        "confidence_level": "high",
    }


@pytest.fixture
def sample_payment_confirmation():
    """Sample payment confirmation data."""
    return {
        "payment_id": "pay_test_12345",
        "trial_id": "trial_test_12345",
        "amount": 15000,
        "currency": "USD",
        "status": "completed",
        "timestamp": datetime.now().isoformat(),
        "email": "contractor@example.com",
        "tier": "premium",
    }


# ============================================================================
# UTILITY FIXTURES
# ============================================================================

@pytest.fixture
def mock_env_vars():
    """Backup and restore environment variables for tests."""
    original = os.environ.copy()
    yield original
    os.environ.clear()
    os.environ.update(original)


@pytest.fixture
def generate_test_id():
    """Generate unique test IDs for test data."""
    import uuid
    def _generate(prefix: str = "test"):
        return f"{prefix}_{uuid.uuid4().hex[:12]}"
    return _generate


# ============================================================================
# MARKERS AND CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line(
        "markers", "integration: integration tests that may hit external APIs"
    )
    config.addinivalue_line(
        "markers", "slow: slow-running tests that take >5 seconds"
    )
    config.addinivalue_line(
        "markers", "database: tests that require database setup"
    )
    config.addinivalue_line(
        "markers", "payment: tests for payment flow"
    )
    config.addinivalue_line(
        "markers", "email: tests for email service"
    )
    config.addinivalue_line(
        "markers", "research: tests for research/scout functionality"
    )

    # Add missing markers found in tests
    config.addinivalue_line(
        "markers", "error_handling: tests for error handling"
    )
    config.addinivalue_line(
        "markers", "performance: tests for performance benchmarks"
    )
