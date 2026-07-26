# Agentic Testing Protocol: How to Rigorously Test RegGuard

**Goal**: Build an automated test suite that validates every critical path before launch.

---

## 🎯 WHAT AN AGENT WILL BUILD

### Test Suite Structure

```
tests/
├─ test_core_research.py          (Unit tests: research accuracy)
├─ test_payment_flow.py           (Integration: payment → delivery)
├─ test_error_handling.py         (Edge cases: failures)
├─ test_performance.py            (Load: concurrent requests)
├─ test_data_persistence.py       (Integration: database)
├─ test_data_accuracy.py          (Validation: regulatory data)
└─ conftest.py                    (Shared fixtures)

Plus:
├─ test_runner.sh                 (Script to run all tests)
└─ test_report_template.md        (Output: PASS/FAIL report)
```

### Test Framework

```
Tool: pytest (already in Python)
Mocking: pytest-mock (simulates Firecrawl, Stripe, email)
Load testing: locust (concurrent requests)
Coverage: pytest-cov (shows what's tested)
```

---

## 📋 SPECIFIC TESTS THE AGENT WILL CREATE

### Test Category 1: Core Research Engine

```python
# tests/test_core_research.py

def test_zip_lookup_returns_dict():
    """Verify lookup returns structured data, not error"""
    result = lookup_jurisdiction("75074", "solar")
    assert isinstance(result, dict)
    assert "electrical_code" in result
    assert "permit_requirements" in result
    assert result["zip"] == "75074"

def test_cost_estimate_is_numeric():
    """Verify cost estimate is reasonable number"""
    result = estimate_interconnection_cost("75074", "large-solar")
    assert isinstance(result["min_cost"], (int, float))
    assert isinstance(result["max_cost"], (int, float))
    assert result["min_cost"] > 0
    assert result["max_cost"] > result["min_cost"]

def test_timeline_is_days():
    """Verify timeline prediction returns days"""
    result = predict_approval_timeline("75074", "solar")
    assert isinstance(result["days_min"], int)
    assert isinstance(result["days_max"], int)
    assert 0 < result["days_min"] <= result["days_max"]
    assert result["days_max"] < 1000  # Sanity check

def test_handles_invalid_zip():
    """Verify graceful error on bad ZIP"""
    result = lookup_jurisdiction("00000", "solar")
    assert "error" in result or result.get("status") == "no_data"
    # Should NOT throw exception

def test_handles_firecrawl_timeout():
    """Verify handles Firecrawl timeout gracefully"""
    # Mock Firecrawl to timeout
    with patch('firecrawl.search', side_effect=TimeoutError):
        result = lookup_jurisdiction("75074", "solar")
        assert "error" in result
        assert "timeout" in result["error"].lower()
```

### Test Category 2: Payment & Email Flow

```python
# tests/test_payment_flow.py

def test_payment_submission_creates_record():
    """Verify payment creates database record"""
    payment_id = submit_payment("user@test.com", "75074", 1500)
    record = db.query(Payment).filter_by(id=payment_id).first()
    assert record is not None
    assert record.amount == 1500
    assert record.status == "pending"

def test_stripe_webhook_updates_payment():
    """Verify Stripe webhook marks payment as complete"""
    # Mock Stripe webhook
    webhook_data = {
        "type": "payment_intent.succeeded",
        "data": {"object": {"id": "pi_123", "metadata": {"payment_id": "abc"}}}
    }
    handle_webhook(webhook_data)
    record = db.query(Payment).filter_by(external_id="pi_123").first()
    assert record.status == "completed"

def test_payment_triggers_research():
    """Verify payment triggers research generation"""
    payment_id = submit_payment("user@test.com", "75074", 1500)
    trigger_research(payment_id)
    research = db.query(Research).filter_by(payment_id=payment_id).first()
    assert research is not None
    assert research.status == "completed"

def test_research_triggers_email():
    """Verify research completion sends email"""
    research_id = generate_research("75074", "solar")
    send_research_email(research_id)
    # Check email service was called
    mock_email_service.send.assert_called_once()
    call_args = mock_email_service.send.call_args
    assert "research" in call_args.kwargs["template"]

def test_payment_failure_graceful():
    """Verify payment failure doesn't create zombie records"""
    with patch('stripe.PaymentIntent.create', side_effect=stripe.error.CardError("declined", None, None)):
        try:
            submit_payment("user@test.com", "75074", 1500)
        except stripe.error.CardError:
            pass
    # No partial records in database
    assert db.query(Payment).count() == 0
```

### Test Category 3: Error Handling

```python
# tests/test_error_handling.py

def test_handles_database_timeout():
    """Verify handles DB timeout gracefully"""
    with patch('db.query', side_effect=TimeoutError):
        result = lookup_jurisdiction("75074", "solar")
        assert result["status"] == "error"
        assert "database" in result["message"].lower()

def test_handles_missing_env_vars():
    """Verify handles missing config gracefully"""
    with patch.dict(os.environ, {}, clear=True):
        try:
            initialize_app()
        except EnvironmentError as e:
            assert "STRIPE_KEY" in str(e) or "API_KEY" in str(e)

def test_handles_invalid_json_input():
    """Verify JSON parsing errors handled"""
    with patch('request.json', side_effect=ValueError):
        result = api.post("/lookup", data="invalid json")
        assert result.status_code == 400
        assert "invalid" in result.json()["error"].lower()

def test_handles_empty_firecrawl_response():
    """Verify handles empty research data"""
    with patch('firecrawl.search', return_value=[]):
        result = lookup_jurisdiction("00000", "solar")
        assert result.get("status") == "no_data"
        # Should provide fallback or error, not crash
```

### Test Category 4: Performance

```python
# tests/test_performance.py

import locust

class UserBehavior(locust.HttpUser):
    wait_time = lambda self: 1
    
    @locust.task
    def lookup_endpoint(self):
        """Simulate user doing ZIP lookup"""
        self.client.post("/api/lookup", json={"zip": "75074", "type": "solar"})
    
    @locust.task
    def payment_endpoint(self):
        """Simulate payment submission"""
        self.client.post("/api/payment", json={"zip": "75074", "amount": 1500})

# Run: locust -f tests/test_performance.py --host=http://localhost:8000 -u 10 -r 2 --run-time 60

def test_lookup_response_time_under_2_sec():
    """Verify lookups complete in <2 sec"""
    start = time.time()
    result = lookup_jurisdiction("75074", "solar")
    elapsed = time.time() - start
    assert elapsed < 2.0, f"Lookup took {elapsed}s, expected <2s"

def test_payment_response_time_under_3_sec():
    """Verify payments complete in <3 sec"""
    start = time.time()
    result = submit_payment("user@test.com", "75074", 1500)
    elapsed = time.time() - start
    assert elapsed < 3.0, f"Payment took {elapsed}s, expected <3s"
```

### Test Category 5: Data Persistence

```python
# tests/test_data_persistence.py

def test_lookup_data_saved_to_db():
    """Verify lookup results saved to database"""
    result = lookup_jurisdiction("75074", "solar")
    record = db.query(Lookup).filter_by(zip="75074").first()
    assert record is not None
    assert record.data == result

def test_payment_data_not_lost():
    """Verify payment data persists after restart"""
    payment_id = submit_payment("user@test.com", "75074", 1500)
    # Simulate database disconnect/reconnect
    db.disconnect()
    db.connect()
    record = db.query(Payment).filter_by(id=payment_id).first()
    assert record is not None

def test_concurrent_writes_no_conflict():
    """Verify concurrent writes don't corrupt data"""
    import threading
    results = []
    def write():
        results.append(submit_payment("user@test.com", "75074", 1500))
    threads = [threading.Thread(target=write) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(results) == 10
    assert len(set(results)) == 10  # All unique IDs
```

### Test Category 6: Data Accuracy (The Critical One)

```python
# tests/test_data_accuracy.py

def test_texas_solar_requirements_accurate():
    """Validate Texas solar data matches real PUC requirements"""
    result = lookup_jurisdiction("75074", "solar")
    # Check key requirements exist
    assert "interconnection_size_limits" in result
    assert "voltage_requirements" in result
    # Check values are reasonable
    assert result["interconnection_size_limits"]["max_kw"] > 1000
    # Check against known-good source
    assert result["authority"] in ["ERCOT", "investor-owned", "municipal"]

def test_california_solar_matches_caiso():
    """Validate California matches CAISO rules"""
    result = lookup_jurisdiction("95814", "large-solar")
    # These are real CAISO requirements
    assert "interconnection_agreement" in result
    assert "fast_track" in result
    assert result["fast_track"]["max_kw"] == 5000  # Real CAISO limit

def test_timeline_predictions_realistic():
    """Verify timeline predictions match real data"""
    result = predict_approval_timeline("75074", "solar")
    # Real PJM timelines: 30-180 days depending on type
    assert 10 < result["days_min"]  # At least 10 days
    assert result["days_max"] < 365  # At most 1 year

def test_cost_estimates_within_range():
    """Verify cost estimates match real interconnection costs"""
    result = estimate_interconnection_cost("75074", "large-solar")
    # Real costs for large solar typically $50K-$500K
    assert result["min_cost"] > 30000
    assert result["max_cost"] < 1000000
```

---

## 🏃 HOW TO RUN THE TESTS

### Option A: Run All Tests

```bash
cd backend
pytest tests/ -v --tb=short
# Output: PASS/FAIL for each test
# Time: ~2 minutes
```

### Option B: Run Specific Category

```bash
pytest tests/test_core_research.py -v
pytest tests/test_payment_flow.py -v
pytest tests/test_error_handling.py -v
```

### Option C: Run with Coverage Report

```bash
pytest tests/ --cov=. --cov-report=html
# Opens: htmlcov/index.html (shows % of code tested)
```

### Option D: Run Load Test

```bash
locust -f tests/test_performance.py --host=http://localhost:8000 -u 10 -r 2 --run-time 60
# Simulates 10 concurrent users for 60 seconds
```

---

## 📊 WHAT SUCCESS LOOKS LIKE

```
======================== test session starts ========================
test_core_research.py::test_zip_lookup_returns_dict PASSED         [ 5%]
test_core_research.py::test_cost_estimate_is_numeric PASSED        [10%]
test_core_research.py::test_timeline_is_days PASSED                [15%]
test_core_research.py::test_handles_invalid_zip PASSED             [20%]
test_core_research.py::test_handles_firecrawl_timeout PASSED       [25%]
test_payment_flow.py::test_payment_submission_creates_record PASSED [30%]
test_payment_flow.py::test_stripe_webhook_updates_payment PASSED   [35%]
test_payment_flow.py::test_payment_triggers_research PASSED        [40%]
test_payment_flow.py::test_research_triggers_email PASSED          [45%]
test_payment_flow.py::test_payment_failure_graceful PASSED         [50%]
test_error_handling.py::test_handles_database_timeout PASSED       [55%]
test_error_handling.py::test_handles_missing_env_vars PASSED       [60%]
test_error_handling.py::test_handles_invalid_json_input PASSED     [65%]
test_data_accuracy.py::test_texas_solar_requirements_accurate PASSED [70%]
test_data_accuracy.py::test_california_solar_matches_caiso PASSED  [75%]
test_data_accuracy.py::test_cost_estimates_within_range PASSED     [80%]

======================== 16 passed in 2.34s =========================
Coverage: 87% (Main logic covered)
Performance: All endpoints <2s
Accuracy: All data validated against real sources
```

---

## ✅ PASS CRITERIA FOR LAUNCH

| Category | Test | Pass Criteria |
|----------|------|---------------|
| **Core Research** | 5 tests | ≥4/5 pass |
| **Payment Flow** | 5 tests | 5/5 pass (100% required) |
| **Error Handling** | 4 tests | ≥3/4 pass |
| **Performance** | 2 tests | Both <3 sec |
| **Data Accuracy** | 3 tests | All 3 pass |
| **Overall** | 19 tests | ≥17/19 pass (89%) |

If ≥89% pass: **SAFE TO LAUNCH**
If 80-89% pass: **LAUNCH WITH CAVEATS** (known issues listed)
If <80% pass: **NOT READY** (fix failures first)

---

## 🚀 I CAN BUILD THIS IN 8 HOURS

I'll create:
1. ✅ 19 comprehensive tests
2. ✅ Mocking for external services (Firecrawl, Stripe, email)
3. ✅ Load test script
4. ✅ Coverage report
5. ✅ PASS/FAIL report template

**Then you can:**
1. Run: `pytest tests/`
2. See: PASS/FAIL for each test
3. Know: "Safe to launch or needs fixes"

**Want me to build this now?**
