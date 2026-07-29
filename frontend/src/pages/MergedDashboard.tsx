/**
 * RegGuard Landing Page — multi-segment site diligence
 * Free lookups → Contractor Pro / IC Project / Sponsor
 */

import { useNavigate } from 'react-router-dom';
import {
  CheckCircle,
  Clock,
  FileText,
  Download,
} from 'lucide-react';
import FreeTrialForm from '../components/FreeTrialForm';

export function PlatformDashboard() {
  const navigate = useNavigate();

  const handleOrderReport = () => {
    navigate('/pricing');
  };

  const handleIcProject = () => {
    navigate('/checkout/ic_project');
  };

  const scrollToFreeTrial = () => {
    document.getElementById('free-trial-form')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <header className="bg-slate-900/80 backdrop-blur border-b border-purple-500/20 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-black text-white">RegGuard</h1>
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/how-it-works')}
              className="text-gray-300 hover:text-white transition text-sm font-semibold"
            >
              How it works
            </button>
            <button
              onClick={() => navigate('/pricing')}
              className="text-gray-300 hover:text-white transition text-sm font-semibold"
            >
              Pricing
            </button>
            <button
              onClick={handleOrderReport}
              className="px-6 py-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-bold rounded-lg transition shadow-lg shadow-green-500/20 cursor-pointer"
            >
              Order Report
            </button>
          </div>
        </div>
      </header>

      <section className="px-4 py-16 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-5xl md:text-6xl font-black text-white mb-6 leading-tight">
            Permitting research shouldn&apos;t take{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-pink-300">
              6 weeks
            </span>{' '}
            and cost{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-pink-300">
              $100K
            </span>
          </h1>

          <p className="text-lg text-gray-300 mb-10">
            You&apos;re a contractor, IC consultant, or developer. You screen a new site and need
            permitting requirements, moratoriums, and forms — without burning weeks of capital.
          </p>

          <div className="bg-gradient-to-r from-green-600/20 to-emerald-600/20 border border-green-500/30 rounded-xl p-8 mb-12">
            <p className="text-xl text-white font-bold mb-4">
              RegGuard cuts research time from weeks to same-day. Here&apos;s what you get:
            </p>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <FileText className="w-6 h-6 text-green-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold text-white">Research memo (PDF)</p>
                  <p className="text-gray-300 text-sm">
                    Local permitting requirements, interconnection process, timeline, costs
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Download className="w-6 h-6 text-green-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold text-white">Contractor punch list (PDF)</p>
                  <p className="text-gray-300 text-sm">
                    Action items. Who to call. What to submit. Step-by-step next steps.
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Download className="w-6 h-6 text-green-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold text-white">Permit application package (PDF)</p>
                  <p className="text-gray-300 text-sm">
                    Forms, checklists, required docs. Ready to submit.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 mb-8">
            <button
              onClick={scrollToFreeTrial}
              className="px-10 py-4 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-black text-lg rounded-xl transition shadow-lg shadow-green-500/30 hover:shadow-green-500/50 cursor-pointer"
            >
              Try Free (No Credit Card)
            </button>
            <button
              onClick={handleIcProject}
              className="px-10 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold text-lg rounded-xl transition shadow-lg shadow-blue-500/30 hover:shadow-blue-500/50 cursor-pointer"
            >
              Order IC Report — $1,500
            </button>
          </div>

          <p className="text-gray-400 text-sm mt-6">
            <strong>Results display in the app.</strong> Then text or email them. Upgrade to
            Contractor Pro ($149/mo) or an IC Project Report ($1,500) when you need the full package.
          </p>
        </div>
      </section>

      <section className="px-4 py-16 sm:px-6 lg:px-8 border-t border-purple-500/10 bg-slate-900/40">
        <div className="max-w-2xl mx-auto">
          <FreeTrialForm showHero />
        </div>
      </section>

      <section className="px-4 py-16 sm:px-6 lg:px-8 border-t border-purple-500/10">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-black text-white mb-12">The Cost of Slow Research:</h2>

          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-gradient-to-br from-red-500/10 to-red-600/5 border border-red-500/20 rounded-xl p-8">
              <h3 className="text-lg font-bold text-white mb-6">Without RegGuard</h3>
              <div className="space-y-4">
                <div className="flex gap-3">
                  <span className="text-red-400 text-2xl font-bold">❌</span>
                  <div>
                    <p className="font-bold text-white">Weeks of research</p>
                    <p className="text-gray-400 text-sm">You&apos;re burning capital while waiting for answers.</p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <span className="text-red-400 text-2xl font-bold">❌</span>
                  <div>
                    <p className="font-bold text-white">High upfront costs</p>
                    <p className="text-gray-400 text-sm">Significant money before you know if the site works.</p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <span className="text-red-400 text-2xl font-bold">❌</span>
                  <div>
                    <p className="font-bold text-white">Bad sites discovered late</p>
                    <p className="text-gray-400 text-sm">Fatal flaws show up after you&apos;re deep into diligence.</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-green-500/10 to-emerald-600/5 border-2 border-green-500/30 rounded-xl p-8">
              <h3 className="text-lg font-bold text-white mb-6">With RegGuard</h3>
              <div className="space-y-4">
                <div className="flex gap-3">
                  <span className="text-green-400 text-2xl font-bold">✓</span>
                  <div>
                    <p className="font-bold text-white">Same-day answers</p>
                    <p className="text-gray-400 text-sm">From question to decision in one business day.</p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <span className="text-green-400 text-2xl font-bold">✓</span>
                  <div>
                    <p className="font-bold text-white">Clear pricing by segment</p>
                    <p className="text-gray-400 text-sm">
                      Free lookups, Pro at $149/mo, IC reports at $1,500 — no surprises.
                    </p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <span className="text-green-400 text-2xl font-bold">✓</span>
                  <div>
                    <p className="font-bold text-white">Kill bad sites fast</p>
                    <p className="text-gray-400 text-sm">Discover fatal flaws early. Move on with confidence.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="px-4 py-16 sm:px-6 lg:px-8 border-t border-purple-500/10">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-black text-white mb-12">Pricing that matches how you work</h2>

          <div className="grid md:grid-cols-3 gap-6 mb-12">
            <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-purple-500/30 rounded-xl p-8 text-center">
              <Clock className="w-12 h-12 text-blue-400 mx-auto mb-4" />
              <p className="text-3xl font-black text-white mb-2">$0</p>
              <p className="text-gray-400">Free contractor lookups</p>
            </div>
            <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-purple-500/30 rounded-xl p-8 text-center">
              <p className="text-3xl font-black text-white mb-2">$149/mo</p>
              <p className="text-gray-400">Contractor Pro</p>
            </div>
            <div className="bg-gradient-to-br from-green-600/20 to-emerald-600/20 border border-green-500/30 rounded-xl p-8 text-center">
              <p className="text-3xl font-black text-white mb-2">$1,500</p>
              <p className="text-gray-400">IC Project Report (one-time)</p>
            </div>
          </div>

          <div className="text-center">
            <button
              onClick={() => navigate('/pricing')}
              className="text-purple-300 hover:text-white font-semibold transition"
            >
              See full pricing → Contractor, IC Annual ($15K/yr), Sponsor ($1,500/mo)
            </button>
          </div>
        </div>
      </section>

      <section className="px-4 py-16 sm:px-6 lg:px-8 border-t border-purple-500/10">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-black text-white mb-12">Common questions</h2>
          <div className="space-y-8">
            <div>
              <p className="font-bold text-white mb-2">Can I trust AI-generated research?</p>
              <p className="text-gray-400">
                Yes. Every finding is sourced. Your attorney should still review before filing —
                RegGuard accelerates research; counsel makes final calls.
              </p>
            </div>
            <div>
              <p className="font-bold text-white mb-2">What&apos;s free vs paid?</p>
              <p className="text-gray-400">
                Free lookups show summary results in-app (text/email them). Contractor Pro is
                $149/month. Full IC project packages start at $1,500 one-time.
              </p>
            </div>
            <div>
              <p className="font-bold text-white mb-2">Can I use RegGuard for multiple sites?</p>
              <p className="text-gray-400">
                Yes. Contractors use Pro for ongoing lookups. IC consultants order per project
                ($1,500) or subscribe annually ($15,000/year) for unlimited capacity.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="px-4 py-16 sm:px-6 lg:px-8 border-t border-purple-500/10">
        <div className="max-w-4xl mx-auto">
          <div className="bg-gradient-to-br from-emerald-600/20 to-green-600/20 border-2 border-emerald-500/30 rounded-xl p-8">
            <div className="flex items-start gap-4">
              <CheckCircle className="w-8 h-8 text-emerald-400 flex-shrink-0 mt-1" />
              <div>
                <h3 className="text-lg font-bold text-white mb-3">Our Guarantee</h3>
                <p className="text-gray-300">
                  We stand behind our research.{' '}
                  <strong>If a critical finding is wrong, we refund 100% of your payment.</strong>
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="px-4 py-20 sm:px-6 lg:px-8 border-t border-purple-500/10 bg-gradient-to-br from-green-600/20 to-emerald-600/20">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-4xl font-black text-white mb-6">
            How many sites are you screening this month?
          </h2>
          <p className="text-xl text-gray-300 mb-10 leading-relaxed">
            Start free, upgrade when you need a full package. Get answers same-day.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-6">
            <button
              onClick={scrollToFreeTrial}
              className="px-10 py-4 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-black text-lg rounded-xl transition shadow-lg cursor-pointer"
            >
              Try Free Lookup
            </button>
            <button
              onClick={handleIcProject}
              className="px-10 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold text-lg rounded-xl transition shadow-lg cursor-pointer"
            >
              Order Report — $1,500
            </button>
          </div>
          <p className="text-gray-400 text-sm">Same-day delivery. No setup required.</p>
        </div>
      </section>

      <footer className="px-4 py-12 sm:px-6 lg:px-8 bg-slate-900/50 border-t border-purple-500/10 text-center text-gray-400 text-sm">
        <div className="max-w-6xl mx-auto mb-8 space-y-2">
          <div className="flex justify-center gap-6 flex-wrap">
            <button
              onClick={() => navigate('/how-it-works')}
              className="text-purple-400 hover:text-purple-300 transition"
            >
              How it works
            </button>
            <button
              onClick={() => navigate('/pricing')}
              className="text-purple-400 hover:text-purple-300 transition"
            >
              Pricing
            </button>
            <a href="mailto:hello@regguard.com" className="text-purple-400 hover:text-purple-300 transition">
              Contact
            </a>
          </div>
          <p className="text-xs">
            RegGuard © 2026 • Permitting research intelligence •
            <a href="#" className="text-purple-400 hover:text-purple-300 ml-2">
              Privacy
            </a>{' '}
            •
            <a href="#" className="text-purple-400 hover:text-purple-300 ml-2">
              Terms
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}

export default PlatformDashboard;
