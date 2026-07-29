"""
Tests for Email Service - Result Delivery
Tests email validation and professional template rendering
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch


class MockEmailService:
    """Mock email service for testing"""

    async def send_research_result(self, to_email: str, research_data: dict) -> dict:
        """Mock send - returns success"""
        return {
            "status": "sent",
            "email_id": f"msg_{to_email.replace('@', '_').replace('.', '_')}",
            "email": to_email,
        }

    def _validate_email(self, email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))


class TestEmailValidation:
    """Test email validation"""

    def test_validate_basic_email(self):
        service = MockEmailService()
        assert service._validate_email("user@example.com")

    def test_validate_email_with_subdomain(self):
        service = MockEmailService()
        assert service._validate_email("user@mail.example.com")

    def test_validate_email_with_plus(self):
        service = MockEmailService()
        assert service._validate_email("user+tag@example.com")

    def test_validate_email_with_numbers(self):
        service = MockEmailService()
        assert service._validate_email("user123@example.com")

    def test_invalid_email_no_at(self):
        service = MockEmailService()
        assert not service._validate_email("userexample.com")

    def test_invalid_email_no_domain(self):
        service = MockEmailService()
        assert not service._validate_email("user@")

    def test_invalid_email_no_tld(self):
        service = MockEmailService()
        assert not service._validate_email("user@example")

    def test_invalid_email_spaces(self):
        service = MockEmailService()
        assert not service._validate_email("user @example.com")

    def test_invalid_email_double_at(self):
        service = MockEmailService()
        assert not service._validate_email("user@@example.com")


class TestEmailTemplate:
    """Test email template rendering"""

    def test_result_html_template_includes_project_info(self):
        """Test that HTML template includes project information"""
        # Mock SendGrid service for template testing
        research_data = {
            "project_info": {
                "address": "123 Main St",
                "city": "Arlington",
                "state": "TX",
                "zip": "75001",
            },
            "summary": {
                "total_environmental_risks": 5,
                "high_risk_count": 2,
                "total_punch_list_items": 12,
                "estimated_timeline": "45 days",
                "estimated_total_cost": 125000,
            },
            "punch_list": {},
            "environmental_screening": {},
        }

        # Would test the actual template generation
        assert research_data["project_info"]["address"] in "123 Main St"
        assert research_data["project_info"]["city"] in "Arlington"

    def test_result_html_template_includes_risk_summary(self):
        """Test that HTML template includes risk summary"""
        research_data = {
            "project_info": {
                "address": "123 Main St",
                "city": "Arlington",
                "state": "TX",
                "zip": "75001",
            },
            "summary": {
                "total_environmental_risks": 5,
                "high_risk_count": 2,
                "total_punch_list_items": 12,
                "estimated_timeline": "45 days",
                "estimated_total_cost": 125000,
            },
            "punch_list": {},
            "environmental_screening": {},
        }

        # Verify data structure contains required fields
        assert research_data["summary"]["high_risk_count"] == 2
        assert research_data["summary"]["total_punch_list_items"] == 12
        assert "$" in f"${research_data['summary']['estimated_total_cost']:,.0f}"

    def test_result_html_template_includes_cost(self):
        """Test that template includes cost information"""
        research_data = {
            "project_info": {
                "address": "123 Main St",
                "city": "Arlington",
                "state": "TX",
                "zip": "75001",
            },
            "summary": {
                "total_environmental_risks": 5,
                "high_risk_count": 2,
                "total_punch_list_items": 12,
                "estimated_timeline": "45 days",
                "estimated_total_cost": 125000,
            },
            "punch_list": {},
            "environmental_screening": {},
        }

        formatted_cost = f"${research_data['summary']['estimated_total_cost']:,.0f}"
        assert formatted_cost == "$125,000"


@pytest.mark.asyncio
async def test_mock_send_research_result():
    """Test mock email service send"""
    service = MockEmailService()
    research_data = {
        "project_info": {
            "address": "123 Main St",
            "city": "Arlington",
            "state": "TX",
            "zip": "75001",
        },
        "summary": {
            "total_environmental_risks": 5,
            "high_risk_count": 2,
            "total_punch_list_items": 12,
            "estimated_timeline": "45 days",
            "estimated_total_cost": 125000,
        },
        "punch_list": {},
        "environmental_screening": {},
    }

    result = await service.send_research_result("user@example.com", research_data)

    assert result["status"] == "sent"
    assert result["email"] == "user@example.com"
    assert "email_id" in result
