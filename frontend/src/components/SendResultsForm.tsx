/**
 * Dual phone + email send form for research results.
 * Works with free-trial summaries (no DB research_id) via /research/send-sms|send-email.
 */

import { useState } from 'react';
import { AlertCircle, CheckCircle, Loader, Mail, Phone } from 'lucide-react';
import { backendUrl } from '../env';

export interface ResultsSummaryPayload {
  zip?: string;
  city?: string;
  state?: string;
  risk_level?: string;
  timeline?: string;
  cost?: number;
  address?: string;
}

interface SendResultsFormProps {
  researchId?: string | null;
  summary: ResultsSummaryPayload;
  userId?: string;
  defaultEmail?: string;
  compact?: boolean;
}

export default function SendResultsForm({
  researchId,
  summary,
  userId,
  defaultEmail = '',
  compact = false,
}: SendResultsFormProps) {
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState(defaultEmail);
  const [loadingSms, setLoadingSms] = useState(false);
  const [loadingEmail, setLoadingEmail] = useState(false);
  const [smsSuccess, setSmsSuccess] = useState('');
  const [emailSuccess, setEmailSuccess] = useState('');
  const [error, setError] = useState('');

  const validatePhone = (value: string): boolean => {
    const digits = value.replace(/\D/g, '');
    return digits.length === 10 || digits.length === 11;
  };

  const validateEmail = (value: string): boolean =>
    /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(value);

  const formatPhoneDisplay = (value: string): string => {
    const digits = value.replace(/\D/g, '').slice(-10);
    return `+1-${digits.slice(0, 3)}-${digits.slice(3, 6)}-${digits.slice(6)}`;
  };

  const buildBody = (extra: Record<string, string>) => ({
    ...extra,
    summary,
    ...(userId ? { user_id: userId } : {}),
    ...(researchId ? { research_id: researchId } : {}),
  });

  const handleSendSms = async () => {
    setError('');
    setSmsSuccess('');
    if (!phone || !validatePhone(phone)) {
      setError('Please enter a valid US phone number (10 digits)');
      return;
    }
    setLoadingSms(true);
    try {
      const path = researchId
        ? `/research/${researchId}/send-sms`
        : '/research/send-sms';
      const response = await fetch(backendUrl(path), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(buildBody({ phone_number: phone })),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail || 'Failed to send SMS');
        return;
      }
      setSmsSuccess(`Sent to ${formatPhoneDisplay(phone)}`);
      setPhone('');
    } catch (err) {
      console.error(err);
      setError('Network error. Please try again.');
    } finally {
      setLoadingSms(false);
    }
  };

  const handleSendEmail = async () => {
    setError('');
    setEmailSuccess('');
    if (!email || !validateEmail(email)) {
      setError('Please enter a valid email address');
      return;
    }
    setLoadingEmail(true);
    try {
      const path = researchId
        ? `/research/${researchId}/send-email`
        : '/research/send-email';
      const response = await fetch(backendUrl(path), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(
          buildBody({ email: email, email_address: email })
        ),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail || 'Failed to send email');
        return;
      }
      setEmailSuccess(`Sent to ${email}`);
    } catch (err) {
      console.error(err);
      setError('Network error. Please try again.');
    } finally {
      setLoadingEmail(false);
    }
  };

  return (
    <div className={compact ? 'space-y-4' : 'space-y-5'}>
      <h3 className="text-lg font-bold text-white">Send these results</h3>
      <p className="text-sm text-gray-400">
        Text or email a summary to yourself — both options are available.
      </p>

      {error && (
        <div className="flex gap-2 p-3 bg-red-500/20 border border-red-500/30 rounded-lg">
          <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
          <p className="text-red-200 text-sm">{error}</p>
        </div>
      )}

      {(smsSuccess || emailSuccess) && (
        <div className="space-y-2">
          {smsSuccess && (
            <div className="flex gap-2 p-3 bg-emerald-500/20 border border-emerald-500/30 rounded-lg">
              <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
              <p className="text-emerald-200 text-sm">{smsSuccess}</p>
            </div>
          )}
          {emailSuccess && (
            <div className="flex gap-2 p-3 bg-emerald-500/20 border border-emerald-500/30 rounded-lg">
              <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
              <p className="text-emerald-200 text-sm">{emailSuccess}</p>
            </div>
          )}
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <label htmlFor="send-phone" className="block text-sm font-semibold text-gray-300">
            Phone number
          </label>
          <div className="flex gap-2">
            <input
              id="send-phone"
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+1 (555) 123-4567"
              disabled={loadingSms}
              className="flex-1 px-3 py-2.5 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500"
            />
            <button
              type="button"
              onClick={handleSendSms}
              disabled={loadingSms}
              className="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-lg transition disabled:opacity-50 flex items-center gap-2 whitespace-nowrap"
            >
              {loadingSms ? <Loader className="w-4 h-4 animate-spin" /> : <Phone className="w-4 h-4" />}
              Text me
            </button>
          </div>
        </div>

        <div className="space-y-2">
          <label htmlFor="send-email" className="block text-sm font-semibold text-gray-300">
            Email
          </label>
          <div className="flex gap-2">
            <input
              id="send-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
              disabled={loadingEmail}
              className="flex-1 px-3 py-2.5 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
            <button
              type="button"
              onClick={handleSendEmail}
              disabled={loadingEmail}
              className="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition disabled:opacity-50 flex items-center gap-2 whitespace-nowrap"
            >
              {loadingEmail ? <Loader className="w-4 h-4 animate-spin" /> : <Mail className="w-4 h-4" />}
              Email me
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
