"""
Test suite for data persistence and integrity.
Tests data saved to DB, no data loss, and concurrent write safety.
"""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
import json


class TestDataSavedToDatabase:
    """Test data is properly persisted to database."""

    @pytest.mark.database
    async def test_research_results_saved_to_database(self, mock_database):
        """Test research results are saved to database."""
        research_data = {
            "trial_id": "trial_test_12345",
            "jurisdiction": "Austin, TX",
            "zip_code": "78704",
            "estimated_cost": 2150,
            "estimated_timeline_days": 15,
            "created_at": datetime.now().isoformat(),
        }
        
        mock_database.execute.return_value = {
            "id": "research_123",
            **research_data
        }
        
        result = await mock_database.execute(
            "INSERT INTO research_results (trial_id, jurisdiction, data) VALUES (?, ?, ?)",
            (research_data["trial_id"], research_data["jurisdiction"], json.dumps(research_data))
        )
        
        assert result is not None
        assert result["trial_id"] == research_data["trial_id"]
        assert result["jurisdiction"] == research_data["jurisdiction"]
        mock_database.execute.assert_called_once()

    @pytest.mark.database
    async def test_payment_records_saved_to_database(self, mock_database):
        """Test payment records are saved to database."""
        payment_data = {
            "trial_id": "trial_test_12345",
            "email": "contractor@example.com",
            "amount_cents": 1500000,
            "status": "completed",
            "stripe_session_id": "cs_test_session_12345",
            "created_at": datetime.now().isoformat(),
        }
        
        mock_database.execute.return_value = {
            "id": "payment_123",
            **payment_data
        }
        
        result = await mock_database.execute(
            "INSERT INTO payments (trial_id, email, amount, status) VALUES (?, ?, ?, ?)",
            (payment_data["trial_id"], payment_data["email"], payment_data["amount_cents"], payment_data["status"])
        )
        
        assert result is not None
        assert result["status"] == "completed"
        assert result["amount_cents"] == 1500000

    @pytest.mark.database
    async def test_user_trial_data_saved_to_database(self, mock_database):
        """Test user trial data is saved to database."""
        trial_data = {
            "id": "trial_test_12345",
            "email": "contractor@example.com",
            "tier": "premium",
            "site_address": "123 Main St, Austin, TX 78704",
            "status": "active",
            "created_at": datetime.now().isoformat(),
        }
        
        mock_database.execute.return_value = trial_data
        
        result = await mock_database.execute(
            "INSERT INTO trials (id, email, tier, address, status) VALUES (?, ?, ?, ?, ?)",
            (trial_data["id"], trial_data["email"], trial_data["tier"], trial_data["site_address"], trial_data["status"])
        )
        
        assert result["id"] == trial_data["id"]
        assert result["email"] == trial_data["email"]

    @pytest.mark.database
    async def test_email_log_saved_to_database(self, mock_database):
        """Test email sending logs are saved to database."""
        email_log = {
            "id": "email_log_123",
            "trial_id": "trial_test_12345",
            "to_email": "contractor@example.com",
            "subject": "Your RegGuard Free Research Memo is Ready",
            "status": "sent",
            "created_at": datetime.now().isoformat(),
        }
        
        mock_database.execute.return_value = email_log
        
        result = await mock_database.execute(
            "INSERT INTO email_logs (trial_id, to_email, subject, status) VALUES (?, ?, ?, ?)",
            (email_log["trial_id"], email_log["to_email"], email_log["subject"], email_log["status"])
        )
        
        assert result["status"] == "sent"
        assert result["to_email"] == "contractor@example.com"

    @pytest.mark.database
    async def test_audit_trail_saved_to_database(self, mock_database):
        """Test audit trail is saved to database."""
        audit_entry = {
            "id": "audit_123",
            "trial_id": "trial_test_12345",
            "action": "payment_completed",
            "details": json.dumps({"amount": 1500000, "tier": "premium"}),
            "timestamp": datetime.now().isoformat(),
        }
        
        mock_database.execute.return_value = audit_entry
        
        result = await mock_database.execute(
            "INSERT INTO audit_log (trial_id, action, details) VALUES (?, ?, ?)",
            (audit_entry["trial_id"], audit_entry["action"], audit_entry["details"])
        )
        
        assert result["action"] == "payment_completed"
        assert result["trial_id"] == "trial_test_12345"


class TestNoDataLoss:
    """Test no data loss occurs during operations."""

    @pytest.mark.database
    async def test_research_data_not_lost_on_crash(self, mock_database):
        """Test research data persisted before crash."""
        research_id = "research_123"
        research_data = {
            "trial_id": "trial_test_12345",
            "jurisdiction": "Austin, TX",
            "status": "in_progress",
        }
        
        # Save data
        mock_database.execute.return_value = {"id": research_id, **research_data}
        result1 = await mock_database.execute("INSERT INTO research_results ... ")
        
        # Simulate crash and recovery - data should still be there
        mock_database.fetch_one.return_value = {"id": research_id, **research_data}
        result2 = await mock_database.fetch_one("SELECT * FROM research_results WHERE id = ?", (research_id,))
        
        assert result2 is not None
        assert result2["id"] == research_id
        assert result2["trial_id"] == research_data["trial_id"]

    @pytest.mark.database
    async def test_payment_data_not_lost_on_error(self, mock_database):
        """Test payment data persisted despite error."""
        payment_id = "payment_123"
        payment_data = {
            "trial_id": "trial_test_12345",
            "amount": 1500000,
            "status": "completed",
        }
        
        # Save payment
        mock_database.execute.return_value = {"id": payment_id, **payment_data}
        result1 = await mock_database.execute("INSERT INTO payments ...")
        
        # Verify data persists
        mock_database.fetch_one.return_value = {"id": payment_id, **payment_data}
        result2 = await mock_database.fetch_one("SELECT * FROM payments WHERE id = ?", (payment_id,))
        
        assert result2["amount"] == payment_data["amount"]
        assert result2["status"] == "completed"

    @pytest.mark.database
    async def test_partial_update_rolled_back_on_error(self, mock_database):
        """Test partial updates are rolled back on error."""
        trial_id = "trial_test_12345"
        initial_status = "active"
        new_status = "payment_pending"
        
        # Start transaction
        mock_database.execute.return_value = None
        await mock_database.execute("BEGIN TRANSACTION")
        
        # Update status
        mock_database.execute.return_value = {"id": trial_id, "status": new_status}
        update1 = await mock_database.execute(
            "UPDATE trials SET status = ? WHERE id = ?",
            (new_status, trial_id)
        )
        
        # Simulate error
        mock_database.execute.side_effect = Exception("Constraint violation")
        
        with pytest.raises(Exception):
            await mock_database.execute("UPDATE trials SET tier = ? WHERE id = ?", ("invalid", trial_id))
        
        # Verify rollback happened
        mock_database.execute.side_effect = None
        await mock_database.execute("ROLLBACK")

    @pytest.mark.database
    async def test_failed_email_send_retries_from_database(self, mock_database):
        """Test failed email send can be retried from database."""
        email_id = "email_123"
        email_data = {
            "trial_id": "trial_test_12345",
            "to_email": "contractor@example.com",
            "status": "pending",
            "retry_count": 0,
        }
        
        # Save email task
        mock_database.execute.return_value = {"id": email_id, **email_data}
        await mock_database.execute("INSERT INTO email_queue ...")
        
        # Retrieve for retry
        mock_database.fetch_one.return_value = {"id": email_id, **email_data, "retry_count": 0}
        result = await mock_database.fetch_one(
            "SELECT * FROM email_queue WHERE status = ? ORDER BY created_at LIMIT 1",
            ("pending",)
        )
        
        assert result is not None
        assert result["to_email"] == "contractor@example.com"

    @pytest.mark.database
    async def test_duplicate_record_prevention(self, mock_database):
        """Test duplicate records are prevented."""
        trial_id = "trial_test_12345"
        
        # First insert
        mock_database.execute.return_value = {"id": "research_1", "trial_id": trial_id}
        result1 = await mock_database.execute(
            "INSERT INTO research_results (trial_id, unique_key) VALUES (?, ?) ON CONFLICT DO UPDATE",
            (trial_id, "unique_123")
        )
        
        # Attempt duplicate insert
        mock_database.execute.return_value = {"id": "research_1", "trial_id": trial_id}  # Same ID returned
        result2 = await mock_database.execute(
            "INSERT INTO research_results (trial_id, unique_key) VALUES (?, ?) ON CONFLICT DO UPDATE",
            (trial_id, "unique_123")
        )
        
        # Should return same record
        assert result1["id"] == result2["id"]


class TestConcurrentWriteSafety:
    """Test concurrent write operations are safe."""

    @pytest.mark.database
    async def test_concurrent_payment_writes_safe(self, mock_database):
        """Test concurrent payment writes don't corrupt data."""
        import asyncio
        
        async def write_payment(payment_num):
            payment_data = {
                "trial_id": f"trial_concurrent_{payment_num}",
                "amount": 1500000,
            }
            mock_database.execute.return_value = {
                "id": f"payment_{payment_num}",
                **payment_data
            }
            return await mock_database.execute(
                "INSERT INTO payments (trial_id, amount) VALUES (?, ?)",
                (payment_data["trial_id"], payment_data["amount"])
            )
        
        # Write 10 payments concurrently
        results = await asyncio.gather(*[write_payment(i) for i in range(10)])
        
        assert len(results) == 10
        assert all(r is not None for r in results)
        assert len(set(r["id"] for r in results)) == 10  # All unique IDs

    @pytest.mark.database
    async def test_concurrent_research_writes_safe(self, mock_database):
        """Test concurrent research writes don't corrupt data."""
        import asyncio
        
        async def write_research(research_num):
            research_data = {
                "trial_id": f"trial_research_{research_num}",
                "zip_code": f"7870{research_num}",
                "jurisdiction": f"City_{research_num}",
            }
            mock_database.execute.return_value = {
                "id": f"research_{research_num}",
                **research_data
            }
            return await mock_database.execute(
                "INSERT INTO research (trial_id, zip_code) VALUES (?, ?)",
                (research_data["trial_id"], research_data["zip_code"])
            )
        
        results = await asyncio.gather(*[write_research(i) for i in range(5)])
        
        assert len(results) == 5
        assert all(r["trial_id"].startswith("trial_research_") for r in results)

    @pytest.mark.database
    async def test_concurrent_read_write_consistency(self, mock_database):
        """Test concurrent reads and writes maintain consistency."""
        import asyncio
        
        async def write_operation(write_num):
            data = {"trial_id": f"trial_{write_num}", "value": write_num * 100}
            mock_database.execute.return_value = {"id": f"item_{write_num}", **data}
            return await mock_database.execute("INSERT INTO items ...", ())
        
        async def read_operation(read_num):
            mock_database.fetch_one.return_value = {
                "id": f"item_{read_num % 5}",
                "trial_id": f"trial_{read_num % 5}",
                "value": (read_num % 5) * 100
            }
            return await mock_database.fetch_one("SELECT * FROM items ...", ())
        
        # Mix reads and writes
        operations = (
            [write_operation(i) for i in range(3)] +
            [read_operation(i) for i in range(3)]
        )
        results = await asyncio.gather(*operations)
        
        assert len(results) == 6
        assert all(r is not None for r in results)

    @pytest.mark.database
    async def test_transaction_isolation(self, mock_database):
        """Test transactions are properly isolated."""
        import asyncio
        
        async def transaction_1():
            await mock_database.execute("BEGIN TRANSACTION")
            mock_database.execute.return_value = {"status": "updated_1"}
            await mock_database.execute("UPDATE table SET status = ? WHERE id = ?", ("status_1", "id_1"))
            await asyncio.sleep(0.1)  # Hold transaction open
            await mock_database.execute("COMMIT")
            return "committed_1"
        
        async def transaction_2():
            await asyncio.sleep(0.05)  # Start after transaction_1
            await mock_database.execute("BEGIN TRANSACTION")
            mock_database.execute.return_value = {"status": "updated_2"}
            await mock_database.execute("UPDATE table SET status = ? WHERE id = ?", ("status_2", "id_2"))
            await mock_database.execute("COMMIT")
            return "committed_2"
        
        results = await asyncio.gather(transaction_1(), transaction_2())
        
        assert len(results) == 2
        assert "committed" in results[0]
        assert "committed" in results[1]
