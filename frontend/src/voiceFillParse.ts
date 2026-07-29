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
/** US phone: (555) 123-4567, 555-123-4567, +1 555 123 4567, spoken-digit clumps */
const PHONE_RE =
  /(?:\+?1[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}\b/;
const ZIP_RE = /\b(\d{5})(?:-\d{4})?\b/;
const STATE_RE = /\b([A-Z]{2})\b/;

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
    .replace(/\b(phone|email|number|at)\b/gi, '')
    .replace(/,/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
  return { city: rest, state };
}

export function parseVoiceTrialTranscript(rawTranscript: string): VoiceFillFields {
  let working = stripFillers(rawTranscript || '');

  let email = '';
  const emailMatch = working.match(EMAIL_RE);
  if (emailMatch) {
    email = emailMatch[0];
    working = working.replace(emailMatch[0], ' ');
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
  } else if (inCity && inCity.index != null) {
    address = working.slice(0, inCity.index).replace(/,?\s*$/, '').trim();
    const split = splitCityState(inCity[1] || '');
    city = split.city;
    state = split.state;
    // Prefer stripping spoken state from city if still glued (e.g. "Dallas Texas")
    if (state && city) {
      const glued = splitCityState(city);
      if (glued.state && glued.city) {
        city = glued.city;
        state = state || glued.state;
      }
    }
  } else {
    state = spokenStateToCode(working) || working.match(STATE_RE)?.[1]?.toUpperCase() || '';
    const tokens = working.split(/\s+/).filter(Boolean);
    if (tokens.length >= 3) {
      let end = tokens.length;
      if (state) {
        const stateName = Object.entries(US_STATES).find(([, c]) => c === state)?.[0];
        if (stateName) {
          const parts = stateName.split(' ');
          const tail = tokens.slice(-parts.length).join(' ').toLowerCase();
          if (tail === stateName) end -= parts.length;
          else if (tokens[tokens.length - 1]?.toUpperCase() === state) end -= 1;
        } else if (tokens[tokens.length - 1]?.toUpperCase() === state) {
          end -= 1;
        }
      }
      const beforeState = tokens.slice(0, end);
      if (beforeState.length >= 2) {
        city = beforeState[beforeState.length - 1];
        address = beforeState.slice(0, -1).join(' ');
      } else {
        address = beforeState.join(' ');
      }
    } else {
      address = working;
    }
  }

  // Clean city if it absorbed a state code
  city = city.replace(STATE_RE, '').replace(/\s+/g, ' ').trim();
  address = address.replace(/\s+/g, ' ').trim();

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
