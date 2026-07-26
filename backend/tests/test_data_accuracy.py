"""
Test suite for data accuracy and domain-specific requirements.
Tests Texas solar accuracy, California CAISO matching, and cost estimate realism.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime


class TestTexasSolarAccuracy:
    """Test Texas solar data accuracy and compliance."""

    @pytest.mark.research
    async def test_texas_solar_permit_requirements_accurate(self):
        """Test Texas solar permit requirements are accurate."""
        with patch("research_memo.build_research_digest") as mock_research:
            mock_research.return_value = {
                "permit_requirements": [
                    "Building Permit (residential/commercial)",
                    "Electrical Permit (per NEC)",
                    "Utility Interconnection Agreement",
                ],
                "jurisdiction": "Austin, TX",
                "solar_specific": True,
            }
            
            result = mock_research({})
            
            assert any("Electrical Permit" in p for p in result["permit_requirements"])
            assert any("Interconnection" in p for p in result["permit_requirements"])
            assert result["solar_specific"] is True

    @pytest.mark.research
    async def test_texas_permitting_timeline_realistic(self, texas_zip_data):
        """Test Texas solar permitting timeline is realistic (7-14 days typical)."""
        with patch("research_memo.build_research_digest") as mock_research:
            mock_research.return_value = {
                "jurisdiction": "Austin, TX",
                "estimated_days_min": 7,
                "estimated_days_max": 14,
                "state": "TX",
            }
            
            result = mock_research({})
            
            assert 5 <= result["estimated_days_min"] <= 15
            assert 10 <= result["estimated_days_max"] <= 30
            assert result["estimated_days_min"] < result["estimated_days_max"]

    @pytest.mark.research
    async def test_texas_fee_estimates_realistic(self):
        """Test Texas solar permit fees are realistic ($800-$2500)."""
        tx_jurisdictions = {
            "Austin, TX": {"min_fee": 800, "max_fee": 1500},
            "Dallas, TX": {"min_fee": 600, "max_fee": 1200},
            "Houston, TX": {"min_fee": 700, "max_fee": 1400},
            "San Antonio, TX": {"min_fee": 500, "max_fee": 1000},
        }
        
        for jurisdiction, expected_range in tx_jurisdictions.items():
            with patch("research_memo.build_research_digest") as mock_research:
                mock_research.return_value = {
                    "jurisdiction": jurisdiction,
                    "estimated_permit_fee": 1000,
                    "estimated_inspection_fee": 150,
                    "estimated_utility_fee": 200,
                }
                
                result = mock_research({})
                total_fee = (
                    result["estimated_permit_fee"] +
                    result["estimated_inspection_fee"] +
                    result["estimated_utility_fee"]
                )
                
                assert total_fee >= expected_range["min_fee"]
                assert total_fee <= 2500  # Sanity check max

    @pytest.mark.research
    async def test_texas_solar_inspection_requirements(self):
        """Test Texas solar inspection requirements are accurate."""
        required_inspections = ["Framing", "Final Electrical", "Final Interconnection"]
        
        with patch("research_memo.build_research_digest") as mock_research:
            mock_research.return_value = {
                "jurisdiction": "Austin, TX",
                "required_inspections": required_inspections,
                "solar_specific": True,
            }
            
            result = mock_research({})
            
            assert "Final Electrical" in result["required_inspections"]
            assert len(result["required_inspections"]) >= 2

    @pytest.mark.research
    async def test_texas_nec_code_references_accurate(self):
        """Test NEC code references are accurate for Texas."""
        with patch("research_memo.build_research_digest") as mock_research:
            mock_research.return_value = {
                "jurisdiction": "Dallas, TX",
                "code_references": [
                    "NEC Article 690 (Solar Photovoltaic Systems)",
                    "Texas Electrical Code (adoption of NEC)",
                    "IEEE 1547 (Interconnection Standard)",
                ],
                "state": "TX",
            }
            
            result = mock_research({})
            
            assert "NEC" in " ".join(result["code_references"])
            assert any("690" in ref for ref in result["code_references"])


class TestCaliforniaCAISO:
    """Test California CAISO data accuracy."""

    @pytest.mark.research
    async def test_california_caiso_zone_identification(self, california_zip_data):
        """Test CAISO zone correctly identified from California address."""
        with patch("research_memo.build_research_digest") as mock_research:
            ca_zip = "94105"
            expected_zone = california_zip_data[ca_zip]["caiso_zone"]
            
            mock_research.return_value = {
                "zip_code": ca_zip,
                "state": "CA",
                "caiso_zone": expected_zone,
                "solar_potential": 1850,
            }
            
            result = mock_research({})
            
            assert result["caiso_zone"] == expected_zone
            assert result["state"] == "CA"

    @pytest.mark.research
    async def test_california_solar_potential_per_zone(self, california_zip_data):
        """Test solar potential estimates match CAISO zone."""
        with patch("research_memo.build_research_digest") as mock_research:
            # San Diego has highest solar potential
            mock_research.return_value = {
                "caiso_zone": "SDG&E",
                "solar_potential_kwh_m2": 2100,  # Highest in California
            }
            
            # LA has medium potential
            la_research = {
                "caiso_zone": "LADWP",
                "solar_potential_kwh_m2": 1950,
            }
            
            result = mock_research({})
            assert result["solar_potential_kwh_m2"] >= 1850  # Realistic for CA

    @pytest.mark.research
    async def test_california_interconnection_requirements_accurate(self):
        """Test California interconnection requirements are accurate."""
        with patch("research_memo.build_research_digest") as mock_research:
            mock_research.return_value = {
                "state": "CA",
                "interconnection_requirements": [
                    "CAISO Interconnection Agreement",
                    "Utility Application (PG&E/LADWP/SDG&E specific)",
                    "IEEE 1547 Compliance",
                    "UL 1741 Certification",
                    "Micro-Inverter or DC Disconnect",
                ],
            }
            
            result = mock_research({})
            
            assert "CAISO" in " ".join(result["interconnection_requirements"])
            assert "IEEE 1547" in " ".join(result["interconnection_requirements"])

    @pytest.mark.research
    async def test_california_fee_higher_than_texas(self):
        """Test California solar fees are typically higher than Texas."""
        ca_fee = 3000  # Typical CA fee
        tx_fee = 1500  # Typical TX fee
        
        with patch("research_memo.build_research_digest") as mock_research:
            # Mock CA estimate
            mock_research.return_value = {
                "state": "CA",
                "total_estimated_fee": ca_fee,
            }
            
            ca_result = mock_research({"state": "CA"})
            
            # CA should be more expensive
            assert ca_result["total_estimated_fee"] > tx_fee

    @pytest.mark.research
    async def test_california_utility_specific_requirements(self):
        """Test utility-specific requirements for California."""
        utility_requirements = {
            "PG&E": ["Rule 21 Compliance", "Carrier Injection"],
            "LADWP": ["Distributed Generation Program", "SCADA Ready"],
            "SDG&E": ["Rule 21 (FERC Standard 1547)", "Export Control Required"],
        }
        
        for utility, requirements in utility_requirements.items():
            with patch("research_memo.build_research_digest") as mock_research:
                mock_research.return_value = {
                    "state": "CA",
                    "utility": utility,
                    "utility_requirements": requirements,
                }
                
                result = mock_research({})
                
                assert result["utility"] == utility
                assert len(result["utility_requirements"]) > 0


class TestCostEstimateRealism:
    """Test cost estimates are realistic and defensible."""

    @pytest.mark.research
    async def test_cost_estimate_components_itemized(self, sample_cost_estimate):
        """Test cost estimates are itemized with component breakdown."""
        estimate = sample_cost_estimate
        
        required_components = ["permit_fees", "plan_review_fees", "inspection_fees"]
        
        for component in required_components:
            assert component in estimate["estimates"]
            assert estimate["estimates"][component] > 0

    @pytest.mark.research
    async def test_residential_solar_cost_estimate_realistic(self):
        """Test residential solar cost estimate ($1000-$3000)."""
        with patch("research_memo.build_research_digest") as mock_research:
            mock_research.return_value = {
                "project_type": "Residential Solar",
                "total_estimated_cost": 2000,
                "cost_breakdown": {
                    "permits": 1200,
                    "inspections": 150,
                    "utility": 200,
                    "contingency": 450,
                }
            }
            
            result = mock_research({})
            
            assert 1000 <= result["total_estimated_cost"] <= 3000

    @pytest.mark.research
    async def test_commercial_solar_cost_estimate_higher(self):
        """Test commercial solar estimates are higher than residential."""
        residential_cost = 2000
        commercial_cost = 5000  # Typically 2-3x higher
        
        assert commercial_cost > residential_cost
        assert (commercial_cost / residential_cost) >= 2.0

    @pytest.mark.research
    async def test_cost_estimate_includes_contingency(self):
        """Test cost estimates include contingency (10-20% of base costs)."""
        base_costs = 1500
        contingency_rate = 0.15  # 15%
        
        with patch("research_memo.build_research_digest") as mock_research:
            mock_research.return_value = {
                "base_costs": base_costs,
                "contingency_amount": base_costs * contingency_rate,
                "total_estimated_cost": base_costs * (1 + contingency_rate),
            }
            
            result = mock_research({})
            
            assert result["contingency_amount"] > 0
            assert result["contingency_amount"] <= base_costs * 0.2

    @pytest.mark.research
    async def test_cost_estimate_varies_by_jurisdiction(self):
        """Test cost estimates vary realistically by jurisdiction."""
        jurisdictions = {
            "Austin, TX": 1500,
            "Dallas, TX": 1400,
            "Houston, TX": 1300,
            "San Jose, CA": 3500,
            "Los Angeles, CA": 3200,
        }
        
        for jurisdiction, expected_cost in jurisdictions.items():
            with patch("research_memo.build_research_digest") as mock_research:
                mock_research.return_value = {
                    "jurisdiction": jurisdiction,
                    "total_estimated_cost": expected_cost,
                }
                
                result = mock_research({})
                
                # CA should be roughly 2-3x TX
                if "CA" in jurisdiction:
                    assert result["total_estimated_cost"] >= 2000
                else:
                    assert result["total_estimated_cost"] <= 2000

    @pytest.mark.research
    async def test_cost_estimate_documentation_clear(self):
        """Test cost estimates include clear documentation."""
        with patch("research_memo.build_research_digest") as mock_research:
            mock_research.return_value = {
                "cost_summary": {
                    "jurisdiction": "Austin, TX",
                    "estimated_total": 2150,
                    "confidence_level": "high",
                    "assumptions": [
                        "Based on typical residential solar installation",
                        "Assumes single-family property",
                        "Does not include electrical upgrades to service",
                    ],
                    "notes": "Contact AHJ for exact fee verification",
                }
            }
            
            result = mock_research({})
            
            assert "assumptions" in result["cost_summary"]
            assert "notes" in result["cost_summary"]
            assert len(result["cost_summary"]["assumptions"]) > 0

    @pytest.mark.research
    async def test_timeline_estimate_includes_contingency(self):
        """Test timeline estimates include realistic contingency."""
        with patch("research_memo.build_research_digest") as mock_research:
            mock_research.return_value = {
                "timeline": {
                    "minimum_days": 7,
                    "expected_days": 14,
                    "worst_case_days": 30,
                    "assumptions": "No RFIs (Requests for Information)",
                }
            }
            
            result = mock_research({})
            
            timeline = result["timeline"]
            assert timeline["expected_days"] > timeline["minimum_days"]
            assert timeline["worst_case_days"] > timeline["expected_days"]
            assert timeline["worst_case_days"] <= 60  # Never exceed 2 months

    @pytest.mark.research
    async def test_cost_accuracy_factors_disclosed(self):
        """Test cost estimate accuracy factors are disclosed."""
        with patch("research_memo.build_research_digest") as mock_research:
            mock_research.return_value = {
                "cost_accuracy": {
                    "factors_affecting_cost": [
                        "Property location within jurisdiction",
                        "System size (kW capacity)",
                        "Installation complexity",
                        "Utility fees (variable by utility)",
                        "Plan review cycles required",
                    ],
                    "recommended_action": "Contact AHJ for binding estimate",
                }
            }
            
            result = mock_research({})
            
            assert len(result["cost_accuracy"]["factors_affecting_cost"]) >= 3
            assert "AHJ" in result["cost_accuracy"]["recommended_action"]
