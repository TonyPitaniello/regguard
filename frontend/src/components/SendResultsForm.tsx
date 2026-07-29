/**
 * Dual phone + email send form for research results.
 * Uses API when available; optional native sms:/mailto: only via explicit secondary buttons.
 */

import { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, Loader, Mail, Phone, MessageSquare } from 'lucide-react';
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
  defaultPhone?: string;
  compact?: boolean;
}

function buildTextBody(summary: ResultsSummaryPayload): string {
  const lines = [
    'RegGuard Site Diligence Summary',
    summary.address ? `Site: ${summary.address}` : '',
    [summary.city, summary.state, summary.zip].filter(Boolean).join(', '),
    summary.risk_level ? `Risk: ${summary.risk_level}` : '',
    summary.timeline ? `Timeline: ${summary.timeline}` : '',
    summary.cost != null ? `Est. cost: $${Number(summary.cost).toLocaleString()}` : '',
    '',
    'View full app: https://app.regguardagent.com/',
  ].filter(Boolean);
  return lines.join('\n');
}

export default function SendResultsForm({
  researchId,
  summary,
  userId,
  defaultEmail = '',
  defaultPhone = '',
}: SendResultsFormProps) {
  const [phone, setPhone] = useState(defaultPhone);
  const [email, setEmail] = useState(defaultEmail);
  const [loadingSms, setLoadingSms] = useState(false);
  const [loadingEmail, setLoadingEmail] = useState(false);
  const [smsSuccess, setSmsSuccess] = useState('');
  const [emailSuccess, setEmailSuccess] = useState('');
  const [error, setError] = useState('');
  const [showSmsNativeFallback, setShowSmsNativeFallback] = useState(false);
  const [showEmailNativeFallback, setShowEmailNativeFallback] = useState(false);

  // Keep defaults in sync when voice fill lands after mount
  useEffect(() => {
    if (defaultEmail) setEmail(defaultEmail);
  }, [defaultEmail]);
  useEffect(() => {
    if (defaultPhone) setPhone(defaultPhone);
  }, [defaultPhone]);

  const validatePhone = (value: string): boolean => {
    const digits = value.replace(/\D/g, '');
    return digits.length === 10 || digits.length === 11;
  };

  const validateEmail = (value: string): boolean =>
    /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(value);

  const digitsOnly = (value: string) => value.replace(/\D/g, '').slice(-10);

  const formatPhoneDisplay = (value: string): string => {
    const digits = digitsOnly(value);
    return `+1-${digits.slice(0, 3)}-${digits.slice(3, 6)}-${digits.slice(6)}`;
  };

  const buildBody = (extra: Record<string, string>) => ({
    ...extra,
    summary,
    ...(userId ? { user_id: userId } : {}),
    ...(researchId ? { research_id: researchId } : {}),
  });

  const openNativeSms = (phoneValue: string) => {
    const digits = digitsOnly(phoneValue);
    const body = encodeURIComponent(buildTextBody(summary));
    window.location.href = `sms:+1${digits}?&body=${body}`;
  };

  const openNativeEmail = (emailValue: string) => {
    const subject = encodeURIComponent('RegGuard Site Diligence Results');
    const body = encodeURIComponent(buildTextBody(summary));
    window.location.href = `mailto:${emailValue}?subject=${subject}&body=${body}`;
  };

  const handleSendSms = async () => {
    setError('');
    setSmsSuccess('');
    setShowSmsNativeFallback(false);
    if (!phone || !validatePhone(phone)) {
      setError('Please enter a valid US phone number (10 digits)');
      return;
    }
    setLoadingSms(true);
    try {
      const path = researchId ? `/research/${researchId}/send-sms` : '/research/send-sms';
      const response = await fetch(backendUrl(path), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(buildBody({ phone_number: phone })),
      });
      if (response.status === 429) {
        let detail = 'Too many texts — try again in a few minutes.';
        try {
          const errBody = await response.json();
          if (errBody?.detail) detail = String(errBody.detail);
        } catch {
          /* ignore */
        }
        setError(detail);
        return;
      }
      if (response.ok) {
        setSmsSuccess(`Text sent to ${formatPhoneDisplay(phone)}`);
        setPhone('');
        return;
      }
      setError(
        'Text could not be sent (Twilio may be offline). Use “Open in Messages” below, or copy share text.',
      );
      setShowSmsNativeFallback(true);
    } catch {
      setError(
        'Text could not be sent (Twilio may be offline). Use “Open in Messages” below, or copy share text.',
      );
      setShowSmsNativeFallback(true);
    } finally {
      setLoadingSms(false);
    }
  };

  const handleSendEmail = async () => {
    setError('');
    setEmailSuccess('');
    setShowEmailNativeFallback(false);
    if (!email || !validateEmail(email)) {
      setError('Please enter a valid email address');
      return;
    }
    setLoadingEmail(true);
    try {
      const path = researchId ? `/research/${researchId}/send-email` : '/research/send-email';
      const response = await fetch(backendUrl(path), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(buildBody({ email, email_address: email })),
      });
      if (response.status === 429) {
        let detail = 'Too many emails — try again in a few minutes.';
        try {
          const errBody = await response.json();
          if (errBody?.detail) detail = String(errBody.detail);
        } catch {
          /* ignore */
        }
        setError(detail);
        return;
      }
      if (response.ok) {
        setEmailSuccess(`Email sent to ${email}`);
        return;
      }
      setError(
        'Email could not be sent. Use “Open email app” below, or copy share text.',
      );
      setShowEmailNativeFallback(true);
    } catch {
      setError(
        'Email could not be sent. Use “Open email app” below, or copy share text.',
      );
      setShowEmailNativeFallback(true);
    } finally {
      setLoadingEmail(false);
    }
  };

  return (
    <div className="space-y-4 rounded-xl border-2 border-emerald-500/40 bg-emerald-500/10 p-4 sm:p-5">
      <div className="flex items-center gap-2">
        <MessageSquare className="w-5 h-5 text-emerald-400" />
        <h3 className="text-lg font-black text-white">Text or email these results</h3>
      </div>
      <p className="text-sm text-gray-300">
        Enter a phone number to text a summary, or an email — both work from this window.
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

      <div className="space-y-2 rounded-lg border border-emerald-500/50 bg-slate-900/60 p-4">
        <label htmlFor="send-phone" className="flex items-center gap-2 text-base font-bold text-emerald-300">
          <Phone className="w-4 h-4" />
          Text results (SMS)
        </label>
        <div className="flex flex-col sm:flex-row gap-2">
          <input
            id="send-phone"
            type="tel"
            inputMode="tel"
            autoComplete="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="(555) 123-4567"
            disabled={loadingSms}
            className="flex-1 px-4 py-3 bg-slate-800 border border-emerald-500/40 rounded-lg text-white text-base placeholder-gray-500 focus:outline-none focus:border-emerald-400"
          />
          <button
            type="button"
            onClick={handleSendSms}
            disabled={loadingSms}
            className="px-6 py-3 bg-emerald-500 hover:bg-emerald-400 text-slate-900 font-black rounded-lg transition disabled:opacity-50 flex items-center justify-center gap-2 whitespace-nowrap text-base"
          >
            {loadingSms ? <Loader className="w-5 h-5 animate-spin" /> : <Phone className="w-5 h-5" />}
            Text me
          </button>
        </div>
        {showSmsNativeFallback && phone && validatePhone(phone) && (
          <button
            type="button"
            onClick={() => openNativeSms(phone)}
            className="w-full sm:w-auto px-4 py-2 text-sm font-semibold text-emerald-300 border border-emerald-500/40 rounded-lg hover:bg-emerald-500/10 transition"
          >
            Open in Messages
          </button>
        )}
      </div>

      <div className="space-y-2 rounded-lg border border-blue-500/40 bg-slate-900/60 p-4">
        <label htmlFor="send-email" className="flex items-center gap-2 text-base font-bold text-blue-300">
          <Mail className="w-4 h-4" />
          Email results
        </label>
        <div className="flex flex-col sm:flex-row gap-2">
          <input
            id="send-email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@company.com"
            disabled={loadingEmail}
            className="flex-1 px-4 py-3 bg-slate-800 border border-blue-500/40 rounded-lg text-white text-base placeholder-gray-500 focus:outline-none focus:border-blue-400"
          />
          <button
            type="button"
            onClick={handleSendEmail}
            disabled={loadingEmail}
            className="px-6 py-3 bg-blue-500 hover:bg-blue-400 text-white font-black rounded-lg transition disabled:opacity-50 flex items-center justify-center gap-2 whitespace-nowrap text-base"
          >
            {loadingEmail ? <Loader className="w-5 h-5 animate-spin" /> : <Mail className="w-5 h-5" />}
            Email me
          </button>
        </div>
        {showEmailNativeFallback && email && validateEmail(email) && (
          <button
            type="button"
            onClick={() => openNativeEmail(email)}
            className="w-full sm:w-auto px-4 py-2 text-sm font-semibold text-blue-300 border border-blue-500/40 rounded-lg hover:bg-blue-500/10 transition"
          >
            Open email app
          </button>
        )}
      </div>
    </div>
  );
}
