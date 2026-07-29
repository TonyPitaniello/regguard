/**
 * Shared free-trial form used on homepage (/) and /free-trial
 * Submits to production API via backendUrl(), then shows results in-app.
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, CheckCircle } from 'lucide-react';
import { LocationPicker } from './LocationPicker';
import { backendUrl } from '../env';

export default function FreeTrialForm({ showHero = false }: { showHero?: boolean }) {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    address: '',
    city: '',
    state: '',
    zip: '',
    projectType: 'data-center',
    email: '',
  });
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleLocationSelect = (
    address: string,
    city: string,
    state: string,
    zip: string,
    _lat: number,
    _lng: number
  ) => {
    setFormData((prev) => ({
      ...prev,
      address,
      city,
      state,
      zip,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (!formData.address || !formData.city || !formData.state || !formData.zip || !formData.email) {
      setError('Please fill in all fields including ZIP code');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(backendUrl('/free-trial'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          address: `${formData.address}, ${formData.city}, ${formData.state}, ${formData.zip}`,
          zip: formData.zip,
          project_type: formData.projectType,
          email: formData.email,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit trial request');
      }

      const data = await response.json();

      if (data.analysis_data) {
        sessionStorage.setItem('analysisResults', JSON.stringify(data.analysis_data));
        if (formData.email) {
          sessionStorage.setItem('userEmail', formData.email);
        }
        navigate('/results', { state: { analysis: data.analysis_data } });
      } else {
        setSubmitted(true);
      }
    } catch (err) {
      setError('Error submitting request. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div id="free-trial-form">
      {showHero && (
        <div className="text-center mb-10">
          <h2 className="text-3xl md:text-4xl font-black text-white mb-3">Try RegGuard Free</h2>
          <p className="text-gray-300">
            No credit card. Enter your site below — results display in the app, then you can text or email them.
          </p>
        </div>
      )}

      {submitted ? (
        <div className="bg-gradient-to-br from-emerald-600/20 to-green-600/20 border-2 border-emerald-500/30 rounded-2xl p-10 text-center">
          <CheckCircle className="w-14 h-14 text-emerald-400 mx-auto mb-4" />
          <h3 className="text-2xl font-black text-white mb-3">Request Submitted!</h3>
          <p className="text-gray-300 mb-2">
            Check your email within 24 hours ({formData.email})
          </p>
        </div>
      ) : (
        <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-purple-500/30 rounded-2xl p-8 md:p-10">
          <form onSubmit={handleSubmit} className="space-y-6" noValidate>
            <LocationPicker onLocationSelect={handleLocationSelect} disabled={loading} />

            <div>
              <label htmlFor="projectType" className="block text-white font-bold mb-2">
                What type of project? *
              </label>
              <select
                id="projectType"
                name="projectType"
                value={formData.projectType}
                onChange={handleInputChange}
                className="w-full px-4 py-3 bg-slate-700 border border-purple-500/30 rounded-lg text-white focus:outline-none focus:border-purple-500"
                disabled={loading}
              >
                <option value="data-center">Data Center</option>
                <option value="renewable">Solar / Wind / Battery</option>
                <option value="commercial">Commercial Building</option>
                <option value="industrial">Industrial / Manufacturing</option>
                <option value="utility">Utility / Substation</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div>
              <label htmlFor="home-email" className="block text-white font-bold mb-2">
                Your Email *
              </label>
              <input
                id="home-email"
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="you@company.com"
                autoComplete="email"
                className="w-full px-4 py-3 bg-slate-700 border border-purple-500/30 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500"
                disabled={loading}
              />
            </div>

            {error && (
              <div className="flex gap-3 p-4 bg-red-500/20 border border-red-500/30 rounded-lg">
                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                <p className="text-red-300 text-sm">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full px-6 py-4 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-bold text-lg rounded-xl transition shadow-lg shadow-green-500/20 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Analyzing site…' : 'Get Free Research Results'}
            </button>

            <p className="text-gray-400 text-sm text-center">
              Results show in the app. Then you can text or email them from the results page.
            </p>
          </form>
        </div>
      )}
    </div>
  );
}
