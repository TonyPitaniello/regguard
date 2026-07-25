#!/bin/bash

# RegGuard Phase 1 MVP: End-to-End Testing Script
# This script provides manual testing steps for the free trial → results → email flow
# 
# PREREQUISITES:
# - Terminal 1: Backend running (cd backend && python -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload)
# - Terminal 2: Frontend running (cd frontend && npm run dev)
# - Browser: http://localhost:5173

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        RegGuard Phase 1 MVP: End-to-End Testing Plan          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test cases: Array of (address, project_type, description)
declare -a TEST_CASES=(
    "1601 Vontress Street, Plano, Texas 75074|data-center|Primary Test - Data Center in Plano"
    "123 Main Street, Dallas, Texas 75201|solar|Solar Project in Dallas"
    "456 Commerce Blvd, Houston, Texas 77002|industrial|Industrial Project in Houston"
    "789 Tech Park, Austin, Texas 78701|commercial|Commercial Project in Austin"
    "321 Industrial Way, San Antonio, Texas 78204|utility|Utility Project in San Antonio"
)

echo -e "${BLUE}📋 TEST CASES TO RUN:${NC}"
echo ""
for test in "${TEST_CASES[@]}"; do
    IFS="|" read -r address project_type description <<< "$test"
    echo -e "  ${GREEN}✓${NC} $description"
    echo -e "    Address: $address"
    echo -e "    Project Type: $project_type"
    echo ""
done

echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${BLUE}🚀 TESTING CHECKLIST:${NC}"
echo ""

echo -e "${YELLOW}PRE-TEST CHECKS:${NC}"
echo "  [ ] Backend running on http://localhost:8001"
echo "  [ ] Frontend running on http://localhost:5173"
echo "  [ ] VITE_BACKEND_ORIGIN env var set correctly in frontend"
echo "  [ ] Render logs visible (for email delivery)"
echo "  [ ] Resend email configured and working"
echo ""

echo -e "${YELLOW}TEST EXECUTION (per location):${NC}"
echo "  [ ] 1. Navigate to http://localhost:5173/free-trial"
echo "  [ ] 2. Auto-detect location (or enter manually)"
echo "  [ ] 3. Confirm location and ZIP code visible"
echo "  [ ] 4. Select project type from dropdown"
echo "  [ ] 5. Enter test email (e.g., test+{timestamp}@example.com)"
echo "  [ ] 6. Click 'Get Free Research Memo'"
echo "  [ ] 7. Monitor backend logs for:"
echo "          - Geocoding: 'Geocoded: {city}, {state} ZIP: {zip}'"
echo "          - Environmental screening: '🌍 Starting real environmental screening'"
echo "          - Punch list generation: '🎯 Generating punch list'"
echo "          - Email: '📧 Sending research memo to {email}'"
echo ""

echo -e "${YELLOW}RESULTS PAGE VERIFICATION:${NC}"
echo "  [ ] 1. Page loads within 5 seconds"
echo "  [ ] 2. Shows 'Your Site Diligence Analysis' heading"
echo "  [ ] 3. Shows correct location (address, city, state, ZIP)"
echo "  [ ] 4. Displays 3 risk summary cards:"
echo "          - Environmental Issues Found (number)"
echo "          - High/Critical Risks (number)"
echo "          - Overall Risk Level (HIGH/MEDIUM/LOW)"
echo ""

echo -e "${YELLOW}ENVIRONMENTAL FINDINGS SECTION:${NC}"
echo "  [ ] 1. Shows 'Environmental Findings' section"
echo "  [ ] 2. Expandable environmental categories:"
echo "          - Wetlands (USGS)"
echo "          - Endangered Species (USFWS)"
echo "          - Flood Zones (FEMA)"
echo "          - Noise Ordinances"
echo "          - NEPA Requirements"
echo "          - State Requirements"
echo "  [ ] 3. Each category shows:"
echo "          - Risk level (color coded)"
echo "          - Description of issue"
echo "          - Action items (bulleted list)"
echo "          - Research cost ($)"
echo ""

echo -e "${YELLOW}CRITICAL PATH SECTION:${NC}"
echo "  [ ] 1. Shows 'Critical Path (Top Priority)' section"
echo "  [ ] 2. Lists top 5 action items"
echo "  [ ] 3. Items clearly marked as red/urgent"
echo ""

echo -e "${YELLOW}PUNCH LIST SECTION:${NC}"
echo "  [ ] 1. Shows 'Full Action Plan' section"
echo "  [ ] 2. Shows count of items (20+) and timeline"
echo "  [ ] 3. Items color-coded by priority (CRITICAL/HIGH/MEDIUM/LOW)"
echo "  [ ] 4. Can expand to see all 20 items"
echo "  [ ] 5. Each item shows:"
echo "          - Task description"
echo "          - Priority level"
echo "          - Timeline (Week X-Y)"
echo "          - Responsible party"
echo "          - Cost estimate (if applicable)"
echo ""

echo -e "${YELLOW}SUMMARY & CTA SECTION:${NC}"
echo "  [ ] 1. Shows timeline estimate"
echo "  [ ] 2. Shows total estimated cost"
echo "  [ ] 3. Shows 'Upgrade to Full Report (\$15,000)' button"
echo "  [ ] 4. Button is clickable"
echo "  [ ] 5. Export (JSON) and Print buttons work"
echo ""

echo -e "${YELLOW}EMAIL DELIVERY VERIFICATION:${NC}"
echo "  [ ] 1. Check Render logs for successful email send"
echo "  [ ] 2. Email arrives within 5 minutes (dev) / 24 hours (prod)"
echo "  [ ] 3. Email contains:"
echo "          - Site location and project info"
echo "          - Environmental findings summary"
echo "          - Critical path items"
echo "          - Call-to-action for upgrade"
echo "  [ ] 4. Email is readable and formatted correctly"
echo "  [ ] 5. No encoding issues or broken formatting"
echo ""

echo -e "${YELLOW}MOBILE RESPONSIVENESS:${NC}"
echo "  [ ] 1. Test on Chrome DevTools mobile views:"
echo "          - iPhone SE (375px)"
echo "          - iPhone 12 Pro (390px)"
echo "          - Pixel 5 (393px)"
echo "          - iPad Air (820px)"
echo "  [ ] 2. All sections readable without horizontal scroll"
echo "  [ ] 3. Buttons clickable on touch"
echo "  [ ] 4. Text sizes appropriate"
echo "  [ ] 5. Images scale correctly"
echo ""

echo -e "${YELLOW}ACCESSIBILITY & PERFORMANCE:${NC}"
echo "  [ ] 1. Console has no JavaScript errors"
echo "  [ ] 2. Console has no warnings"
echo "  [ ] 3. Run Lighthouse audit:"
echo "          Performance: 80+"
echo "          Accessibility: 80+"
echo "          Best Practices: 80+"
echo "          SEO: 80+"
echo "  [ ] 4. Page loads within 3 seconds"
echo "  [ ] 5. Results page renders within 2 seconds"
echo ""

echo -e "${YELLOW}ERROR HANDLING:${NC}"
echo "  [ ] 1. Test with invalid address (should show geocoding error)"
echo "  [ ] 2. Test with valid address but no data (should show fallback)"
echo "  [ ] 3. Backend error doesn't crash frontend"
echo "  [ ] 4. Email send failure gracefully handled"
echo ""

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${BLUE}🎯 SUCCESS CRITERIA:${NC}"
echo ""
echo -e "${GREEN}PASS IF:${NC}"
echo "  ✓ All 5 locations generate analysis successfully"
echo "  ✓ Results page displays within 3 seconds"
echo "  ✓ All environmental categories populated with data"
echo "  ✓ Punch list shows 20+ items"
echo "  ✓ Email delivers within 5 minutes"
echo "  ✓ Mobile responsive on all screen sizes"
echo "  ✓ No console errors or warnings"
echo "  ✓ Lighthouse scores 80+ on all metrics"
echo ""

echo -e "${RED}FAIL IF:${NC}"
echo "  ✗ Analysis fails to generate"
echo "  ✗ Results page shows blank/errors"
echo "  ✗ Email doesn't arrive"
echo "  ✗ Console errors present"
echo "  ✗ Mobile layout broken"
echo "  ✗ Lighthouse scores below 70"
echo ""

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${BLUE}📊 LOGGING & MONITORING:${NC}"
echo ""
echo "Backend (Render/Local):"
echo "  - Look for: '✅ Option A analysis complete'"
echo "  - Look for: '📧 Sending research memo'"
echo "  - Look for: 'Successfully sent research memo'"
echo "  - Watch for: ❌ Error messages"
echo ""

echo "Frontend (Browser Console):"
echo "  - Look for: '✅ Analysis received, navigating to results page'"
echo "  - Watch for: ❌ Any error stack traces"
echo "  - No warnings about missing dependencies"
echo ""

echo ""
echo -e "${GREEN}Ready to test! Follow the checklist above and report any failures.${NC}"
echo ""
