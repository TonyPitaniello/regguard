/**
 * Client-side voice → free-trial field extraction (Web Speech transcript).
 * Zero-cost regex + heuristics — no backend NLP required.
 */

export const VOICE_FILL_EVENT = 'regguard:voice-fill';
export const VOICE_SUBMIT_EVENT = 'regguard:voice-submit';

export interface VoiceFillFields {
  address: string;
  city: string;
  state: string;
  zip: string;
  email: string;
  phone: string;
  transcript: string;
}

export type VoiceFillDetail = VoiceFillFields & {
  readyToRun: boolean;
};

const EMAIL_RE = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/;
/** Spoken: "john at gmail dot com", "john dot smith at company dot com" */
const SPOKEN_EMAIL_RE =
  /\b([a-z0-9]+(?:\s+(?:dot|period|underscore|dash|hyphen)\s+[a-z0-9]+)*)\s+at\s+([a-z0-9]+(?:\s+(?:dot|period)\s+[a-z0-9]+)+)\b/i;
/** US phone: (555) 123-4567, 555-123-4567, +1 555 123 4567, spoken-digit clumps */
const PHONE_RE =
  /(?:\+?1[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}\b/;
const ZIP_RE = /\b(\d{5})(?:-\d{4})?\b/;
const STATE_RE = /\b([A-Z]{2})\b/;

const STREET_TYPE_RE =
  /\b(street|st|avenue|ave|road|rd|boulevard|blvd|drive|dr|lane|ln|court|ct|way|place|pl|circle|cir|parkway|pkwy|highway|hwy|trail|terrace|ter)\b/i;
const SUITE_RE =
  /\b(?:suite|ste|unit|apt|apartment|building|bldg|#)\s*[a-z0-9-]+\b/gi;

const US_STATES: Record<string, string> = {
  alabama: 'AL',
  alaska: 'AK',
  arizona: 'AZ',
  arkansas: 'AR',
  california: 'CA',
  colorado: 'CO',
  connecticut: 'CT',
  delaware: 'DE',
  florida: 'FL',
  georgia: 'GA',
  hawaii: 'HI',
  idaho: 'ID',
  illinois: 'IL',
  indiana: 'IN',
  iowa: 'IA',
  kansas: 'KS',
  kentucky: 'KY',
  louisiana: 'LA',
  maine: 'ME',
  maryland: 'MD',
  massachusetts: 'MA',
  michigan: 'MI',
  minnesota: 'MN',
  mississippi: 'MS',
  missouri: 'MO',
  montana: 'MT',
  nebraska: 'NE',
  nevada: 'NV',
  'new hampshire': 'NH',
  'new jersey': 'NJ',
  'new mexico': 'NM',
  'new york': 'NY',
  'north carolina': 'NC',
  'north dakota': 'ND',
  ohio: 'OH',
  oklahoma: 'OK',
  oregon: 'OR',
  pennsylvania: 'PA',
  'rhode island': 'RI',
  'south carolina': 'SC',
  'south dakota': 'SD',
  tennessee: 'TN',
  texas: 'TX',
  utah: 'UT',
  vermont: 'VT',
  virginia: 'VA',
  washington: 'WA',
  'west virginia': 'WV',
  wisconsin: 'WI',
  wyoming: 'WY',
  'district of columbia': 'DC',
};

/** Common multi-word US cities (longest-first matching). */
const MULTI_WORD_CITIES = [
  'salt lake city',
  'oklahoma city',
  'virginia beach',
  'corpus christi',
  'colorado springs',
  'kansas city',
  'jersey city',
  'overland park',
  'fort lauderdale',
  'santa barbara',
  'san francisco',
  'san antonio',
  'los angeles',
  'new orleans',
  'baton rouge',
  'little rock',
  'fort worth',
  'long beach',
  'las vegas',
  'san diego',
  'san jose',
  'new york',
  'el paso',
  'st louis',
  'st paul',
  'des moines',
].sort((a, b) => b.length - a.length);

function digitsPhone(raw: string): string {
  const d = raw.replace(/\D/g, '');
  if (d.length === 11 && d.startsWith('1')) return d.slice(1);
  if (d.length === 10) return d;
  return d.slice(-10);
}

function spokenStateToCode(text: string): string {
  const lower = text.toLowerCase();
  let best = '';
  let bestLen = 0;
  for (const [name, code] of Object.entries(US_STATES)) {
    const re = new RegExp(`\\b${name.replace(/ /g, '\\s+')}\\b`, 'i');
    if (re.test(lower) && name.length > bestLen) {
      best = code;
      bestLen = name.length;
    }
  }
  return best;
}

function spokenSeparatorsToSymbols(part: string): string {
  return part
    .replace(/\s+(dot|period)\s+/gi, '.')
    .replace(/\s+underscore\s+/gi, '_')
    .replace(/\s+(dash|hyphen)\s+/gi, '-')
    .replace(/\s+/g, '')
    .toLowerCase();
}

/**
 * Convert spoken email phrases to RFC-ish addresses.
 * "john at gmail dot com" → john@gmail.com
 * "john underscore smith at acme dot io" → john_smith@acme.io
 */
export function extractSpokenEmail(text: string): { email: string; matched: string } | null {
  const m = text.match(SPOKEN_EMAIL_RE);
  if (!m) return null;
  const local = spokenSeparatorsToSymbols(m[1] || '');
  const domain = spokenSeparatorsToSymbols(m[2] || '');
  if (!local || !domain || !domain.includes('.')) return null;
  const email = `${local}@${domain}`;
  if (!EMAIL_RE.test(email)) return null;
  return { email, matched: m[0] };
}

/**
 * True when the user likely tried to dictate an email but we didn't get a usable one.
 */
export function needsSpokenEmailTip(fields: VoiceFillFields): boolean {
  if (fields.email && EMAIL_RE.test(fields.email)) return false;
  const t = (fields.transcript || '').toLowerCase();
  if (!t.trim()) return false;
  const tried =
    /\bemail\b/.test(t) ||
    (/\bat\b/.test(t) && /\b(dot|period)\b/.test(t)) ||
    SPOKEN_EMAIL_RE.test(t);
  return tried || !fields.email;
}

/**
 * Strip filler phrases speakers often add before the address.
 */
function stripFillers(text: string): string {
  return text
    .replace(
      /\b(my (email|phone|number|address) is|email me at|email is|phone number|phone is|phone|call me at|text me at|research|run research|look up|please|um+|uh+)\b/gi,
      ' '
    )
    .replace(/\s+/g, ' ')
    .replace(/\s*,\s*,+/g, ', ')
    .trim();
}

/**
 * Pull trailing US state (abbrev or full name) off a city/state phrase.
 */
function splitCityState(phrase: string): { city: string; state: string } {
  let rest = phrase.trim().replace(/\s+/g, ' ');
  let state = '';
  const spoken = spokenStateToCode(rest);
  if (spoken) {
    state = spoken;
    const stateName = Object.entries(US_STATES).find(([, c]) => c === spoken)?.[0];
    if (stateName) {
      const nameRe = new RegExp(`\\s*\\b${stateName.replace(/ /g, '\\s+')}\\b\\s*$`, 'i');
      if (nameRe.test(rest)) {
        rest = rest.replace(nameRe, '').trim();
      } else {
        rest = rest.replace(new RegExp(`\\b${spoken}\\b`, 'i'), '').trim();
      }
    }
  } else {
    const trailing = rest.match(/\b([A-Za-z]{2})\s*$/);
    if (trailing) {
      state = trailing[1].toUpperCase();
      rest = rest.slice(0, -trailing[1].length).trim();
    }
  }
  rest = rest
    .replace(/\b(phone|email|number)\b/gi, '')
    .replace(/,/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
  return { city: rest, state };
}

function findMultiWordCity(tokens: string[]): { city: string; cityTokenCount: number } | null {
  const lower = tokens.map((t) => t.toLowerCase());
  const joined = lower.join(' ');
  for (const city of MULTI_WORD_CITIES) {
    if (joined === city || joined.endsWith(' ' + city)) {
      const parts = city.split(' ');
      return { city: titleCaseCity(city), cityTokenCount: parts.length };
    }
  }
  return null;
}

function titleCaseCity(name: string): string {
  return name
    .split(' ')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(' ');
}

/**
 * Split "STREET [suite N] CITY…" when there are no commas / "in".
 * Keeps suite/unit in the street line; prefers multi-word city names.
 */
function splitStreetAndCity(beforeState: string[]): { address: string; city: string } {
  if (beforeState.length === 0) return { address: '', city: '' };
  if (beforeState.length === 1) return { address: beforeState[0], city: '' };

  const mw = findMultiWordCity(beforeState);
  if (mw && beforeState.length > mw.cityTokenCount) {
    return {
      address: beforeState.slice(0, -mw.cityTokenCount).join(' '),
      city: mw.city,
    };
  }

  // Find last street-type token; optional suite/unit after it stays in address.
  let streetEnd = -1;
  for (let i = 0; i < beforeState.length; i++) {
    if (STREET_TYPE_RE.test(beforeState[i])) streetEnd = i;
  }

  if (streetEnd >= 0) {
    let addrEnd = streetEnd;
    // Consume "suite 400" / "unit 12B" after street type
    let i = streetEnd + 1;
    while (i < beforeState.length) {
      const pair = `${beforeState[i]} ${beforeState[i + 1] || ''}`;
      const one = beforeState[i];
      if (/^(suite|ste|unit|apt|apartment|building|bldg)$/i.test(one) && beforeState[i + 1]) {
        addrEnd = i + 1;
        i += 2;
        continue;
      }
      if (/^#/.test(one) || SUITE_RE.test(pair)) {
        // reset lastIndex — SUITE_RE is global
        SUITE_RE.lastIndex = 0;
        if (/^(suite|ste|unit|apt|apartment|building|bldg|#)/i.test(one)) {
          addrEnd = beforeState[i + 1] ? i + 1 : i;
          i = addrEnd + 1;
          continue;
        }
      }
      SUITE_RE.lastIndex = 0;
      break;
    }
    const address = beforeState.slice(0, addrEnd + 1).join(' ');
    const cityTokens = beforeState.slice(addrEnd + 1);
    if (cityTokens.length) {
      const cityMw = findMultiWordCity(cityTokens);
      return {
        address,
        city: cityMw ? cityMw.city : cityTokens.join(' '),
      };
    }
    return { address, city: '' };
  }

  // Fallback: last token is city (single-word)
  return {
    address: beforeState.slice(0, -1).join(' '),
    city: beforeState[beforeState.length - 1],
  };
}

function normalizeSuiteInAddress(address: string): string {
  return address
    .replace(/\b(ste)\b/gi, 'Suite')
    .replace(/\b(apt)\b/gi, 'Apt')
    .replace(/\s+/g, ' ')
    .trim();
}

export function parseVoiceTrialTranscript(rawTranscript: string): VoiceFillFields {
  let working = stripFillers(rawTranscript || '');

  let email = '';
  const emailMatch = working.match(EMAIL_RE);
  if (emailMatch) {
    email = emailMatch[0];
    working = working.replace(emailMatch[0], ' ');
  } else {
    const spoken = extractSpokenEmail(working);
    if (spoken) {
      email = spoken.email;
      working = working.replace(spoken.matched, ' ');
    }
  }
  // Drop leftover "email" cue words after the address is isolated
  if (email) {
    working = working.replace(/\b(e-?mail|email)\b/gi, ' ');
  }

  let phone = '';
  const phoneMatch = working.match(PHONE_RE);
  if (phoneMatch) {
    phone = digitsPhone(phoneMatch[0]);
    if (phone.length === 10) {
      working = working.replace(phoneMatch[0], ' ');
    } else {
      phone = '';
    }
  }

  let zip = '';
  const zipMatch = working.match(ZIP_RE);
  if (zipMatch) {
    zip = zipMatch[1];
    working = working.replace(zipMatch[0], ' ');
  }

  working = working.replace(/\s+/g, ' ').trim();

  let city = '';
  let state = '';
  let address = '';

  // Pattern: "STREET in CITY STATE"
  const inCity = working.match(/\bin\s+(.+)$/i);

  const commaParts = working
    .split(',')
    .map((p) => p.trim())
    .filter(Boolean);

  if (commaParts.length >= 2) {
    address = commaParts[0];
    const mid = commaParts[1] || '';
    const rest = commaParts.slice(2).join(' ');
    const midSplit = splitCityState(`${mid} ${rest}`.trim());
    city = midSplit.city || mid.replace(STATE_RE, '').replace(/\d+/g, '').trim();
    state = midSplit.state;
    if (!state) {
      const stateFromAbbrev = (mid + ' ' + rest).match(STATE_RE);
      state = stateFromAbbrev?.[1]?.toUpperCase() || spokenStateToCode(mid + ' ' + rest) || '';
    }
    // Multi-word city may span comma parts poorly — prefer known cities in mid+rest
    const cityCandidate = `${mid} ${rest}`.replace(STATE_RE, '').replace(/\d+/g, '').trim();
    const cityTokens = cityCandidate.split(/\s+/).filter(Boolean);
    const mw = findMultiWordCity(cityTokens);
    if (mw) city = mw.city;
  } else if (inCity && inCity.index != null) {
    address = working.slice(0, inCity.index).replace(/,?\s*$/, '').trim();
    const split = splitCityState(inCity[1] || '');
    city = split.city;
    state = split.state;
    if (state && city) {
      const glued = splitCityState(city);
      if (glued.state && glued.city) {
        city = glued.city;
        state = state || glued.state;
      }
    }
    const cityTokens = city.split(/\s+/).filter(Boolean);
    const mw = findMultiWordCity(cityTokens);
    if (mw) city = mw.city;
  } else {
    state = spokenStateToCode(working) || working.match(STATE_RE)?.[1]?.toUpperCase() || '';
    const tokens = working
      .split(/\s+/)
      .filter(Boolean)
      .filter((t) => !/^(email|e-?mail|phone|number|please)$/i.test(t));
    if (tokens.length >= 3) {
      let end = tokens.length;
      if (state) {
        const stateName = Object.entries(US_STATES).find(([, c]) => c === state)?.[0];
        if (stateName) {
          const parts = stateName.split(' ');
          // Prefer stripping state from the end; also scan near-end if cue words linger
          for (let i = end - parts.length; i >= Math.max(0, end - parts.length - 2); i--) {
            const slice = tokens.slice(i, i + parts.length).join(' ').toLowerCase();
            if (slice === stateName) {
              end = i;
              break;
            }
          }
          if (end === tokens.length && tokens[tokens.length - 1]?.toUpperCase() === state) {
            end -= 1;
          }
        } else if (tokens[tokens.length - 1]?.toUpperCase() === state) {
          end -= 1;
        }
      }
      const beforeState = tokens.slice(0, end);
      const split = splitStreetAndCity(beforeState);
      address = split.address;
      city = split.city;
    } else {
      address = working;
    }
  }

  // Peel a trailing state glued onto city ("Austin Texas"), but never wipe
  // cities that share a state name ("New York") when a state is already set.
  if (city) {
    const cleaned = splitCityState(city);
    if (cleaned.state && cleaned.city) {
      state = state || cleaned.state;
      city = cleaned.city;
    } else if (cleaned.state && !cleaned.city && !state) {
      state = cleaned.state;
    }
  }
  // Only strip 2-letter state codes from city when we already have state
  if (state) {
    city = city.replace(new RegExp(`\\b${state}\\b`, 'i'), '').replace(/\s+/g, ' ').trim();
  }
  city = city.replace(/\s+/g, ' ').trim();
  address = normalizeSuiteInAddress(address.replace(/\s+/g, ' ').trim());

  return {
    address,
    city,
    state,
    zip,
    email,
    phone,
    transcript: rawTranscript.trim(),
  };
}

export function voiceFieldsReady(fields: VoiceFillFields): boolean {
  return Boolean(fields.address && fields.city && fields.state && fields.zip && fields.email);
}

export function dispatchVoiceFill(fields: VoiceFillFields): void {
  if (typeof window === 'undefined') return;
  const detail: VoiceFillDetail = {
    ...fields,
    readyToRun: voiceFieldsReady(fields),
  };
  window.dispatchEvent(new CustomEvent(VOICE_FILL_EVENT, { detail }));
}

export function dispatchVoiceSubmit(): void {
  if (typeof window === 'undefined') return;
  window.dispatchEvent(new CustomEvent(VOICE_SUBMIT_EVENT));
}
