/**
 * Mock JWT Token helper utility for ThreatLens.
 * Simulates encoding, decoding, and managing JSON Web Tokens in local storage.
 */

const TOKEN_KEY = 'threatlens_auth_token';

/**
 * Encodes mock user data into a simulated JWT string format
 * @param {Object} payload - User data (email, role, name, etc)
 * @returns {string} Simulated JWT token
 */
export const encodeMockToken = (payload) => {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  
  // Add issue and expiration time (1 hour from now)
  const exp = Math.floor(Date.now() / 1000) + 3600;
  const iat = Math.floor(Date.now() / 1000);
  const fullPayload = { ...payload, exp, iat };
  
  const encodedPayload = btoa(JSON.stringify(fullPayload));
  const signature = btoa('threatlens_mock_signature');
  
  return `${header}.${encodedPayload}.${signature}`;
};

/**
 * Decodes a simulated JWT token back into JSON payload
 * @param {string} token 
 * @returns {Object|null} Decoded payload or null if invalid
 */
export const decodeMockToken = (token) => {
  if (!token) return null;
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    
    // Decode base64 payload
    const decodedPayload = JSON.parse(atob(parts[1]));
    return decodedPayload;
  } catch (error) {
    console.error('Failed to decode mock JWT token:', error);
    return null;
  }
};

/**
 * Retrieves the token from local storage
 * @returns {string|null}
 */
export const getToken = () => {
  return localStorage.getItem(TOKEN_KEY);
};

/**
 * Saves the token to local storage
 * @param {string} token 
 */
export const setToken = (token) => {
  localStorage.setItem(TOKEN_KEY, token);
};

/**
 * Removes the token from local storage
 */
export const removeToken = () => {
  localStorage.removeItem(TOKEN_KEY);
};

/**
 * Checks if a token is expired
 * @param {string} token 
 * @returns {boolean} True if expired or invalid
 */
export const isTokenExpired = (token) => {
  const payload = decodeMockToken(token);
  if (!payload || !payload.exp) return true;
  
  const currentTime = Math.floor(Date.now() / 1000);
  return payload.exp < currentTime;
};
