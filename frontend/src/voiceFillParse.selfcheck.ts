/**
 * Lightweight self-check for voice fill parsing.
 * Run: node --experimental-strip-types src/voiceFillParse.selfcheck.ts
 */
import {
  extractSpokenEmail,
  needsSpokenEmailTip,
  parseVoiceTrialTranscript,
  voiceFieldsReady,
} from './voiceFillParse.ts';

const samples: Array<{
  input: string;
  expect: Partial<ReturnType<typeof parseVoiceTrialTranscript>>;
}> = [
  {
    input: '123 Main Street in Austin Texas 78701 email me at you@company.com',
    expect: {
      address: '123 Main Street',
      city: 'Austin',
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
  // Spoken emails
  {
    input: '123 Main Street in Austin Texas 78701 email john at gmail dot com',
    expect: {
      email: 'john@gmail.com',
      city: 'Austin',
      state: 'TX',
      zip: '78701',
    },
  },
  {
    input: '200 Oak Ave in Dallas Texas 75201 john dot smith at company dot com',
    expect: {
      email: 'john.smith@company.com',
      city: 'Dallas',
      state: 'TX',
    },
  },
  {
    input: '10 Pine Road in Austin Texas 78701 john underscore smith at acme dot io',
    expect: {
      email: 'john_smith@acme.io',
      zip: '78701',
    },
  },
  {
    input: 'jane dash doe at example dot com',
    expect: {
      email: 'jane-doe@example.com',
    },
  },
  // Suite / unit
  {
    input: '123 Main Street suite 400 Austin Texas 78701 email ops@example.com',
    expect: {
      address: '123 Main Street suite 400',
      city: 'Austin',
      state: 'TX',
      zip: '78701',
      email: 'ops@example.com',
    },
  },
  {
    input: '88 Market Street unit 12B San Francisco California 94105 email a@b.co',
    expect: {
      address: '88 Market Street unit 12B',
      city: 'San Francisco',
      state: 'CA',
      zip: '94105',
    },
  },
  // Multi-word cities
  {
    input: '123 Main Street San Antonio Texas 78701 email you@company.com',
    expect: {
      address: '123 Main Street',
      city: 'San Antonio',
      state: 'TX',
      zip: '78701',
      email: 'you@company.com',
    },
  },
  {
    input: '400 Broadway in New York New York 10013 email hello@nyc.com',
    expect: {
      address: '400 Broadway',
      city: 'New York',
      state: 'NY',
      zip: '10013',
      email: 'hello@nyc.com',
    },
  },
  {
    input: '1 Main Street Los Angeles California 90012 email team@la.com',
    expect: {
      city: 'Los Angeles',
      state: 'CA',
      zip: '90012',
    },
  },
];

export function runVoiceFillParseSelfCheck(): { ok: boolean; failures: string[] } {
  const failures: string[] = [];
  for (const sample of samples) {
    const got = parseVoiceTrialTranscript(sample.input);
    for (const [k, v] of Object.entries(sample.expect)) {
      if ((got as Record<string, string>)[k] !== v) {
        failures.push(
          `${sample.input} → ${k}: got "${(got as Record<string, string>)[k]}" want "${v}"`
        );
      }
    }
  }

  const ready = voiceFieldsReady(
    parseVoiceTrialTranscript(
      '100 Industrial Blvd in Dallas Texas 75201 email ops@example.com'
    )
  );
  if (!ready) failures.push('expected readyToRun for complete Dallas sample');

  const spoken = extractSpokenEmail('reach me at john at gmail dot com please');
  if (!spoken || spoken.email !== 'john@gmail.com') {
    failures.push('extractSpokenEmail failed for john at gmail dot com');
  }

  const tip = needsSpokenEmailTip(
    parseVoiceTrialTranscript('123 Main Street Austin Texas 78701 email me at john gmail com')
  );
  if (!tip) failures.push('expected spoken-email tip when email parse fails');

  const noTip = needsSpokenEmailTip(
    parseVoiceTrialTranscript(
      '123 Main Street Austin Texas 78701 john at gmail dot com'
    )
  );
  if (noTip) failures.push('did not expect tip when spoken email parsed cleanly');

  return { ok: failures.length === 0, failures };
}

const result = runVoiceFillParseSelfCheck();
if (!result.ok) {
  console.error('voiceFillParse self-check FAILED');
  for (const f of result.failures) console.error(' -', f);
  process.exit(1);
}
console.log(`voiceFillParse self-check OK (${samples.length}+ cases)`);
