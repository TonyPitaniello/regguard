# Quick Start Guide - Text & Email Delivery Feature

## 🚀 5-Minute Setup

### 1. Configure Environment Variables

Add to `backend/.env`:

```bash
# Get these from Twilio Console
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_FROM_NUMBER=+1XXXXXXXXXX

# SendGrid should already be configured
SENDGRID_API_KEY=SG.XXXXXXXXXXXXXXXXXXXX
```

### 2. Install Python Package

```bash
pip install twilio
```

### 3. Run Database Migration

```bash
# With Supabase CLI:
supabase migration up

# Or manually with psql:
psql -U postgres -d your_database -f backend/migrations/010_result_deliveries.sql
```

### 4. Verify Installation

```bash
# Run tests
cd backend
pytest tests/test_sms_service.py tests/test_email_service.py tests/test_result_delivery_service.py -v
```

### 5. Start Dev Servers

```bash
# From repo root
npm run dev
```

Visit http://localhost:5173 and navigate to Results Page to test!

## 📱 Testing the Feature

### Via Frontend (Recommended)

1. Complete a research lookup to get to Results page
2. Click "📱 Text This Result" or "📧 Email This Result"
3. Enter phone/email in the modal
4. Click "Send" button
5. You should see success message or error

### Via API (Manual Testing)

```bash
curl -X POST http://localhost:8000/api/research/test-123/send-sms \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "5551234567"}'

# Response:
# {
#   "status": "sent",
#   "message_id": "SMxxxxxxxx...",
#   "phone": "+15551234567",
#   "delivery_id": "uuid..."
# }
```

## 🔧 Configuration Options

### Rate Limiting

Edit `backend/result_delivery_service.py`:

```python
self.SMS_RATE_LIMIT = 3      # Change from 3
self.EMAIL_RATE_LIMIT = 5    # Change from 5
```

### SMS Templates

Edit `backend/sms_service.py` → `_format_sms_message()` method

### Email Templates

Edit `backend/email_service.py` → `_build_result_html_email()` method

## 📚 Key Files

| File | Purpose |
|------|---------|
| `backend/sms_service.py` | Twilio SMS integration |
| `backend/result_delivery_service.py` | Orchestration & rate limiting |
| `backend/email_service.py` | SendGrid email enhancement |
| `frontend/src/components/ShareResultsModal.tsx` | Modal UI component |
| `backend/migrations/010_result_deliveries.sql` | Database schema |
| `SHARE_RESULTS_IMPLEMENTATION.md` | Full documentation |

## 🐛 Troubleshooting

### "SMS not sending"

Check:
1. Twilio credentials in `.env`
2. Twilio account has credits
3. Phone number is valid US format
4. Check logs for error details

### "Email not sending"

Check:
1. SendGrid API key in `.env`
2. Email is valid format
3. SendGrid account is active
4. Check logs for error details

### "Rate limit error"

This is expected! Users get:
> "Rate limit exceeded. Try again in 47 minutes."

Wait until the hour resets or increase limits in `result_delivery_service.py`

## 📊 Monitoring

### Database Queries

Check deliveries:
```sql
SELECT * FROM result_deliveries ORDER BY created_at DESC LIMIT 10;
```

Check rate limits:
```sql
SELECT * FROM delivery_rate_limits WHERE user_id = '...' ORDER BY hour_slot DESC;
```

### Logs

Look for:
- `✅ SMS sent successfully`
- `❌ Failed to send SMS`
- `SMS rate limit exceeded`

## 🎯 What's Included

✅ Fully working SMS delivery (Twilio)
✅ Fully working Email delivery (SendGrid/Resend)
✅ Rate limiting with countdown timers
✅ Database tracking for all deliveries
✅ Beautiful React modal component
✅ Real-time validation
✅ 40+ test cases
✅ Complete documentation
✅ Mock services for testing
✅ Professional templates

## 📖 Next Steps

1. ✅ **Setup**: Add Twilio credentials
2. ✅ **Migrate**: Run database migration
3. ✅ **Test**: Run test suite
4. ✅ **Verify**: Test SMS/Email from UI
5. ✅ **Deploy**: Push to production
6. ✅ **Monitor**: Watch logs for errors

## 💬 Questions?

See `SHARE_RESULTS_IMPLEMENTATION.md` for:
- Complete API documentation
- Advanced configuration
- Security notes
- Cost estimation
- Troubleshooting guide
