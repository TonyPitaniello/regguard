/**
 * OrdersPage.tsx
 * Phase 2 Week 2: Order history and PDF download portal
 * 
 * Shows user's orders and provides PDF download links
 */

import React, { useState, useEffect } from 'react';
import { Download, Clock, CheckCircle, AlertCircle } from 'lucide-react';

interface PDF {
  type: 'research_memo' | 'punch_list' | 'permits';
  name: string;
  size: string;
  url: string;
  icon: string;
}

interface Order {
  order_id: string;
  trial_id: string;
  tier: string;
  status: string;
  created_at: string;
  amount: number;
  pdfs: PDF[];
  expires_at: string;
}

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const userEmail = sessionStorage.getItem('userEmail') || '';

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `${import.meta.env.VITE_BACKEND_ORIGIN}/orders?email=${userEmail}`
      );

      if (!response.ok) throw new Error('Failed to fetch orders');

      const data = await response.json();
      setOrders(data.orders || []);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load orders';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const downloadPDF = (pdf: PDF) => {
    // Open PDF in new tab (browser handles download)
    window.open(pdf.url, '_blank');
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const getDaysRemaining = (expiresAt: string) => {
    const now = new Date();
    const expiry = new Date(expiresAt);
    const days = Math.ceil((expiry.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    return Math.max(0, days);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p className="text-gray-300">Loading your orders...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="bg-slate-900/80 backdrop-blur border-b border-purple-500/20 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-black text-white">My Orders</h1>
          <p className="text-gray-400 mt-1">{userEmail}</p>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {error && (
          <div className="flex gap-3 p-4 bg-red-500/20 border border-red-500/30 rounded-lg mb-8">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <p className="text-red-200">{error}</p>
          </div>
        )}

        {orders.length === 0 ? (
          <div className="text-center py-12">
            <AlertCircle className="w-12 h-12 text-gray-500 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-white mb-2">No Orders Yet</h2>
            <p className="text-gray-400 mb-6">
              You haven't purchased any plans yet.
            </p>
            <a
              href="/free-trial"
              className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-bold rounded-lg hover:shadow-lg transition inline-block"
            >
              Start Free Trial
            </a>
          </div>
        ) : (
          <div className="space-y-6">
            {orders.map((order) => (
              <OrderCard
                key={order.order_id}
                order={order}
                onDownload={downloadPDF}
                formatDate={formatDate}
                getDaysRemaining={getDaysRemaining}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

// ============================================================================
// ORDER CARD COMPONENT
// ============================================================================

function OrderCard({
  order,
  onDownload,
  formatDate,
  getDaysRemaining,
}: {
  order: Order;
  onDownload: (pdf: PDF) => void;
  formatDate: (date: string) => string;
  getDaysRemaining: (date: string) => number;
}) {
  const daysRemaining = getDaysRemaining(order.expires_at);
  const tierColors = {
    free: 'from-gray-500 to-slate-500',
    premium: 'from-blue-600 to-purple-600',
    enterprise: 'from-indigo-600 to-purple-600',
  };

  const tierColor = tierColors[order.tier as keyof typeof tierColors] || tierColors.premium;

  return (
    <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-purple-500/20 rounded-lg overflow-hidden hover:border-purple-500/40 transition">
      {/* Header */}
      <div className={`bg-gradient-to-r ${tierColor} p-6`}>
        <div className="flex justify-between items-start">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-2xl font-bold text-white">
                {order.tier.toUpperCase()} Plan
              </h2>
              <span
                className={`px-3 py-1 rounded text-sm font-semibold ${
                  order.status === 'completed'
                    ? 'bg-green-500/20 text-green-400'
                    : 'bg-yellow-500/20 text-yellow-400'
                }`}
              >
                {order.status === 'completed' ? '✓ Completed' : 'Pending'}
              </span>
            </div>
            <p className="text-sm text-gray-200">
              Order #{order.order_id.slice(0, 8)}
            </p>
          </div>
          <div className="text-right">
            <p className="text-3xl font-black text-white">${(order.amount / 100).toLocaleString()}</p>
            <p className="text-sm text-gray-300">Purchased {formatDate(order.created_at)}</p>
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="p-6">
        <div className="grid md:grid-cols-2 gap-6 mb-6">
          {/* Order Info */}
          <div>
            <h3 className="text-sm font-bold text-gray-400 uppercase mb-4">
              Order Information
            </h3>
            <dl className="space-y-3">
              <div>
                <dt className="text-sm text-gray-500">Status</dt>
                <dd className="text-white font-semibold flex items-center gap-2">
                  {order.status === 'completed' ? (
                    <>
                      <CheckCircle className="w-4 h-4 text-green-400" />
                      Completed
                    </>
                  ) : (
                    <>
                      <Clock className="w-4 h-4 text-yellow-400" />
                      Processing
                    </>
                  )}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">Access Expires</dt>
                <dd className="text-white font-semibold">
                  {formatDate(order.expires_at)}
                  {daysRemaining < 7 && (
                    <span className="text-xs text-orange-400 ml-2">
                      ({daysRemaining} days left)
                    </span>
                  )}
                </dd>
              </div>
            </dl>
          </div>

          {/* Download Info */}
          <div>
            <h3 className="text-sm font-bold text-gray-400 uppercase mb-4">
              Included Files
            </h3>
            <ul className="space-y-2 text-sm text-gray-300">
              <li className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-purple-400"></span>
                Research Memo PDF
              </li>
              <li className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-purple-400"></span>
                Complete Punch List
              </li>
              <li className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-purple-400"></span>
                State Permit Package
              </li>
            </ul>
          </div>
        </div>

        {/* Download Buttons */}
        {order.status === 'completed' && order.pdfs && order.pdfs.length > 0 ? (
          <div>
            <h3 className="text-sm font-bold text-gray-400 uppercase mb-4">
              Download Files
            </h3>
            <div className="grid sm:grid-cols-3 gap-3">
              {order.pdfs.map((pdf) => (
                <button
                  key={pdf.type}
                  onClick={() => onDownload(pdf)}
                  className="flex items-center justify-center gap-2 px-4 py-3 bg-purple-600/20 hover:bg-purple-600/30 border border-purple-500/30 hover:border-purple-500/50 rounded-lg transition text-purple-300 hover:text-purple-200 font-semibold"
                >
                  <Download className="w-4 h-4" />
                  <span className="truncate">{pdf.name}</span>
                </button>
              ))}
            </div>
            {daysRemaining < 3 && (
              <div className="mt-4 p-3 bg-orange-500/10 border border-orange-500/30 rounded-lg">
                <p className="text-sm text-orange-300">
                  ⚠️ Downloads expire in {daysRemaining} days. Download now to save offline.
                </p>
              </div>
            )}
          </div>
        ) : (
          <div className="p-4 bg-slate-700/30 border border-slate-600/30 rounded-lg text-center">
            <p className="text-gray-400 text-sm">
              📧 Check your email for download links. They should arrive within 1 hour.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
