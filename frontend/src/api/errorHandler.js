/**
 * Global API Error Handler — ThreatLens Frontend
 *
 * Provides a single utility function that normalizes raw Axios errors into the
 * canonical `ApiError` shape defined in `types.js`. This function is used
 * exclusively by the Axios response interceptor in `client.js`.
 *
 * Handles the following FastAPI error patterns:
 *  - 422 Unprocessable Entity: detail is an array of {loc, msg, type} objects
 *  - 4xx / 5xx with string detail: detail is a plain string
 *  - Network errors / timeouts (no HTTP response received)
 *  - Unknown / unexpected error shapes
 *
 * @module api/errorHandler
 */

/**
 * Extracts a human-readable summary from a FastAPI 422 validation error array.
 *
 * @param {import('./types').FastApiValidationError[]} detail - The `detail` array from FastAPI
 * @returns {string} Concatenated, comma-separated field error messages
 */
function summarizeValidationErrors(detail) {
  if (!Array.isArray(detail) || detail.length === 0) {
    return 'Validation error — please check your input.'
  }
  return detail
    .map((err) => {
      const field = err.loc ? err.loc.slice(-1)[0] : 'field'
      return `${field}: ${err.msg}`
    })
    .join(', ')
}

/**
 * Normalizes any Axios error into a canonical `ApiError` object.
 *
 * This is the **only** place in the frontend where raw HTTP error shapes are
 * parsed. Components and services should never inspect `error.response`
 * directly — they receive a structured `ApiError` instead.
 *
 * @param {import('axios').AxiosError} error - The raw Axios error object
 * @returns {import('./types').ApiError}     - Structured, normalized API error
 */
export function normalizeError(error) {
  // ── Network / CORS / Timeout errors (no response from server) ──────────────
  if (!error.response) {
    if (error.code === 'ECONNABORTED') {
      return {
        isApiError: true,
        status: 0,
        code: 'REQUEST_TIMEOUT',
        message: 'The request timed out. The backend may be slow or unavailable.'
      }
    }
    return {
      isApiError: true,
      status: 0,
      code: 'NETWORK_ERROR',
      message: 'Unable to reach the ThreatLens backend. Check that the server is running on port 8000.'
    }
  }

  const { status, data } = error.response
  const detail = data?.detail

  // ── 422 Unprocessable Entity (FastAPI validation errors) ───────────────────
  if (status === 422) {
    return {
      isApiError: true,
      status,
      code: 'VALIDATION_ERROR',
      message: summarizeValidationErrors(detail),
      validationErrors: Array.isArray(detail) ? detail : []
    }
  }

  // ── 404 Not Found ──────────────────────────────────────────────────────────
  if (status === 404) {
    return {
      isApiError: true,
      status,
      code: 'NOT_FOUND',
      message: typeof detail === 'string' ? detail : 'The requested resource was not found.'
    }
  }

  // ── 400 Bad Request ────────────────────────────────────────────────────────
  if (status === 400) {
    return {
      isApiError: true,
      status,
      code: 'BAD_REQUEST',
      message: typeof detail === 'string' ? detail : 'The request was malformed. Please check your input.'
    }
  }

  // ── 401 Unauthorized ───────────────────────────────────────────────────────
  if (status === 401) {
    return {
      isApiError: true,
      status,
      code: 'UNAUTHORIZED',
      message: typeof detail === 'string' ? detail : 'Unauthorized. Authentication is required.'
    }
  }

  // ── 500+ Server Errors ─────────────────────────────────────────────────────
  if (status >= 500) {
    return {
      isApiError: true,
      status,
      code: 'SERVER_ERROR',
      message: typeof detail === 'string'
        ? detail
        : `Internal server error (HTTP ${status}). The backend encountered an unexpected problem.`
    }
  }

  // ── Fallback for any other status code ─────────────────────────────────────
  return {
    isApiError: true,
    status,
    code: 'UNKNOWN_ERROR',
    message: typeof detail === 'string' ? detail : `Unexpected error (HTTP ${status}).`
  }
}

/**
 * Type guard — returns `true` if the value is a normalized `ApiError`.
 *
 * @param {unknown} value - Any caught error value
 * @returns {value is import('./types').ApiError}
 */
export function isApiError(value) {
  return (
    typeof value === 'object' &&
    value !== null &&
    value.isApiError === true
  )
}

export default { normalizeError, isApiError }
