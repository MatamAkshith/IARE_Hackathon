/**
 * Centralized Axios HTTP Client — ThreatLens Frontend
 *
 * This is the single Axios instance used for **all** backend API calls.
 * Service files (dashboardService.js, scanService.js, etc.) must import this
 * client and call its methods instead of creating their own Axios instances.
 *
 * Configuration:
 *  - baseURL:  Read from VITE_API_BASE_URL (.env). Falls back to the local
 *              dev backend at http://localhost:8000/api/v1 if the variable is
 *              missing, so development works without a .env file.
 *  - timeout:  30 seconds — accommodates the full extraction pipeline which
 *              runs WHOIS, DNS, TLS, HTML, and threat intel concurrently.
 *  - headers:  Content-Type set to application/json globally.
 *
 * Interceptors:
 *  - REQUEST:  Logs outgoing calls in development mode.
 *  - RESPONSE: Returns `response.data` directly (unwraps the Axios envelope).
 *              On error, normalizes via `errorHandler.normalizeError()` and
 *              re-throws a structured `ApiError` object.
 *
 * @module api/client
 */

import axios from 'axios'
import { normalizeError } from './errorHandler.js'

// ── Constants ──────────────────────────────────────────────────────────────────
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'
const DEFAULT_TIMEOUT_MS = 30_000
const IS_DEV = import.meta.env.DEV === true

// ── Axios instance ─────────────────────────────────────────────────────────────
const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: DEFAULT_TIMEOUT_MS,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json'
  }
})

// ── Request Interceptor ────────────────────────────────────────────────────────
/**
 * Logs outgoing requests in development mode.
 * In production builds this is a no-op (Vite tree-shakes the branch).
 */
apiClient.interceptors.request.use(
  (config) => {
    if (IS_DEV) {
      console.debug(
        `[ThreatLens API] ▶ ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`,
        config.params ? { params: config.params } : '',
        config.data ? { body: config.data } : ''
      )
    }
    return config
  },
  (error) => {
    // Request setup failed before it was even sent (e.g. serialization error)
    if (IS_DEV) {
      console.error('[ThreatLens API] Request setup error:', error)
    }
    return Promise.reject(normalizeError(error))
  }
)

// ── Response Interceptor ───────────────────────────────────────────────────────
/**
 * SUCCESS path: unwrap `response.data` so callers receive plain objects rather
 * than the full Axios response envelope.
 *
 * ERROR path: all HTTP error codes (4xx / 5xx) and network errors are funneled
 * through `normalizeError()` and re-thrown as structured `ApiError` objects.
 * Components must catch these with `isApiError()` to distinguish API failures
 * from unexpected JavaScript exceptions.
 */
apiClient.interceptors.response.use(
  (response) => {
    if (IS_DEV) {
      console.debug(
        `[ThreatLens API] ✅ ${response.status} ${response.config.url}`,
        response.data
      )
    }
    // Return the data payload directly — callers get `{ id, name, ... }`
    // instead of `{ data: { id, name, ... }, status: 200, headers: ... }`
    return response.data
  },
  (error) => {
    const apiError = normalizeError(error)

    if (IS_DEV) {
      console.error(
        `[ThreatLens API] ❌ ${apiError.status} [${apiError.code}]`,
        apiError.message
      )
    }

    // Re-throw a normalized ApiError — NEVER the raw AxiosError
    return Promise.reject(apiError)
  }
)

export default apiClient
