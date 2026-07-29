/**
 * Lightweight self-check for voice fill parsing (run via node / vitest if available).
 */
import { parseVoiceTrialTranscript, voiceFieldsReady } from '../voiceFillParse';

const samples: Array<{ input: string; expect: Partial<ReturnType<typeof parseVoiceTrialTranscript>> }> = [
  {
    input: '123 Main Street in Austin Texas 78701 email me at you@company.com',
    expect: {
      zip: '78701',
      email: 'you@company.com',
      state: 'TX',
    },
  },
  {
    input: '500 Congress Ave, Austin, TX 78701, phone 512-555-1234, alex@regguard.com',
    expect: {
      zip: '78701',
      email: 'alex@regguard.com',
      phone: '5125551234',
      state: 'TX',
      city: 'Austin',
    },
  },
];

export function runVoiceFillParseSelfCheck(): { ok: boolean; failures: string[] } {
  const failures: string[] = [];
  for (const sample of samples) {
    const got = parseVoiceTrialTranscript(sample.input);
    for (const [k, v] of Object.entries(sample.expect)) {
      if ((got as Record<string, string>)[k] !== v) {
        failures.push(`${sample.input} → ${k}: got "${(got as Record<string, string>)[k]}" want "${v}"`);
      }
    }
  }
  const ready = voiceFieldsReady(
    parseVoiceTrialTranscript(
      '100 Industrial Blvd in Dallas Texas 75201 email ops@example.com'
    )
  );
  if (!ready) failures.push('expected readyToRun for complete Dallas sample');
  return { ok: failures.length === 0, failures };
}
