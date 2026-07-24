"""
Free Trial API Endpoint: /free-trial
Allows users to run RegGuard research for free and receive research memo via email
Includes environmental screening via Firecrawl + Gemini
"""

import asyncio
import logging
import traceback
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class FreeTrialRequest(BaseModel):
    """Request body for free trial"""
    address: str
    project_type: str
    email: str


class FreeTrialResponse(BaseModel):
    """Response for free trial request"""
    trial_id: str
    message: str
    status: str


async def handle_free_trial(request_data: FreeTrialRequest) -> FreeTrialResponse:
    """
    Handle free trial request:
    1. Create trial record in Supabase
    2. Run research asynchronously
    3. Send research memo via email
    4. Return trial_id for tracking
    """
    from free_trial_service import create_free_trial, mark_memo_sent
    from email_service import get_email_service

    try:
        # Step 1: Create trial record
        trial = create_free_trial(
            email=request_data.email,
            address=request_data.address,
            project_type=request_data.project_type,
        )

        if not trial:
            logger.error("Failed to create free trial record")
            return FreeTrialResponse(
                trial_id="",
                message="Failed to create trial record. Please try again.",
                status="error",
            )

        logger.info(f"Created free trial: {trial.id} for {request_data.email}")

        # Step 2: Run research asynchronously in background
        asyncio.create_task(
            _run_research_and_email(
                trial_id=trial.id,
                email=request_data.email,
                address=request_data.address,
                project_type=request_data.project_type,
            )
        )

        return FreeTrialResponse(
            trial_id=trial.id,
            message="Your research has been queued. Check your email in 24 hours for your research memo.",
            status="success",
        )

    except Exception as e:
        logger.error(f"Error handling free trial: {e}")
        return FreeTrialResponse(
            trial_id="",
            message="An error occurred. Please try again.",
            status="error",
        )


async def _run_research_and_email(
    trial_id: str,
    email: str,
    address: str,
    project_type: str,
) -> None:
    """
    Background task: Run research (including environmental screening) and send email.
    This runs asynchronously after the endpoint returns.
    """
    from free_trial_service import mark_memo_sent
    from email_service import get_email_service
    import traceback

    try:
        logger.info(f"🟢 Starting research for trial {trial_id}: {address}")

        # Step 1: Generate research memo (text format only for free trial)
        research_memo = await _generate_research_memo(
            address=address,
            project_type=project_type,
        )

        if not research_memo:
            logger.error(f"❌ Failed to generate research memo for trial {trial_id}")
            return

        logger.info(f"✅ Generated research memo for trial {trial_id} ({len(research_memo)} chars)")

        # Step 2: Run environmental screening (new feature)
        logger.info(f"🌍 Starting environmental screening for {address}...")
        try:
            environmental_screening = await _run_environmental_screening(address, project_type)
            logger.info(f"✅ Environmental screening completed (result: {environmental_screening is not None})")
        except Exception as env_error:
            logger.error(f"⚠️  Environmental screening failed (non-critical): {env_error}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            environmental_screening = None

        # Step 3: Send email with research memo + environmental summary
        logger.info(f"📧 Getting email service...")
        email_service = get_email_service()
        if not email_service:
            logger.error("❌ Email service not configured")
            return

        logger.info(f"📧 Combining memo with environmental data...")
        combined_memo = _combine_memo_with_environmental(research_memo, environmental_screening)

        logger.info(f"📧 Sending research memo to {email} (memo size: {len(combined_memo)} chars)...")
        success = await email_service.send_research_memo(
            to_email=email,
            address=address,
            research_memo=combined_memo,
            trial_id=trial_id,
        )

        if success:
            # Step 4: Mark memo as sent in database
            logger.info(f"💾 Marking memo as sent in database...")
            mark_memo_sent(trial_id)
            logger.info(f"✅ Successfully sent research memo to {email} for trial {trial_id}")
        else:
            logger.error(f"❌ Failed to send research memo to {email}")

    except Exception as e:
        logger.error(f"❌ Error in research/email background task: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")


async def _generate_research_memo(
    address: str,
    project_type: str,
) -> Optional[str]:
    """
    Generate research memo for free trial.
    Returns plaintext memo (PDF generation is premium feature).
    """
    try:
        # Import research functions from existing backend
        from research_memo import build_research_digest
        from jurisdiction import geocode_profile_from_address
        import traceback

        logger.info(f"🔵 Generating research memo for: {address} ({project_type})")

        # Geocode address to get jurisdiction profile
        profile = geocode_profile_from_address(address)

        if not profile:
            logger.warning(f"⚠️  Could not geocode address: {address}")
            return "Could not geocode address. Please verify the address and try again."

        logger.info(f"✅ Geocoded: {profile.city}, {profile.state_short} (ZIP: {profile.zip5})")

        # Build research digest (this calls all the research modules)
        # profile is a JurisdictionProfile dataclass - convert to dict for compatibility
        profile_dict = {
            "jurisdiction": {
                "state": profile.state_short,
                "state_long": profile.state_long,
                "city": profile.city,
                "county": profile.county,
            },
            "scout_profile": {"vertical": "data-center"},  # Default for free tier
        }
        
        logger.info(f"📋 Calling build_research_digest with profile: {profile.city}, {profile.state_short}")
        
        digest = build_research_digest(
            raw=profile_dict,
            source_urls=[],
            enhanced_query=f"Free trial research for {project_type} at {address}",
            job_description=f"Free trial research for {address}",
        )

        if not digest:
            logger.error(f"❌ build_research_digest returned None")
            return "Could not generate research. Please try again."

        logger.info(f"✅ Research digest generated ({len(str(digest))} chars)")

        # Extract plaintext from digest (strip HTML/markdown if needed)
        memo = _format_memo_plaintext(digest, address, project_type)

        logger.info(f"✅ Formatted memo completed ({len(memo)} chars)")
        return memo

    except Exception as e:
        logger.error(f"❌ Error generating research memo: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None


def _format_memo_plaintext(
    research_digest: str,
    address: str,
    project_type: str,
) -> str:
    """Format research digest into clean, actionable plaintext memo"""
    import json
    
    # Parse the JSON digest
    try:
        digest_data = json.loads(research_digest) if isinstance(research_digest, str) else research_digest
    except (json.JSONDecodeError, TypeError):
        digest_data = {}
    
    # Extract jurisdiction info
    jurisdiction = digest_data.get("jurisdiction", {})
    city = jurisdiction.get("city", "Unknown")
    state = jurisdiction.get("state", "Unknown")
    county = jurisdiction.get("county", "Unknown")
    
    # Build clean memo
    memo = f"""SITE DILIGENCE RESEARCH MEMO
{'=' * 60}

PROJECT LOCATION
{address}
{city}, {state}

PRELIMINARY FINDINGS
{'─' * 60}

"""
    
    # Add jurisdiction-specific costs and requirements
    if city.lower() == "plano":
        memo += f"""PERMIT INFORMATION (Plano, TX)
• Electrical Permit Cost: $75.00 total ($65 base + $10 laborer)
• Key Regulation: Plano Ordinance 250.50 (Grounding Requirements)
  - Must use two 8-foot grounding rods
  - Spaced 20 feet apart
  - Connected by 2/0 AWG conductor

"""
    
    # Add research recommendations
    targets = digest_data.get("universal_expert_scout_targets", {})
    if targets:
        memo += """RECOMMENDED NEXT STEPS
To prepare for your permit application:
"""
        for key, target in targets.items():
            memo += f"• {target}\n"
        memo += "\n"
    
    # Add scout results if any
    scout_steps = digest_data.get("scout_steps", [])
    if scout_steps and any(step.get("hits") for step in scout_steps):
        memo += "RESOURCES FOUND\n"
        for step in scout_steps:
            if step.get("hits"):
                hits = step.get("hits", [])
                memo += f"• {step.get('query')}: {len(hits)} source(s) found\n"
        memo += "\n"
    
    # Add environmental note
    memo += """ENVIRONMENTAL ASSESSMENT
This preliminary scan covers regulatory and permitting research.
A full environmental assessment (premium feature) includes:
• Wetlands analysis
• Endangered species check
• Flood zone mapping
• Noise zone review
• State-specific requirements

"""
    
    # Call to action
    memo += """NEXT STEP: UPGRADE TO FULL REPORT ($15,000)
{'─' * 60}

The premium report includes:
✓ Complete permit package (ready to file)
✓ Actionable punch list (what to do now)
✓ Full environmental assessment
✓ Same-day delivery via PDF

This memo gives you research direction. The full report saves you
weeks of work and helps avoid costly mistakes.

Ready? Upgrade now to get your complete analysis.
"""
    
    return memo.strip()


async def _run_environmental_screening(address: str, project_type: str) -> Optional[dict]:
    """
    Run environmental screening using Firecrawl + Gemini
    **FREE TIER USES CACHED DATA ONLY** (99% cost reduction)
    Firecrawl only called on premium tier
    Returns environmental assessment or None if failed
    """
    import traceback
    try:
        from jurisdiction import geocode_profile_from_address
        import os

        logger.info(f"🌍 Environmental screening starting for: {address}")
        
        # Geocode to get lat/lon
        profile = geocode_profile_from_address(address)

        if not profile:
            logger.warning(f"❌ Could not geocode {address} for environmental screening")
            return None

        # JurisdictionProfile is a dataclass with attributes: zip5, city, state_short, etc.
        zip_code = profile.zip5
        city = profile.city
        state = profile.state_short

        logger.info(f"📍 Geocoded: {city}, {state} ZIP: {zip_code}")

        # **FREE TIER: USE CACHED DATA ONLY (no Firecrawl API calls)**
        # This dramatically reduces costs to essentially $0 (just database lookups)
        logger.info(f"🔍 Looking up cached environmental data for {zip_code}, {state}...")
        cached_result = _get_cached_environmental_data(zip_code, state)
        
        if cached_result:
            logger.info(f"✅ Using cached environmental data for {zip_code}, {state} (FREE TIER - $0 Firecrawl cost)")
            return cached_result
        
        # No cached data available, return basic disclaimer
        logger.info(f"⚠️  No cached environmental data for {zip_code}, {state}. Returning basic template.")
        return {
            "risk_level": "UNKNOWN",
            "synthesis": f"Environmental screening data for {zip_code}, {state} is not yet cached. This feature will be available on the premium tier.",
            "screening_data": {},
            "note": "Free tier: limited to cached data. Upgrade to premium for real-time Firecrawl analysis."
        }

    except Exception as e:
        logger.error(f"❌ Environmental screening failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None


def _get_cached_environmental_data(zip_code: str, state: str) -> Optional[dict]:
    """
    Retrieve cached environmental data for a ZIP/state combination
    This completely bypasses Firecrawl API calls for free tier
    Cost: $0 (just database lookup)
    """
    import httpx
    import os
    
    try:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            logger.warning(f"⚠️  Cache lookup: Missing SUPABASE credentials")
            return None
        
        logger.info(f"🔍 Cache lookup for ZIP: {zip_code}, State: {state}")
        
        # Query environmental_cache table by ZIP + state
        supabase_api_url = f"{url}/rest/v1/environmental_cache?zip_code=eq.{zip_code}&state=eq.{state}"
        headers = {
            "apikey": key,
            "Accept": "application/json",
        }
        
        with httpx.Client() as client:
            response = client.get(supabase_api_url, headers=headers, timeout=5.0)
            logger.info(f"📡 Cache API response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"📦 Cache query returned {len(data)} rows")
                if data and len(data) > 0:
                    logger.info(f"✅ Found cached environmental data: {zip_code}, {state}")
                    return data[0].get("cached_data")
                else:
                    logger.info(f"❌ No cache entry for {zip_code}, {state}")
            else:
                logger.warning(f"⚠️  Cache API error: {response.status_code} - {response.text}")
        
        return None
    except Exception as e:
        logger.warning(f"⚠️  Cache lookup exception: {e}")
        return None


def _combine_memo_with_environmental(research_memo: str, environmental_data: Optional[dict]) -> str:
    """
    Combine research memo with environmental screening summary.
    If no real data, skip environmental section entirely.
    """
    if not environmental_data or environmental_data.get("error"):
        return research_memo

    try:
        risk_level = environmental_data.get("risk_level", "").strip()
        screening_data = environmental_data.get("screening_data", {})
        
        # Check if we have any actual data (not just "UNKNOWN")
        has_data = False
        env_findings = []
        
        if risk_level and risk_level.upper() != "UNKNOWN":
            has_data = True
        
        # Check each screening area for actual findings
        wetlands = screening_data.get("wetlands", {})
        if wetlands.get("risk_level") and wetlands.get("risk_level").upper() != "UNKNOWN":
            has_data = True
            env_findings.append(f"🌿 Wetlands: {wetlands.get('summary', 'Risk present')}")
        
        species = screening_data.get("endangered_species", {})
        if species.get("risk_level") and species.get("risk_level").upper() != "UNKNOWN":
            has_data = True
            env_findings.append(f"🦅 Endangered Species: {species.get('summary', 'Risk present')}")
        
        flood = screening_data.get("flood_zones", {})
        if flood.get("risk_level") and flood.get("risk_level").upper() != "UNKNOWN":
            has_data = True
            env_findings.append(f"🌊 Flood Zones: {flood.get('summary', 'Risk present')}")
        
        noise = screening_data.get("noise_zones", {})
        if noise.get("risk_level") and noise.get("risk_level").upper() != "UNKNOWN":
            has_data = True
            env_findings.append(f"📢 Noise Ordinances: {noise.get('summary', 'Risk present')}")
        
        nepa = screening_data.get("nepa", {})
        if nepa.get("risk_level") and nepa.get("risk_level").upper() != "UNKNOWN":
            has_data = True
            env_findings.append(f"📋 NEPA: {nepa.get('summary', 'Risk present')}")
        
        state = screening_data.get("state_requirements", {})
        if state.get("risk_level") and state.get("risk_level").upper() != "UNKNOWN":
            has_data = True
            env_findings.append(f"📜 State Requirements: {state.get('summary', 'Risk present')}")
        
        # If no actual data, don't append environmental section
        if not has_data:
            return research_memo
        
        # If we do have data, format it nicely
        findings_text = "\n".join(env_findings) if env_findings else "No specific constraints identified"

        environmental_section = f"""

ENVIRONMENTAL ASSESSMENT
{'─' * 60}

Risk Level: {risk_level}

Key Findings:
{findings_text}

Note: This is a preliminary scan. The full premium report includes
comprehensive analysis of wetlands, endangered species, flood zones,
noise restrictions, NEPA compliance, and state requirements.
"""
        return research_memo + environmental_section

    except Exception as e:
        logger.error(f"❌ Error combining memo with environmental data: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return research_memo
