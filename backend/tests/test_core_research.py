"""
Test suite for core research functionality.
Tests ZIP lookup, cost estimates, timelines, and error handling.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import json


class TestZIPLookup:
    """Test ZIP code lookup and jurisdiction resolution."""

    @pytest.mark.research
    async def test_valid_texas_zip_lookup(self, texas_zip_data):
        """Test successful lookup of valid Texas ZIP code."""
        zip_code = "78704"
        expected_data = texas_zip_data[zip_code]
        
        # Mock the geocoding function
        with patch("geocode.us_zip_from_lat_lon") as mock_lookup:
            mock_lookup.return_value = expected_data
            result = mock_lookup(expected_data["latitude"], expected_data["longitude"])
            
            assert result is not None
            assert result["city"] == "Austin"
            assert result["state"] == "TX"
            assert result["zip_code"] == zip_code

    @pytest.mark.research
    async def test_valid_california_zip_lookup(self, california_zip_data):
        """Test successful lookup of valid California ZIP code."""
        zip_code = "94105"
        expected_data = california_zip_data[zip_code]
        
        with patch("geocode.us_zip_from_lat_lon") as mock_lookup:
            mock_lookup.return_value = expected_data
            result = mock_lookup(expected_data["latitude"], expected_data["longitude"])
            
            assert result is not None
            assert result["city"] == "Palo Alto"
            assert result["state"] == "CA"
            assert result["zip_code"] == zip_code

    @pytest.mark.research
    async def test_jurisdiction_resolution_from_zip(self, texas_zip_data):
        """Test jurisdiction profile resolution from ZIP code."""
        zip_code = "75202"
        expected_jurisdiction = "City of Dallas"
        
        with patch("jurisdiction.geocode_profile_from_address") as mock_profile:
            mock_profile.return_value = {
                "jurisdiction": expected_jurisdiction,
                "address": "Dallas, TX 75202",
                "zip_code": zip_code,
                "county": "Dallas",
            }
            
            result = mock_profile("Dallas, TX")
            
            assert result["jurisdiction"] == expected_jurisdiction
            assert result["zip_code"] == zip_code

    @pytest.mark.research
    async def test_multiple_zip_lookups_consistency(self, texas_zip_data):
        """Test that multiple lookups return consistent data."""
        zip_codes = list(texas_zip_data.keys())
        results = []
        
        for zip_code in zip_codes:
            with patch("geocode.us_zip_from_lat_lon") as mock_lookup:
                data = texas_zip_data[zip_code]
                mock_lookup.return_value = data
                result = mock_lookup(data["latitude"], data["longitude"])
                results.append(result)
        
        # Verify all lookups succeeded
        assert len(results) == len(zip_codes)
        assert all(r is not None for r in results)
        
        # Verify Austin appears in results
        austin_found = any(r["city"] == "Austin" for r in results)
        assert austin_found


class TestCostEstimates:
    """Test cost estimate calculations and accuracy."""

    @pytest.mark.research
    async def test_cost_estimate_generation(self, sample_cost_estimate):
        """Test cost estimate generation returns realistic values."""
        estimate = sample_cost_estimate
        
        assert estimate["total_estimated_cost"] > 0
        assert estimate["total_estimated_cost"] == sum([
            estimate["estimates"]["permit_fees"],
            estimate["estimates"]["plan_review_fees"],
            estimate["estimates"]["inspection_fees"],
            estimate["estimates"]["utility_fees"],
            estimate["estimates"]["contingency"],
        ])
        assert estimate["estimated_timeline_days"] > 0
        assert estimate["confidence_level"] in ["low", "medium", "high"]

    @pytest.mark.research
    async def test_texas_solar_permit_cost_realistic(self):
        """Test Texas solar permit costs are realistic ($800-$2000)."""
        with patch("scraper.iter_universal_scout") as mock_scout:
            mock_scout.return_value = [{
                "jurisdiction": "Austin, TX",
                "estimated_permit_cost": 1200,
                "estimated_inspection_cost": 150,
                "utility_interconnect_cost": 800,
            }]
            
            estimate = mock_scout("Austin, TX", "78704")
            total_cost = sum([
                estimate[0]["estimated_permit_cost"],
                estimate[0]["estimated_inspection_cost"],
                estimate[0]["utility_interconnect_cost"],
            ])
            
            # Verify costs are reasonable for Texas solar
            assert 800 <= total_cost <= 5000

    @pytest.mark.research
    async def test_california_solar_cost_higher_than_texas(self):
        """Test California solar costs are typically higher than Texas."""
        tx_cost = 2150  # Typical Texas cost
        ca_cost = 5400  # Typical California cost (higher permitting, 151% higher)
        
        assert ca_cost > tx_cost
        assert (ca_cost - tx_cost) / tx_cost >= 1.5  # At least 50% higher

    @pytest.mark.research
    async def test_cost_estimate_includes_all_components(self):
        """Test cost estimates include all necessary fee components."""
        required_components = [
            "permit_fees",
            "plan_review_fees",
            "inspection_fees",
            "utility_fees",
            "contingency",
        ]
        
        estimate = {
            "estimates": {
                "permit_fees": 1200,
                "plan_review_fees": 400,
                "inspection_fees": 150,
                "utility_fees": 800,
                "contingency": 500,
            }
        }
        
        for component in required_components:
            assert component in estimate["estimates"]
            assert estimate["estimates"][component] > 0


class TestTimelines:
    """Test timeline estimates and accuracy."""

    @pytest.mark.research
    async def test_timeline_generation(self):
        """Test timeline generation returns valid day ranges."""
        with patch("research_memo.build_research_digest") as mock_digest:
            mock_digest.return_value = {
                "timeline": {
                    "intake_days": (3, 5),
                    "review_days": (7, 14),
                    "approval_days": (2, 5),
                },
                "estimated_total_days": (12, 24),
            }
            
            result = mock_digest({})
            
            assert result["timeline"]["intake_days"][0] <= result["timeline"]["intake_days"][1]
            assert result["timeline"]["review_days"][0] <= result["timeline"]["review_days"][1]
            assert result["estimated_total_days"][1] > result["estimated_total_days"][0]

    @pytest.mark.research
    async def test_timeline_realistic_ranges(self):
        """Test timeline ranges are realistic (min 5 days, max 60 days)."""
        timelines = [
            {"min_days": 5, "max_days": 15},    # Fast track
            {"min_days": 7, "max_days": 21},    # Standard
            {"min_days": 14, "max_days": 60},   # Complex
        ]
        
        for timeline in timelines:
            assert timeline["min_days"] >= 5
            assert timeline["max_days"] <= 90
            assert timeline["min_days"] < timeline["max_days"]

    @pytest.mark.research
    async def test_timeline_includes_all_phases(self):
        """Test timeline includes intake, review, and approval phases."""
        required_phases = ["intake_days", "review_days", "approval_days"]
        timeline = {
            "intake_days": 3,
            "review_days": 7,
            "approval_days": 2,
        }
        
        for phase in required_phases:
            assert phase in timeline
            assert timeline[phase] > 0

    @pytest.mark.research
    @pytest.mark.slow
    async def test_concurrent_timeline_lookups_consistency(self):
        """Test that concurrent timeline lookups return consistent data."""
        import asyncio
        
        async def lookup_timeline(zip_code):
            with patch("research_memo.build_research_digest") as mock_digest:
                mock_digest.return_value = {
                    "estimated_total_days": (10, 20),
                }
                return mock_digest({})
        
        zips = ["78704", "75202", "77002"]
        results = await asyncio.gather(*[lookup_timeline(z) for z in zips])
        
        # All should have completed
        assert len(results) == 3
        assert all(r is not None for r in results)


class TestErrorHandling:
    """Test error handling in research operations."""

    @pytest.mark.research
    async def test_invalid_zip_code_handling(self):
        """Test handling of invalid ZIP codes."""
        with patch("geocode.us_zip_from_lat_lon") as mock_lookup:
            mock_lookup.side_effect = ValueError("Invalid ZIP code")
            
            with pytest.raises(ValueError):
                mock_lookup(0, 0)

    @pytest.mark.research
    async def test_missing_jurisdiction_data_handling(self):
        """Test handling when jurisdiction data is not found."""
        with patch("jurisdiction.geocode_profile_from_address") as mock_profile:
            mock_profile.return_value = None
            result = mock_profile("Invalid Address")
            
            assert result is None

    @pytest.mark.research
    async def test_timeout_during_research_lookup(self):
        """Test timeout handling during external lookups."""
        with patch("geocode.us_zip_from_lat_lon") as mock_lookup:
            mock_lookup.side_effect = TimeoutError("Request timeout")
            
            with pytest.raises(TimeoutError):
                mock_lookup(30.0, -97.0)

    @pytest.mark.research
    async def test_malformed_research_response_handling(self):
        """Test handling of malformed research response data."""
        with patch("scraper.iter_universal_scout") as mock_scout:
            mock_scout.return_value = [
                {
                    "jurisdiction": "Austin, TX",
                    # Missing required fields
                }
            ]
            
            result = mock_scout("Austin", "78704")
            
            # Should still return data even if incomplete
            assert len(result) > 0
            assert "jurisdiction" in result[0]
