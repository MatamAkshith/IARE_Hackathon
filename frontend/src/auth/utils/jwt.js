/**
 * JWT Utility — Stage E.1
 *
 * Handles storage of the server-issued JWT (localStorage) and safe
 * decoding of the base64url payload.  Encoding is no longer done
 * client-side; tokens are issued exclusively by the backend.
 */

const TOKEN_KEY = 'threatlens_auth_token';

// ── Storage helpers ──────────────────────────────────────────────────────────

/** Retrieve the stored JWT from sessionStorage. */
export const getToken = () => sessionStorage.getItem(TOKEN_KEY);

/** Persist a JWT to sessionStorage. */
export const setToken = (token) => sessionStorage.setItem(TOKEN_KEY, token);

/** Remove the stored JWT from sessionStorage. */
export const removeToken = () => {
  sessionStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(TOKEN_KEY);
};

// ── Token decoding ───────────────────────────────────────────────────────────

/**
 * Decode the base64url payload of a JWT without verifying the signature.
 * Signature verification is the backend's responsibility.
 *
 * @param {string} token
 * @returns {Object|null} Decoded payload or null on error
 */
export const decodeToken = (token) => {
  if (!token) return null;
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    // base64url → base64 → JSON
    const base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/');
    const json = atob(base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), '='));
    return JSON.parse(json);
  } catch {
    return null;
  }
};

/**
 * Check whether a JWT has expired based on its `exp` claim.
 *
 * @param {string} token
 * @returns {boolean} True if expired or invalid
 */
export const isTokenExpired = (token) => {
  const payload = decodeToken(token);
  if (!payload || !payload.exp) return true;
  return payload.exp < Math.floor(Date.now() / 1000);
};
