import React, { useState, useRef, useEffect } from 'react'
import { askQuestion } from '../../api'

/**
 * AI Assistant Chat Interface — ThreatLens Frontend
 *
 * Stage A.6 — AI Assistant Chatbot Component.
 *
 * Provides a conversational SOC analyst chat box embedded inside the investigation workspace.
 * Allows analysts to type custom prompts or click pre-selected questions (e.g. "What DNS features are risky?").
 * Sends the queries along with the page's current telemetry payload and maps the LLM messages.
 */
export default function AiAssistantChat({ indicator, context }) {
  const [messages, setMessages] = useState([
    {
      sender: 'ai',
      text: `Hello Analyst. I have loaded the investigation context for **${indicator}**. Ask me any security question about this threat target.`,
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const presetQuestions = [
    'Why is this indicator rated risky?',
    'What infrastructure properties does it share?',
    'What are the recommended containment actions?'
  ]

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading])

  const handleSend = async (textToSend) => {
    const query = (textToSend || input).trim()
    if (!query) return

    // Clear input if sending custom typing
    if (!textToSend) setInput('')

    // Append user message
    const userMsg = { sender: 'user', text: query, timestamp: new Date() }
    setMessages(prev => [...prev, userMsg])
    setLoading(true)

    try {
      // Execute live QA assistant call
      const res = await askQuestion(indicator, query, context)
      
      const aiMsg = {
        sender: 'ai',
        text: res.message || 'No clear response compiled by gateway.',
        actions: res.suggested_actions || [],
        confidence: res.confidence,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, aiMsg])
    } catch (err) {
      const errorMsg = {
        sender: 'ai',
        text: `Error contacting the AI assistant: ${err.message || 'Server timeout.'}. Please verify settings.`,
        isError: true,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMsg])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-[480px] bg-[#090d16] border border-[#1a2336] rounded-xl overflow-hidden shadow-md">
      {/* Messages list */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 font-sans text-xs">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex flex-col max-w-[85%] ${m.sender === 'user' ? 'ml-auto items-end' : 'mr-auto items-start'}`}
          >
            <div
              className={`p-3 rounded-xl border leading-relaxed ${
                m.sender === 'user'
                  ? 'bg-brand-950/20 border-brand-900/30 text-slate-200 rounded-br-none'
                  : m.isError
                  ? 'bg-rose-950/15 border-rose-900/30 text-rose-400 rounded-bl-none'
                  : 'bg-[#0c121e] border-[#151d2c] text-slate-300 rounded-bl-none'
              }`}
            >
              <div className="break-words whitespace-pre-wrap">{m.text}</div>
              
              {/* Render suggested actions if any */}
              {m.actions && m.actions.length > 0 && (
                <div className="mt-3 pt-2.5 border-t border-[#1a2336] space-y-1.5 w-full">
                  <span className="block text-[8px] uppercase tracking-wider text-slate-500 font-extrabold">
                    Suggested SOC Actions:
                  </span>
                  <div className="flex flex-col gap-1">
                    {m.actions.map((act, i) => (
                      <div
                        key={i}
                        className="px-2 py-1 rounded bg-[#101726]/60 border border-[#152035] text-[10px] text-brand-300 font-semibold"
                      >
                        {act.title || act}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {m.confidence && (
                <div className="mt-2 text-[8px] text-slate-500 font-mono text-right font-semibold">
                  Confidence Score: {m.confidence}
                </div>
              )}
            </div>
            
            <span className="text-[8px] text-slate-500 font-mono mt-1 px-1">
              {m.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
        ))}

        {loading && (
          <div className="flex flex-col items-start max-w-[85%] mr-auto">
            <div className="p-3 rounded-xl bg-[#0c121e] border-[#151d2c] rounded-bl-none flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-brand-400 animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="w-1.5 h-1.5 rounded-full bg-brand-400 animate-bounce" style={{ animationDelay: '150ms' }} />
              <span className="w-1.5 h-1.5 rounded-full bg-brand-400 animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Preset Questions list (visible when idle) */}
      {!loading && (
        <div className="p-3 border-t border-[#1a2336]/60 bg-[#070a11]/40 flex gap-2 overflow-x-auto whitespace-nowrap scrollbar-none">
          {presetQuestions.map((q, i) => (
            <button
              key={i}
              type="button"
              onClick={() => handleSend(q)}
              className="px-2.5 py-1.5 rounded-lg bg-[#0e1422] border border-[#1a2336] hover:border-brand-500 text-[10px] font-bold text-slate-400 hover:text-slate-200 transition-colors uppercase tracking-wider"
            >
              {q}
            </button>
          ))}
        </div>
      )}

      {/* Input panel form */}
      <form
        onSubmit={(e) => {
          e.preventDefault()
          handleSend()
        }}
        className="p-3 border-t border-[#1a2336] bg-[#0c121e] flex gap-2"
      >
        <input
          type="text"
          placeholder="Ask a custom threat context question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
          className="flex-1 px-3 py-2 bg-[#0e1422] border border-[#1a2336] rounded-lg text-[11px] text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-all disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="px-4 bg-brand-600 hover:bg-brand-500 text-slate-900 font-extrabold rounded-lg text-xs uppercase tracking-wider transition-colors disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </div>
  )
}
