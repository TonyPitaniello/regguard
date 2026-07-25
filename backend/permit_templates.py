"""
State-Specific Permit Templates and Auto-Fill Logic
Provides permit requirements and auto-filling capabilities per state/county
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class State(Enum):
    """Supported states"""
    TEXAS = "TX"
    CALIFORNIA = "CA"
    NEW_YORK = "NY"
    FLORIDA = "FL"
    COLORADO = "CO"


@dataclass
class PermitTemplate:
    """Template for a specific permit type"""
    state: str
    municipality: str
    permit_name: str
    authority: str
    typical_fee: float
    estimated_timeline_days: int
    key_requirements: List[str]
    forms_required: List[str]
    documents_needed: List[str]
    inspector_checklist: List[str]


# ============================================================================
# TEXAS PERMITS
# ============================================================================

TEXAS_PLANO_ELECTRICAL = PermitTemplate(
    state="TX",
    municipality="Plano",
    permit_name="Electrical Permit",
    authority="City of Plano Building Department",
    typical_fee=500,
    estimated_timeline_days=10,
    key_requirements=[
        "Compliance with Plano Ordinance 250.50",
        "Two 8-foot grounding rods (minimum)",
        "Rods spaced 20 feet apart",
        "Connected by 2/0 AWG conductor",
        "Licensed electrician signature required",
    ],
    forms_required=[
        "Application for Electrical Permit (Form PL-001)",
        "Electrical Single Line Diagram",
        "Grounding Plan (as applicable)",
    ],
    documents_needed=[
        "Site plan (8.5x11 or larger)",
        "Electrical one-line diagram",
        "Proof of Professional Engineer license (if applicable)",
        "Property deed or authorization letter",
    ],
    inspector_checklist=[
        "Verify permit number and date",
        "Check contractor license",
        "Inspect grounding installation",
        "Test continuity of grounding",
        "Verify material specifications",
        "Sign final approval",
    ],
)

TEXAS_DALLAS_ENVIRONMENTAL = PermitTemplate(
    state="TX",
    municipality="Dallas",
    permit_name="Environmental Permit",
    authority="City of Dallas Environmental Services",
    typical_fee=1200,
    estimated_timeline_days=21,
    key_requirements=[
        "Phase 1 Environmental Site Assessment",
        "Stormwater pollution prevention plan",
        "Erosion control measures",
        "Wetlands assessment (if applicable)",
    ],
    forms_required=[
        "Environmental Compliance Application (Form DA-ENV-2024)",
        "Phase 1 ESA Report",
        "Stormwater Plan",
    ],
    documents_needed=[
        "Phase 1 ESA (Environmental Site Assessment)",
        "Stormwater Pollution Prevention Plan",
        "Site photos (before and after)",
        "Spill response plan",
    ],
    inspector_checklist=[
        "Verify Phase 1 ESA completion",
        "Check pollution prevention measures",
        "Inspect erosion control",
        "Verify stormwater routing",
        "Test retention systems",
    ],
)

TEXAS_HOUSTON_INTERCONNECTION = PermitTemplate(
    state="TX",
    municipality="Houston",
    permit_name="Utility Interconnection Agreement",
    authority="City of Houston - Utility Authority",
    typical_fee=5000,
    estimated_timeline_days=60,
    key_requirements=[
        "Interconnection Study (System Impact Study)",
        "Facilities Study",
        "Relay coordination study",
        "Proof of liability insurance",
    ],
    forms_required=[
        "Interconnection Application (Large Generator)",
        "System Impact Study Request",
        "Facilities Study Request",
    ],
    documents_needed=[
        "Application for Interconnection",
        "Facility design specifications",
        "One-line diagram with protection",
        "Certificate of Insurance",
        "Grid stability analysis",
    ],
    inspector_checklist=[
        "Verify application completeness",
        "Check engineering drawings",
        "Review protection coordination",
        "Validate technical specifications",
        "Confirm insurance coverage",
        "Schedule site visit",
    ],
)

# ============================================================================
# CALIFORNIA PERMITS
# ============================================================================

CALIFORNIA_SAN_FRANCISCO_BUILDING = PermitTemplate(
    state="CA",
    municipality="San Francisco",
    permit_name="Building Permit (California Building Code)",
    authority="San Francisco Department of Building Inspection",
    typical_fee=3500,
    estimated_timeline_days=30,
    key_requirements=[
        "Compliance with California Building Code (CBC)",
        "Title 24 Energy Code adherence",
        "Seismic safety requirements",
        "ADA accessibility standards",
    ],
    forms_required=[
        "Application for Permit (SF-123)",
        "Building Code Analysis",
        "Title 24 Energy Compliance",
    ],
    documents_needed=[
        "Structural drawings (sealed by engineer)",
        "Electrical plans (sealed by engineer)",
        "Title 24 calculations",
        "CEQA (California Environmental Quality Act) documentation",
    ],
    inspector_checklist=[
        "Verify seismic compliance",
        "Check Title 24 compliance",
        "Inspect structural elements",
        "Verify electrical systems",
        "Check accessibility",
    ],
)

CALIFORNIA_LOS_ANGELES_ENERGY = PermitTemplate(
    state="CA",
    municipality="Los Angeles",
    permit_name="Energy Commission Approval",
    authority="California Energy Commission",
    typical_fee=2000,
    estimated_timeline_days=45,
    key_requirements=[
        "California Energy Commission approval",
        "DG (Distributed Generation) interconnection",
        "NGET (Net Energy Metering) eligibility",
    ],
    forms_required=[
        "Application for Distributed Generation",
        "Energy Impact Report",
    ],
    documents_needed=[
        "Project description and specifications",
        "One-line diagram",
        "Energy production forecast",
        "Grid impact analysis",
    ],
    inspector_checklist=[
        "Verify CEC approval",
        "Check DG specifications",
        "Validate metering configuration",
        "Test interconnection",
    ],
)

# ============================================================================
# NEW YORK PERMITS
# ============================================================================

NEW_YORK_NYC_BUILDING = PermitTemplate(
    state="NY",
    municipality="New York City",
    permit_name="NYC Building Permit (NYC Building Code)",
    authority="NYC Department of Buildings",
    typical_fee=4000,
    estimated_timeline_days=35,
    key_requirements=[
        "NYC Building Code compliance",
        "Energy Conservation Code (NYSERDA)",
        "Fire safety certification",
    ],
    forms_required=[
        "DOB Application (Form CF)",
        "Building Code Analysis",
        "Fire Safety Plan",
    ],
    documents_needed=[
        "Signed and sealed drawings",
        "Energy audit report",
        "Fire protection plan",
        "Professional licenses (PE, RA)",
    ],
    inspector_checklist=[
        "Verify professional licenses",
        "Check sealed documents",
        "Inspect fire safety measures",
        "Validate structural drawings",
    ],
)

# ============================================================================
# PERMIT FIELD MAPPING (Auto-Fill Logic)
# ============================================================================

FIELD_MAPPING = {
    # Project information
    "project_name": "analysis.project_info.address",
    "project_address": "analysis.project_info.address",
    "project_city": "analysis.project_info.city",
    "project_state": "analysis.project_info.state",
    "project_zip": "analysis.project_info.zip",
    "project_type": "analysis.project_info.type",
    
    # Coordinates
    "latitude": "analysis.project_info.coordinates.latitude",
    "longitude": "analysis.project_info.coordinates.longitude",
    
    # Dates
    "submission_date": "current_date",
    "analysis_date": "analysis.timestamp",
    
    # Environmental findings
    "environmental_summary": "analysis.environmental_screening.risk_level",
    "wetlands_present": "analysis.environmental_screening.findings[0].risk_level",
    "species_concern": "analysis.environmental_screening.findings[1].risk_level",
    "flood_zone": "analysis.environmental_screening.findings[2].risk_level",
    
    # Permits and timelines
    "estimated_permit_time": "analysis.punch_list.timeline_summary",
    "estimated_cost": "analysis.punch_list.estimated_total_cost",
}


class PermitAutoFill:
    """Handles auto-filling of permit forms with analysis data"""
    
    @staticmethod
    def get_field_value(analysis_data: Dict[str, Any], field_path: str) -> Any:
        """
        Extract value from analysis data using dot notation
        
        Example:
            get_field_value(data, "analysis.project_info.city")
            Returns: data["analysis"]["project_info"]["city"]
        """
        parts = field_path.split(".")
        value = analysis_data
        
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            elif isinstance(value, list) and part.isdigit():
                value = value[int(part)]
            else:
                return None
        
        return value
    
    @staticmethod
    def auto_fill_permit(
        permit_template: PermitTemplate,
        analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Auto-fill permit form with analysis data
        
        Returns dict of field_name: value for pre-filled forms
        """
        logger.info(f"Auto-filling permit: {permit_template.permit_name}")
        
        filled_fields = {}
        
        for field_name, field_path in FIELD_MAPPING.items():
            value = PermitAutoFill.get_field_value(analysis_data, field_path)
            if value is not None:
                filled_fields[field_name] = value
        
        logger.info(f"✅ Auto-filled {len(filled_fields)} fields")
        return filled_fields
    
    @staticmethod
    def generate_submission_checklist(permit_template: PermitTemplate) -> List[str]:
        """Generate pre-submission checklist for a permit"""
        checklist = [
            "□ All fields completed and accurate",
            "□ Professional seal applied (if required)",
            "□ Required documents attached",
            "□ Fees calculated and prepared",
            "□ Copies made (verify number required)",
            "□ Contact information current",
            "□ Authorization letters signed",
        ]
        
        # Add specific requirements
        for req in permit_template.key_requirements:
            checklist.append(f"□ Verified: {req}")
        
        return checklist


# ============================================================================
# STATE-SPECIFIC LOGIC
# ============================================================================

STATE_LOGIC = {
    "TX": {
        "key_authority": "Local Authorities Having Jurisdiction (AHJ)",
        "typical_cost_range": "$500-$5,000",
        "typical_timeline": "2-4 weeks",
        "requires_engineer_seal": True,
        "requires_contractor_license": True,
        "requires_insurance": False,
        "major_cities": ["Houston", "Dallas", "Austin", "San Antonio", "Plano"],
    },
    "CA": {
        "key_authority": "California Energy Commission + Local Authority",
        "typical_cost_range": "$2,000-$10,000",
        "typical_timeline": "4-8 weeks",
        "requires_engineer_seal": True,
        "requires_contractor_license": True,
        "requires_insurance": True,
        "major_cities": ["Los Angeles", "San Francisco", "San Diego", "Sacramento"],
    },
    "NY": {
        "key_authority": "NYC Department of Buildings + PSC",
        "typical_cost_range": "$1,000-$8,000",
        "typical_timeline": "3-6 weeks",
        "requires_engineer_seal": True,
        "requires_contractor_license": True,
        "requires_insurance": True,
        "major_cities": ["New York", "Buffalo", "Rochester"],
    },
}


def get_state_templates(state: str) -> List[PermitTemplate]:
    """Get all permit templates for a state"""
    templates = []
    
    if state == "TX":
        templates = [
            TEXAS_PLANO_ELECTRICAL,
            TEXAS_DALLAS_ENVIRONMENTAL,
            TEXAS_HOUSTON_INTERCONNECTION,
        ]
    elif state == "CA":
        templates = [
            CALIFORNIA_SAN_FRANCISCO_BUILDING,
            CALIFORNIA_LOS_ANGELES_ENERGY,
        ]
    elif state == "NY":
        templates = [
            NEW_YORK_NYC_BUILDING,
        ]
    
    return templates


def get_state_requirements(state: str) -> Dict[str, Any]:
    """Get state-specific requirements and recommendations"""
    return STATE_LOGIC.get(state, {
        "key_authority": "Local Authority Having Jurisdiction",
        "typical_cost_range": "$500-$5,000",
        "typical_timeline": "2-6 weeks",
        "requires_engineer_seal": True,
        "requires_contractor_license": True,
        "requires_insurance": False,
    })


async def generate_permit_package(
    analysis_data: Dict[str, Any],
    state: str
) -> Dict[str, Any]:
    """
    Generate complete permit package for a state
    
    Returns:
    {
        "state": "TX",
        "permits": [
            {
                "name": "Electrical Permit",
                "authority": "...",
                "fee": 500,
                "timeline_days": 10,
                "filled_fields": {...},
                "checklist": [...],
            },
            ...
        ],
        "state_requirements": {...},
        "total_estimated_cost": 6700,
        "total_estimated_days": 91,
    }
    """
    logger.info(f"📦 Generating permit package for {state}")
    
    try:
        templates = get_state_templates(state)
        permits = []
        total_cost = 0
        max_timeline = 0
        
        for template in templates:
            filled_fields = PermitAutoFill.auto_fill_permit(template, analysis_data)
            checklist = PermitAutoFill.generate_submission_checklist(template)
            
            permit_data = {
                "name": template.permit_name,
                "authority": template.authority,
                "fee": template.typical_fee,
                "timeline_days": template.estimated_timeline_days,
                "requirements": template.key_requirements,
                "documents_needed": template.documents_needed,
                "forms_required": template.forms_required,
                "filled_fields": filled_fields,
                "checklist": checklist,
            }
            
            permits.append(permit_data)
            total_cost += template.typical_fee
            max_timeline = max(max_timeline, template.estimated_timeline_days)
        
        package = {
            "state": state,
            "permits": permits,
            "state_requirements": get_state_requirements(state),
            "total_estimated_cost": total_cost,
            "total_estimated_days": max_timeline,
        }
        
        logger.info(f"✅ Permit package generated: ${total_cost} over {max_timeline} days")
        return package
        
    except Exception as e:
        logger.error(f"❌ Error generating permit package: {e}")
        raise
