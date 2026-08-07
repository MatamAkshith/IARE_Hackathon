/**
 * API Layer — Public Exports
 *
 * Service files should import from this barrel:
 *   import apiClient from '../api'
 *   import { isApiError } from '../api'
 *
 * @module api
 */
export { default as apiClient } from './client.js'
export { normalizeError, isApiError } from './errorHandler.js'
