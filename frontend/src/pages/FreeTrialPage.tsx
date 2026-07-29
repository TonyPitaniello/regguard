/**
 * RegGuard Free Trial page — thin wrapper around shared FreeTrialForm
 */

import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import FreeTrialForm from '../components/FreeTrialForm';

export default function FreeTrialPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <header className="bg-slate-900/80 backdrop-blur border-b border-purple-500/20 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-purple-400 hover:text-purple-300 transition"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </button>
        </div>
      </header>

      <section className="px-4 py-16 sm:px-6 lg:px-8">
        <div className="max-w-2xl mx-auto">
          <FreeTrialForm showHero />
        </div>
      </section>
    </div>
  );
}
