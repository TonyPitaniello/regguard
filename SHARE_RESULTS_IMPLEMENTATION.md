# RegGuard Share Results Feature

## Overview

The "Share Results" feature enables users to instantly deliver their research results via SMS (text message) or email. After completing a free trial research lookup, users can:

1. **Send via Text (SMS)**: Receive a formatted research summary on their phone using Twilio
2. **Send via Email**: Receive a professional HTML email with full research details using SendGrid/Resend
3. **Download PDF**: Save research results for offline access

## Features

### ✅ User Features

- **Instant Delivery**: Results sent immediately after user provides phone/email
- **Multiple Formats**: SMS for quick summaries, Email for detailed reports
- **Rate Limiting**: Prevents abuse (3 SMS/hour, 5 emails/hour per user)
- **Validation**: Real-time feedback on phone and email inputs
- **Success Confirmations**: Clear visual confirmation when results are sent
- **Error Handling**: User-friendly error messages and retry guidance

### ✅ Technical Features

- **Database Tracking**: All deliveries logged for audit/support
- **Rate Limiting Table**: Enforces per-user, per-hour limits
- **Service Flexibility**: Works with Twilio for SMS, SendGrid or Resend for Email
- **Mock Services**: Built-in mock services for development/testing
- **Professional Templates**: Pre-designed SMS and email templates
- **Error Resilience**: Graceful degradation if services unavailable

## Architecture

### Backend Structure

```
backend/
├── sms_service.py              # Twilio SMS service + validation
├── email_service.py            # Enhanced with send_research_result()
├── result_delivery_service.py  # Orchestration + rate limiting
├── main.py                     # API endpoints
├── migrations/
│   └── 010_result_deliveries.sql  # Database schema
└── tests/
    ├── test_sms_service.py
    ├── test_email_service.py
    └── test_result_delivery_service.py
```

### Frontend Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── ShareResultsModal.tsx    # Modal form component
│   └── pages/
│       └── ResultsPage.tsx          # Updated with share buttons
```

### Database Schema

```sql
-- result_deliveries: Tracks all SMS/email deliveries
CREATE TABLE result_deliveries (
  id UUID PRIMARY KEY,
  research_id UUID NOT NULL,
  user_id UUID NOT NULL REFERENCES profiles(id),
  delivery_method TEXT CHECK (IN 'sms', 'email'),
  destination TEXT,              -- phone or email
  status TEXT CHECK (IN 'pending', 'sent', 'failed'),
  service_message_id TEXT,        -- Twilio SID or SendGrid ID
  error_message TEXT,
  sent_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- delivery_rate_limits: Enforces per-user rate limiting
CREATE TABLE delivery_rate_limits (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES profiles(id),
  delivery_method TEXT CHECK (IN 'sms', 'email'),
  hour_slot TIMESTAMP NOT NULL,   -- Truncated to hour boundary
  count INT NOT NULL DEFAULT 1,
  UNIQUE(user_id, delivery_method, hour_slot)
);
```

## Setup Guide

### 1. Environment Configuration

Add to `.env.example` and `.env`:

```bash
# SMS Service (Twilio)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_FROM_NUMBER=+1XXXXXXXXXX

# Email Service (already configured)
SENDGRID_API_KEY=SG.XXXXXXXXXXXXXXXXXXXX
RESEND_API_KEY=re_XXXXXXXXXXXXXXXXXXXX
RESEND_FROM_EMAIL=noreply@regguardagent.com
```

### 2. Get Twilio Credentials

1. Sign up at [twilio.com](https://www.twilio.com)
2. Create a new project or use existing
3. Get **Account SID** and **Auth Token** from Console
4. Purchase or create a SMS-capable phone number
5. Add credentials to `.env`

### 3. Database Migration

Run migration to create tables:

```bash
# Using Supabase CLI
supabase migration up

# Or manually execute SQL:
psql -U postgres -d your_db -f backend/migrations/010_result_deliveries.sql
```

### 4. Install Dependencies

```bash
# Python (backend)
pip install twilio sendgrid

# Already included: httpx, fastapi, starlette
```

### 5. Test Services

```bash
# Run tests
cd backend
pytest tests/test_sms_service.py -v
pytest tests/test_email_service.py -v
pytest tests/test_result_delivery_service.py -v
```

## API Endpoints

### Send SMS

```http
POST /api/research/{research_id}/send-sms
Content-Type: application/json

{
  "phone_number": "+1-555-123-4567"
}
```

**Response (Success):**
```json
{
  "status": "sent",
  "message_id": "SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "phone": "+15551234567",
  "delivery_id": "uuid-here"
}
```

**Response (Error):**
```json
{
  "status": "failed",
  "error": "Invalid phone number: must be US format"
}
```

### Send Email

```http
POST /api/research/{research_id}/send-email
Content-Type: application/json

{
  "email_address": "user@example.com"
}
```

**Response (Success):**
```json
{
  "status": "sent",
  "email_id": "...",
  "email": "user@example.com",
  "delivery_id": "uuid-here"
}
```

**Response (Error - Rate Limited):**
```json
{
  "status": "failed",
  "error": "Rate limit exceeded. Try again in 47 minutes."
}
```

## SMS Template

The SMS message is formatted to fit in ~160-320 characters:

```
RegGuard: Arlington, TX 75001
⚠️ 3 High Risks
💰 $125,000
⏱️ 45 days

View full report: regguard.io
```

**Customization:** Edit `sms_service.py::_format_sms_message()` to change template.

## Email Template

Professional HTML email with:

- **Header**: RegGuard branding + project location
- **Risk Summary**: Total risks, high-risk count, timeline, estimated cost
- **Action Items**: Number of punch list items with summary
- **CTA Button**: Link to view full research report
- **Footer**: Contact info + unsubscribe

**Customization:** Edit `email_service.py::_build_result_html_email()` to change template.

## Rate Limiting

### Limits

- **SMS**: 3 messages per user per hour
- **Email**: 5 messages per user per hour

### Implementation

1. Check current hour slot count in `delivery_rate_limits` table
2. If count >= limit, return error with reset time
3. On successful send, increment counter
4. Counters reset at top of each hour

### Error Message

```
Rate limit exceeded. Try again in 47 minutes.
```

User sees this with helpful countdown timer.

## Frontend Usage

### Import Modal

```tsx
import ShareResultsModal from '../components/ShareResultsModal';

function MyComponent() {
  const [shareModal, setShareModal] = useState({ isOpen: false, method: 'sms' });

  return (
    <>
      <button onClick={() => setShareModal({ isOpen: true, method: 'sms' })}>
        📱 Text This Result
      </button>
      
      <ShareResultsModal
        isOpen={shareModal.isOpen}
        onClose={() => setShareModal({ isOpen: false, method: 'sms' })}
        deliveryMethod={shareModal.method}
        researchId="research-123"
        onSuccess={(result) => console.log('Sent:', result)}
      />
    </>
  );
}
```

### Modal Features

- **Real-time Validation**: Feedback as user types
- **Loading State**: Shows spinner during send
- **Success State**: Auto-close after 3 seconds
- **Error Display**: Shows error messages with retry logic
- **Rate Limit Handling**: Shows countdown timer

## Testing

### Run All Tests

```bash
cd backend
pytest tests/test_sms_service.py tests/test_email_service.py tests/test_result_delivery_service.py -v
```

### Test Coverage

- **Phone Validation**: 10-digit, 11-digit, E.164, formatted, invalid formats
- **Email Validation**: Various formats, invalid cases
- **SMS Formatting**: Message structure, character limits, truncation
- **Rate Limiting**: Under limit, at limit, multiple increments
- **Delivery Tracking**: SMS sent, email failed, error logging
- **End-to-End**: Successful SMS, successful email, validation errors

### Mock Services

The project includes mock services for testing without real API calls:

```python
from sms_service import MockSMSService
from result_delivery_service import ResultDeliveryService

async def test_flow():
    service = ResultDeliveryService()
    result = await service.send_sms(
        phone_number="5551234567",
        research_data={...},
        user_id="user-123"
    )
    assert result["status"] == "sent"
```

## Troubleshooting

### SMS Not Sending

**Check:**
1. Twilio credentials in `.env` file
2. Twilio account has available SMS credits
3. Phone number is valid US format
4. Not exceeding rate limit (3 per hour)
5. `twilio` package installed: `pip install twilio`

**Logs:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Email Not Sending

**Check:**
1. SendGrid or Resend API key in `.env`
2. Email address is valid
3. Not exceeding rate limit (5 per hour)
4. `sendgrid` or `resend` package installed

**Logs:**
Look for `SendGrid error:` or `Resend error:` in logs

### Rate Limit Errors

**Message:** "Rate limit exceeded. Try again in X minutes."

**Solutions:**
1. User should wait for the specified time
2. Each hour resets the counter
3. Limits are per-user, so other users not affected

## Cost Estimation

### SMS (Twilio)

- **Per Message**: ~$0.01
- **Typical Volume**: 10-100/day
- **Monthly (100/day)**: ~$30

### Email (SendGrid/Resend)

- **SendGrid Free Tier**: 100 emails/day, then $0.10+ per 1000
- **Resend Free Tier**: First 100 emails/day, then pay-as-you-go
- **Typical Volume**: Low cost with free tier

## Security Considerations

### PII Handling

- ✅ Phone numbers NOT stored long-term (only in delivery logs with hash)
- ✅ Email addresses NOT stored long-term (transient delivery only)
- ✅ All data sent over HTTPS
- ✅ Rate limiting prevents automated scraping

### Access Control

- ✅ Requires user authentication (via existing auth system)
- ✅ Users can only send their own research results
- ✅ API checks user context before allowing send

### Data Protection

- ✅ All deliveries logged for compliance
- ✅ Failed attempts tracked with error messages
- ✅ No retry loops (one send per request)

## Future Enhancements

### Short-term

- [ ] Bulk send (admin feature to email multiple users)
- [ ] SMS to multiple recipients
- [ ] Custom email templates (user branding)
- [ ] Delivery analytics dashboard

### Long-term

- [ ] WhatsApp integration
- [ ] Slack notifications
- [ ] PDF generation option
- [ ] Scheduled delivery
- [ ] Webhook notifications for delivery status

## Support

For issues or questions:

1. Check logs: `backend/logs/` (if configured)
2. Run tests: `pytest tests/test_*.py -v`
3. Contact: support@regguardagent.com

## Version History

- **v1.0** (Jul 2026): Initial release with SMS and Email support
  - Twilio SMS integration
  - SendGrid/Resend email support
  - Rate limiting per user/hour
  - Professional templates
  - Database tracking
  - React modal component
  - Comprehensive tests
