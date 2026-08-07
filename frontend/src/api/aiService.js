/**
 * AI Service — ThreatLens Frontend
 *
 * Stage A.6 — AI Assistant & Reports Integration.
 *
 * Provides API queries to query the AI Investigation Assistant Q&A chatbot
 * and trigger executive/analyst Markdown report compilation.
 *
 * @module api/aiService
 */

import { apiClient } from './index.js'

/**
 * Sends a conversational query to the AI Investigation Assistant.
 *
 * @param {string} indicator - The URL or domain context
 * @param {string} query - The analyst's question
 * @param {Object} [context={}] - Page's current telemetry context
 * @returns {Promise<Object>} AssistantResponse model
 */
export async function askQuestion(indicator, query, context = {}) {
  return apiClient.post('/ai/ask', {
    indicator,
    query,
    evidence: context.evidence || null,
    risk_assessment: context.risk_assessment || null,
    campaign_details: context.campaign_details || null
  })
}

/**
 * Compiles a detailed, technical incident report summary for SOC analysts.
 *
 * @param {string} indicator
 * @param {Object} [context={}]
 * @returns {Promise<Object>} AnalystReport model
 */
export async function getAnalystReport(indicator, context = {}) {
  return apiClient.post('/ai/report/analyst', {
    indicator,
    evidence: context.evidence || null,
    risk_assessment: context.risk_assessment || null,
    campaign_details: context.campaign_details || null
  })
}

/**
 * Compiles a high-level executive business impact summary for leadership presentation.
 *
 * @param {string} indicator
 * @param {Object} [context={}]
 * @returns {Promise<Object>} ExecutiveSummary model
 */
export async function getExecutiveSummary(indicator, context = {}) {
  return apiClient.post('/ai/report/executive', {
    indicator,
    evidence: context.evidence || null,
    risk_assessment: context.risk_assessment || null,
    campaign_details: context.campaign_details || null
  })
}

export default { askQuestion, getAnalystReport, getExecutiveSummary }
