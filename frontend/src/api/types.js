/**
 * API Error Types — ThreatLens Frontend
 *
 * Defines the canonical shapes for API errors and responses across the entire
 * frontend. All API service files must use these types when throwing or
 * catching errors, ensuring consistent handling at the component layer.
 *
 * NOTE: This project uses plain JavaScript with JSDoc annotations (no
 * TypeScript). These are documentation-only type definitions.
 *
 * @module api/types
 */

/**
 * Represents a single FastAPI validation error item.
 * FastAPI 422 responses return an array of these under the `detail` key.
 *
 * @typedef {Object} FastApiValidationError
 * @property {string[]} loc   - Location path of the invalid field (e.g. ["body", "url"])
 * @property {string}   msg   - Human-readable error message
 * @property {string}   type  - Pydantic error type identifier
 */

/**
 * Canonical API error structure used across all ThreatLens services.
 *
 * @typedef {Object} ApiError
 * @property {number}  status      - HTTP status code (e.g. 404, 422, 500)
 * @property {string}  message     - Human-readable summary of the error
 * @property {string}  [code]      - Optional machine-readable error code
 * @property {FastApiValidationError[]} [validationErrors] - Populated for 422 errors only
 * @property {boolean} isApiError  - Discriminant flag; always `true`
 */

/**
 * Standard pagination parameters for list endpoints.
 *
 * @typedef {Object} PaginationParams
 * @property {number} [skip=0]    - Number of records to skip
 * @property {number} [limit=20]  - Maximum number of records to return
 */

/**
 * Standard paginated list response wrapper.
 *
 * @template T
 * @typedef {Object} PaginatedResponse
 * @property {T[]}    items  - List of items for this page
 * @property {number} total  - Total number of records available
 * @property {number} skip   - Records skipped
 * @property {number} limit  - Requested page size
 */

export default {}
