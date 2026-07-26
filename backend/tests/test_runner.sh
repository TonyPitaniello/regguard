#!/bin/bash

################################################################################
# RegGuard Backend Test Runner
# Runs comprehensive test suite with coverage reporting
################################################################################

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
TESTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$TESTS_DIR")"
COVERAGE_DIR="$TESTS_DIR/coverage"
COVERAGE_HTML_DIR="$COVERAGE_DIR/html"
REPORT_FILE="$TESTS_DIR/TEST_REPORT.txt"

# Ensure coverage directory exists
mkdir -p "$COVERAGE_DIR"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          RegGuard Backend Test Suite Runner               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Check dependencies
echo -e "${YELLOW}→ Checking test dependencies...${NC}"
cd "$BACKEND_DIR"

required_packages=("pytest" "pytest-cov" "pytest-mock" "pytest-asyncio")
missing_packages=()

for pkg in "${required_packages[@]}"; do
    python -c "import ${pkg//-/_}" 2>/dev/null || missing_packages+=("$pkg")
done

if [ ${#missing_packages[@]} -gt 0 ]; then
    echo -e "${RED}✗ Missing packages: ${missing_packages[*]}${NC}"
    echo ""
    echo -e "${YELLOW}Installing missing packages...${NC}"
    pip install "${missing_packages[@]}" -q
    echo -e "${GREEN}✓ Packages installed${NC}"
else
    echo -e "${GREEN}✓ All dependencies present${NC}"
fi
echo ""

# Step 2: Run tests with coverage
echo -e "${YELLOW}→ Running test suite with coverage...${NC}"
echo ""

# Prepare test command
TEST_CMD="python -m pytest \
    $TESTS_DIR \
    -v \
    --tb=short \
    --cov=$BACKEND_DIR \
    --cov-report=term-missing \
    --cov-report=html:$COVERAGE_HTML_DIR \
    --cov-report=json:$COVERAGE_DIR/coverage.json \
    -m 'not integration' \
    --junit-xml=$COVERAGE_DIR/junit.xml \
    --color=yes"

# Run tests
if $TEST_CMD > "$REPORT_FILE" 2>&1; then
    test_status=0
else
    test_status=$?
fi

# Display test output
cat "$REPORT_FILE"
echo ""

# Step 3: Parse results
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

if [ $test_status -eq 0 ]; then
    # Count passed tests
    passed=$(grep -c "PASSED" "$REPORT_FILE" || true)
    failed=$(grep -c "FAILED" "$REPORT_FILE" || true)
    skipped=$(grep -c "SKIPPED" "$REPORT_FILE" || true)
    
    echo -e "${GREEN}✓ ALL TESTS PASSED${NC}"
    echo ""
    echo -e "  ${GREEN}PASSED:${NC}  $passed tests"
    [ $failed -gt 0 ] && echo -e "  ${RED}FAILED:${NC}  $failed tests"
    [ $skipped -gt 0 ] && echo -e "  ${YELLOW}SKIPPED:${NC} $skipped tests"
    echo ""
    
    # Show coverage summary
    echo -e "${YELLOW}→ Coverage Report:${NC}"
    grep -E "TOTAL|^[a-z_]+\.py" "$REPORT_FILE" | tail -20 || true
    echo ""
    
else
    # Show failures
    failed=$(grep -c "FAILED" "$REPORT_FILE" || true)
    passed=$(grep -c "PASSED" "$REPORT_FILE" || true)
    
    echo -e "${RED}✗ TEST SUITE FAILED${NC}"
    echo ""
    echo -e "  ${GREEN}PASSED:${NC}  $passed tests"
    echo -e "  ${RED}FAILED:${NC}  $failed tests"
    echo ""
    
    # Show failed test details
    echo -e "${RED}Failed Tests:${NC}"
    grep "FAILED" "$REPORT_FILE" | head -10 || true
    echo ""
fi

# Step 4: Coverage analysis
echo -e "${YELLOW}→ Coverage Analysis:${NC}"

# Calculate coverage percentage from JSON report if available
if [ -f "$COVERAGE_DIR/coverage.json" ]; then
    coverage_pct=$(python -c "
import json
with open('$COVERAGE_DIR/coverage.json') as f:
    data = json.load(f)
    total = data.get('totals', {})
    pct = total.get('percent_covered', 0)
    print(f'{pct:.1f}')
" 2>/dev/null || echo "N/A")
    
    echo -e "  Coverage: ${BLUE}${coverage_pct}%${NC}"
else
    echo -e "  Coverage: ${YELLOW}See HTML report${NC}"
fi

echo ""
echo -e "${YELLOW}→ Report Locations:${NC}"
echo -e "  Text Report:     ${BLUE}$REPORT_FILE${NC}"
echo -e "  HTML Coverage:   ${BLUE}$COVERAGE_HTML_DIR/index.html${NC}"
echo -e "  JUnit XML:       ${BLUE}$COVERAGE_DIR/junit.xml${NC}"
echo ""

# Step 5: Test counts
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}→ Test Inventory:${NC}"
echo ""

test_files=(
    "test_core_research.py:5"
    "test_payment_flow.py:5"
    "test_error_handling.py:4"
    "test_performance.py:2"
    "test_data_persistence.py:3"
    "test_data_accuracy.py:3"
)

total_tests=0
for file_info in "${test_files[@]}"; do
    file="${file_info%:*}"
    expected="${file_info#*:}"
    actual=$(grep -c "async def test_\|def test_" "$TESTS_DIR/$file" || echo "0")
    total_tests=$((total_tests + actual))
    printf "  %-30s %2d tests\n" "$file" "$actual"
done

echo ""
echo -e "  ${GREEN}Total Tests:${NC} ${total_tests}/25"
echo ""

# Final status
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

if [ $test_status -eq 0 ]; then
    echo -e "${GREEN}✓ Test Suite Execution Complete${NC}"
    echo ""
    echo "Launch Readiness Checklist:"
    echo -e "  ${GREEN}✓${NC} All unit tests passing"
    echo -e "  ${GREEN}✓${NC} Error handling validated"
    echo -e "  ${GREEN}✓${NC} Performance targets met"
    echo -e "  ${GREEN}✓${NC} Data integrity verified"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Test Suite Failed - Fix errors before launch${NC}"
    echo ""
    exit 1
fi
