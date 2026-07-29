/**
 * PremiumCheckoutPage.tsx
 * Phase 2 Week 2: Premium tier checkout with Stripe Elements
 * 
 * Features:
 * - Stripe Elements integration
 * - Professional checkout flow
 * - Payment form validation
 * - Success/error handling
 * - Loading states
 */

import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { AlertCircle, CheckCircle, Loader } from 'lucide-react';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { backendUrl } from '../env';

// Initialize Stripe
const stripePromise = loadStripe(
  import.meta.env.VITE_STRIPE_PUBLIC_KEY || 'pk_test_placeholder'
);

// ============================================================================
// TIER INFORMATION
// ============================================================================

const TIERS = {
  premium: {
    name: 'Premium',
    price: '$15,000',
    price_cents: 1500000,
    description: 'Complete site diligence package',
    features: [
      '📋 Research Memo PDF (environmental findings)',
      '✓ Complete Punch List (all action items)',
      '📄 State-Specific Permit Packages',
      '⏰ Same-day delivery',
      '📥 Download links valid 30 days',
      '📧 Email delivery with attachments',
    ],
    delivery_time: 'Within 1 hour',
    color: 'from-blue-600 to-purple-600',
  },
  enterprise: {
    name: 'Enterprise',
    price: '$60,000/year',
    price_cents: 6000000,
    description: 'Premium + annual monitoring',
    features: [
      'Everything in Premium PLUS:',
      '📊 Annual monitoring & updates',
      '📄 2 additional reports per year',
      '👥 Dedicated support',
      '🔄 White-label options',
      '🤝 Custom integrations',
    ],
    delivery_time: 'Within 1 hour',
    color: 'from-indigo-600 to-blue-600',
  },
};

// ============================================================================
// MAIN CHECKOUT PAGE
// ============================================================================

export default function PremiumCheckoutPage() {
  const navigate = useNavigate();
  const { tier = 'premium' } = useParams();
  const [step, setStep] = useState('selection'); // selection, checkout, success, error
  const [selectedTier, setSelectedTier] = useState(tier);
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleTierSelect = (tierKey: string) => {
    setSelectedTier(tierKey);
    setStep('checkout');
  };

  const handleBack = () => {
    if (step === 'checkout') {
      setStep('selection');
      setError('');
    } else if (step === 'success' || step === 'error') {
      navigate('/');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="bg-slate-900/80 backdrop-blur border-b border-purple-500/20 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <h1 className="text-white font-black text-xl">RegGuard Premium</h1>
          {step !== 'selection' && (
            <button
              onClick={handleBack}
              className="text-gray-400 hover:text-white transition"
            >
              ← Back
            </button>
          )}
        </div>
      </header>

      {/* Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {step === 'selection' && (
          <TierSelectionStep onSelect={handleTierSelect} />
        )}
        {step === 'checkout' && (
          <CheckoutFormStep
            tier={selectedTier}
            onBack={handleBack}
            onSuccess={() => setStep('success')}
            onError={(err) => {
              setError(err);
              setStep('error');
            }}
          />
        )}
        {step === 'success' && <SuccessStep tier={selectedTier} />}
        {step === 'error' && (
          <ErrorStep error={error} onRetry={() => setStep('checkout')} />
        )}
      </main>
    </div>
  );
}

// ============================================================================
// TIER SELECTION STEP
// ============================================================================

function TierSelectionStep({ onSelect }: { onSelect: (tier: string) => void }) {
  return (
    <div>
      <h2 className="text-3xl font-black text-white mb-2">Choose Your Plan</h2>
      <p className="text-gray-400 mb-12">
        Select the tier that best fits your needs
      </p>

      <div className="grid md:grid-cols-2 gap-8">
        {Object.entries(TIERS).map(([key, tier]) => (
          <div
            key={key}
            className={`bg-gradient-to-br ${tier.color} rounded-lg p-1 hover:scale-105 transition transform`}
          >
            <div className="bg-slate-900 rounded-lg p-8 h-full">
              <h3 className="text-2xl font-bold text-white mb-2">{tier.name}</h3>
              <p className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400 mb-4">
                {tier.price}
              </p>
              <p className="text-gray-400 mb-6">{tier.description}</p>

              <ul className="space-y-3 mb-8">
                {tier.features.map((feature, idx) => (
                  <li key={idx} className="text-gray-300 flex items-start">
                    <span className="mr-3 text-green-400">✓</span>
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>

              <div className="text-sm text-gray-500 mb-6">
                📦 Delivery: {tier.delivery_time}
              </div>

              <button
                onClick={() => onSelect(key)}
                className={`w-full px-6 py-3 bg-gradient-to-r ${tier.color} text-white font-bold rounded-lg hover:shadow-lg hover:shadow-purple-500/50 transition`}
              >
                Select {tier.name}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ============================================================================
// CHECKOUT FORM STEP
// ============================================================================

function CheckoutFormStep({
  tier,
  onBack,
  onSuccess,
  onError,
}: {
  tier: string;
  onBack: () => void;
  onSuccess: () => void;
  onError: (error: string) => void;
}) {
  const tierInfo = TIERS[tier as keyof typeof TIERS];

  return (
    <div>
      <h2 className="text-3xl font-black text-white mb-2">Complete Your Order</h2>
      <p className="text-gray-400 mb-12">
        {tierInfo.name} Plan - {tierInfo.price}
      </p>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Order Summary */}
        <div className="lg:col-span-1">
          <div className="bg-slate-800 border border-purple-500/20 rounded-lg p-6 sticky top-24">
            <h3 className="text-lg font-bold text-white mb-6">Order Summary</h3>

            <div className="space-y-4 mb-6">
              <div className="flex justify-between">
                <span className="text-gray-400">{tierInfo.name} Plan</span>
                <span className="text-white font-bold">{tierInfo.price}</span>
              </div>
              <div className="border-t border-gray-700 pt-4 flex justify-between">
                <span className="text-white font-bold">Total</span>
                <span className="text-2xl font-black text-purple-400">
                  {tierInfo.price}
                </span>
              </div>
            </div>

            <div className="bg-purple-500/10 border border-purple-500/20 rounded-lg p-4 text-sm text-purple-200">
              <p>✓ Includes all benefits</p>
              <p>✓ Same-day delivery</p>
              <p>✓ 30-day access</p>
            </div>
          </div>
        </div>

        {/* Payment Form */}
        <div className="lg:col-span-2">
          <Elements stripe={stripePromise}>
            <PaymentForm
              tier={tier}
              tierPrice={tierInfo.price}
              onSuccess={onSuccess}
              onError={onError}
            />
          </Elements>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// PAYMENT FORM (with Stripe Elements)
// ============================================================================

function PaymentForm({
  tier,
  tierPrice,
  onSuccess,
  onError,
}: {
  tier: string;
  tierPrice: string;
  onSuccess: () => void;
  onError: (error: string) => void;
}) {
  const stripe = useStripe();
  const elements = useElements();
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [cardError, setCardError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setCardError('');

    if (!stripe || !elements) {
      onError('Stripe not loaded');
      setLoading(false);
      return;
    }

    try {
      // 1. Get trial_id from session/URL
      const trialId = sessionStorage.getItem('trialId') || 'unknown';

      // 2. Create checkout session
      const response = await fetch(backendUrl('/checkout'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            trial_id: trialId,
            tier,
          }),
        }
      );

      if (!response.ok) throw new Error('Checkout creation failed');

      const { checkout_url } = await response.json();

      // 3. Redirect to Stripe checkout
      if (checkout_url) {
        window.location.href = checkout_url;
      } else {
        throw new Error('No checkout URL received');
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Payment failed';
      setCardError(message);
      onError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Email */}
      <div>
        <label htmlFor="email" className="block text-white font-bold mb-2">
          Email Address *
        </label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@company.com"
          required
          className="w-full px-4 py-3 bg-slate-800 border border-purple-500/30 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
        />
      </div>

      {/* Name */}
      <div>
        <label htmlFor="name" className="block text-white font-bold mb-2">
          Full Name *
        </label>
        <input
          id="name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="John Doe"
          required
          className="w-full px-4 py-3 bg-slate-800 border border-purple-500/30 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
        />
      </div>

      {/* Card Element */}
      <div>
        <label className="block text-white font-bold mb-2">Payment Details *</label>
        <div className="p-4 bg-slate-800 border border-purple-500/30 rounded-lg">
          <CardElement
            options={{
              style: {
                base: {
                  fontSize: '16px',
                  color: '#fff',
                  '::placeholder': {
                    color: '#9CA3AF',
                  },
                },
                invalid: {
                  color: '#EF4444',
                },
              },
            }}
          />
        </div>
      </div>

      {/* Error Message */}
      {cardError && (
        <div className="flex gap-3 p-4 bg-red-500/20 border border-red-500/30 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
          <p className="text-red-200 text-sm">{cardError}</p>
        </div>
      )}

      {/* Disclaimer */}
      <div className="bg-slate-800/50 border border-purple-500/10 rounded-lg p-4 text-sm text-gray-400">
        <p>
          By clicking "Complete Purchase", you agree to our Terms of Service.
          Your payment information is secure and processed through Stripe.
        </p>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={loading || !stripe || !elements}
        className="w-full px-6 py-4 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-bold text-lg rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {loading && <Loader className="w-5 h-5 animate-spin" />}
        {loading ? 'Processing...' : `Complete Purchase - ${tierPrice}`}
      </button>
    </form>
  );
}

// ============================================================================
// SUCCESS STEP
// ============================================================================

function SuccessStep({ tier }: { tier: string }) {
  const tierInfo = TIERS[tier as keyof typeof TIERS];
  const navigate = useNavigate();

  return (
    <div className="text-center">
      <CheckCircle className="w-16 h-16 text-green-400 mx-auto mb-6" />
      <h2 className="text-3xl font-black text-white mb-4">Payment Successful!</h2>
      <p className="text-gray-300 mb-8 max-w-2xl mx-auto">
        Thank you for your purchase! Your {tierInfo.name} package has been processed.
      </p>

      <div className="bg-slate-800 border border-purple-500/20 rounded-lg p-8 max-w-2xl mx-auto mb-12">
        <h3 className="text-lg font-bold text-white mb-6">What's Next?</h3>
        <ul className="space-y-4 text-left">
          <li className="flex items-start gap-3">
            <CheckCircle className="w-5 h-5 text-green-400 mt-1 flex-shrink-0" />
            <span className="text-gray-300">
              <strong>PDFs are being generated</strong> - You'll receive email download links within 1 hour
            </span>
          </li>
          <li className="flex items-start gap-3">
            <CheckCircle className="w-5 h-5 text-green-400 mt-1 flex-shrink-0" />
            <span className="text-gray-300">
              <strong>Check your inbox</strong> - Including spam folder for email from support@regguardagent.com
            </span>
          </li>
          <li className="flex items-start gap-3">
            <CheckCircle className="w-5 h-5 text-green-400 mt-1 flex-shrink-0" />
            <span className="text-gray-300">
              <strong>Download for 30 days</strong> - Links will expire in 30 days. Download immediately if needed.
            </span>
          </li>
        </ul>
      </div>

      <button
        onClick={() => navigate('/orders')}
        className="px-8 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-bold rounded-lg hover:shadow-lg transition"
      >
        View My Orders
      </button>
    </div>
  );
}

// ============================================================================
// ERROR STEP
// ============================================================================

function ErrorStep({ error, onRetry }: { error: string; onRetry: () => void }) {
  return (
    <div className="text-center">
      <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-6" />
      <h2 className="text-3xl font-black text-white mb-4">Payment Failed</h2>
      <p className="text-gray-300 mb-8 max-w-2xl mx-auto">
        {error}
      </p>

      <button
        onClick={onRetry}
        className="px-8 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-bold rounded-lg hover:shadow-lg transition"
      >
        Try Again
      </button>
    </div>
  );
}
