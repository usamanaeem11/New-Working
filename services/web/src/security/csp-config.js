/**
 * Content Security Policy Configuration
 * Web platform hardening
 */

export const CSP_DIRECTIVES = {
  'default-src': ["'self'"],
  'script-src': [
    "'self'",
    "'unsafe-inline'",  // Required for React
    'https://cdn.jsdelivr.net',  // CDN for libraries
  ],
  'style-src': [
    "'self'",
    "'unsafe-inline'",  // Required for styled-components
  ],
  'img-src': [
    "'self'",
    'data:',
    'https:',
  ],
  'font-src': [
    "'self'",
    'data:',
  ],
  'connect-src': [
    "'self'",
    'https://api.workingtracker.com',
    'wss://api.workingtracker.com',  // WebSocket
  ],
  'frame-ancestors': ["'none'"],  // Prevent clickjacking
  'base-uri': ["'self'"],
  'form-action': ["'self'"],
};

export function generateCSPHeader() {
  const directives = Object.entries(CSP_DIRECTIVES)
    .map(([key, values]) => `${key} ${values.join(' ')}`)
    .join('; ');
  
  return directives;
}

// XSS Protection
export const SECURITY_HEADERS = {
  'Content-Security-Policy': generateCSPHeader(),
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'DENY',
  'X-XSS-Protection': '1; mode=block',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
};
