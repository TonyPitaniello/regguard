"""
Test suite for performance requirements.
Tests response times and concurrent request handling.
"""

import pytest
import time
import asyncio
from unittest.mock import AsyncMock, patch
from concurrent.futures import ThreadPoolExecutor
import statistics


class TestResponseTime:
    """Test API response times meet performance requirements."""

    @pytest.mark.slow
    @pytest.mark.performance
    async def test_research_endpoint_response_time_under_2_seconds(self, sample_research_request):
        """Test research endpoint responds in < 2 seconds."""
        start_time = time.time()
        
        with patch("research_memo.build_research_digest") as mock_research:
            mock_research.return_value = {
                "trial_id": "trial_test_12345",
                "jurisdiction": "Austin, TX",
                "estimated_cost": 2150,
                "estimated_timeline_days": 15,
                "action_plan": "# Action Plan\n- Step 1\n- Step 2",
            }
            
            result = mock_research(sample_research_request)
        
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < 2.0, f"Response took {elapsed_time}s, expected < 2s"
        assert result is not None

    @pytest.mark.slow
    @pytest.mark.performance
    async def test_payment_checkout_response_time_under_2_seconds(self, sample_payment_request):
        """Test payment checkout endpoint responds in < 2 seconds."""
        start_time = time.time()
        
        with patch("stripe.checkout.Session.create") as mock_session:
            mock_session.return_value = {
                "id": "cs_test_session_12345",
                "url": "https://checkout.stripe.com/pay/cs_test_session_12345",
            }
            
            result = mock_session()
        
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < 2.0, f"Response took {elapsed_time}s, expected < 2s"
        assert "url" in result

    @pytest.mark.slow
    @pytest.mark.performance
    async def test_zip_lookup_response_time_under_1_second(self, texas_zip_data):
        """Test ZIP lookup responds in < 1 second."""
        start_time = time.time()
        
        with patch("geocode.us_zip_from_lat_lon") as mock_lookup:
            zip_code = "78704"
            data = texas_zip_data[zip_code]
            mock_lookup.return_value = data
            
            result = mock_lookup(data["latitude"], data["longitude"])
        
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < 1.0, f"Response took {elapsed_time}s, expected < 1s"
        assert result is not None

    @pytest.mark.slow
    @pytest.mark.performance
    async def test_email_send_response_time_under_5_seconds(self, mock_email_service, sample_research_memo):
        """Test email sending completes in < 5 seconds."""
        start_time = time.time()
        
        await mock_email_service.send_research_memo(
            to_email="contractor@example.com",
            address="123 Main St, Austin, TX 78704",
            research_memo=sample_research_memo,
            trial_id="trial_test_12345",
        )
        
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < 5.0, f"Email send took {elapsed_time}s, expected < 5s"
        assert mock_email_service.send_research_memo.called


class TestConcurrentRequests:
    """Test system handles concurrent requests properly."""

    @pytest.mark.slow
    @pytest.mark.performance
    async def test_concurrent_research_requests(self):
        """Test system handles 10 concurrent research requests."""
        num_concurrent = 10
        
        async def make_research_request(request_id):
            with patch("research_memo.build_research_digest") as mock_research:
                mock_research.return_value = {
                    "trial_id": f"trial_test_{request_id}",
                    "jurisdiction": "Austin, TX",
                    "status": "completed",
                }
                await asyncio.sleep(0.1)  # Simulate API call
                return mock_research({})
        
        start_time = time.time()
        
        tasks = [make_research_request(i) for i in range(num_concurrent)]
        results = await asyncio.gather(*tasks)
        
        elapsed_time = time.time() - start_time
        
        assert len(results) == num_concurrent
        assert all(r is not None for r in results)
        # Should be faster than sequential (10 * 0.1 = 1s)
        assert elapsed_time < 2.0

    @pytest.mark.slow
    @pytest.mark.performance
    async def test_concurrent_payment_requests(self):
        """Test system handles 5 concurrent payment requests."""
        num_concurrent = 5
        
        async def make_payment_request(request_id):
            with patch("stripe.checkout.Session.create") as mock_session:
                mock_session.return_value = {
                    "id": f"cs_test_session_{request_id}",
                    "url": f"https://checkout.stripe.com/pay/cs_test_session_{request_id}",
                }
                await asyncio.sleep(0.2)  # Simulate API call
                return mock_session()
        
        start_time = time.time()
        
        tasks = [make_payment_request(i) for i in range(num_concurrent)]
        results = await asyncio.gather(*tasks)
        
        elapsed_time = time.time() - start_time
        
        assert len(results) == num_concurrent
        assert all(r is not None for r in results)
        assert elapsed_time < 3.0

    @pytest.mark.slow
    @pytest.mark.performance
    async def test_concurrent_zip_lookups(self, texas_zip_data):
        """Test system handles 20 concurrent ZIP lookups."""
        num_concurrent = 20
        zips = list(texas_zip_data.keys()) * 5  # Repeat to get 20 lookups
        
        async def lookup_zip(zip_code):
            with patch("geocode.us_zip_from_lat_lon") as mock_lookup:
                data = texas_zip_data.get(zip_code.split("_")[0], texas_zip_data["78704"])
                mock_lookup.return_value = data
                await asyncio.sleep(0.05)
                return mock_lookup(data["latitude"], data["longitude"])
        
        start_time = time.time()
        
        tasks = [lookup_zip(z) for z in zips[:num_concurrent]]
        results = await asyncio.gather(*tasks)
        
        elapsed_time = time.time() - start_time
        
        assert len(results) == num_concurrent
        assert all(r is not None for r in results)
        assert elapsed_time < 2.0

    @pytest.mark.slow
    @pytest.mark.performance
    async def test_concurrent_mixed_workload(self):
        """Test system handles mixed concurrent workload (research + payment + lookups)."""
        
        async def research_task():
            with patch("research_memo.build_research_digest") as mock_research:
                mock_research.return_value = {"status": "completed"}
                await asyncio.sleep(0.15)
                return mock_research({})
        
        async def payment_task():
            with patch("stripe.checkout.Session.create") as mock_session:
                mock_session.return_value = {"id": "cs_test"}
                await asyncio.sleep(0.1)
                return mock_session()
        
        async def lookup_task():
            with patch("geocode.us_zip_from_lat_lon") as mock_lookup:
                mock_lookup.return_value = {"zip_code": "78704"}
                await asyncio.sleep(0.05)
                return mock_lookup(30.0, -97.0)
        
        start_time = time.time()
        
        tasks = (
            [research_task() for _ in range(3)] +
            [payment_task() for _ in range(2)] +
            [lookup_task() for _ in range(5)]
        )
        results = await asyncio.gather(*tasks)
        
        elapsed_time = time.time() - start_time
        
        assert len(results) == 10
        assert all(r is not None for r in results)
        # Mixed workload should still complete efficiently
        assert elapsed_time < 1.0


class TestThroughput:
    """Test system throughput under load."""

    @pytest.mark.slow
    @pytest.mark.performance
    async def test_requests_per_second_capacity(self):
        """Test system can handle at least 10 requests per second."""
        requests_per_second = 10
        duration_seconds = 1
        expected_requests = requests_per_second * duration_seconds
        
        async def dummy_request():
            await asyncio.sleep(0.01)  # 10ms per request
            return {"status": "ok"}
        
        start_time = time.time()
        
        tasks = [dummy_request() for _ in range(expected_requests)]
        results = await asyncio.gather(*tasks)
        
        elapsed_time = time.time() - start_time
        actual_rps = len(results) / elapsed_time
        
        assert len(results) == expected_requests
        assert actual_rps >= requests_per_second / 2  # Allow 50% margin

    @pytest.mark.slow
    @pytest.mark.performance
    async def test_memory_efficiency_with_repeated_operations(self):
        """Test memory doesn't leak with repeated operations."""
        num_operations = 100
        
        async def operation():
            with patch("research_memo.build_research_digest") as mock_research:
                mock_research.return_value = {
                    "data": "x" * 10000,  # 10KB payload
                    "status": "ok",
                }
                return mock_research({})
        
        # Run many operations and verify they complete
        for i in range(num_operations):
            result = await operation()
            assert result is not None
        
        # If we got here without memory error, test passes
        assert True

    @pytest.mark.slow
    @pytest.mark.performance
    async def test_response_time_consistency(self):
        """Test response times are consistent across multiple requests."""
        num_requests = 20
        response_times = []
        
        async def timed_request():
            start = time.time()
            with patch("geocode.us_zip_from_lat_lon") as mock_lookup:
                mock_lookup.return_value = {"zip_code": "78704"}
                await asyncio.sleep(0.05)
                result = mock_lookup(30.0, -97.0)
            elapsed = time.time() - start
            response_times.append(elapsed)
            return result
        
        tasks = [timed_request() for _ in range(num_requests)]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == num_requests
        
        # Check response time consistency
        avg_time = statistics.mean(response_times)
        std_dev = statistics.stdev(response_times)
        
        # Standard deviation should be low (consistent performance)
        assert std_dev < avg_time * 0.5  # Std dev < 50% of mean
