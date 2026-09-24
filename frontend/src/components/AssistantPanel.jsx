import React, { useState, useRef, useEffect } from 'react'
import { useMail } from '../context/MailContext.jsx'
import { askAssistant } from '../api.js'

export default function AssistantPanel() {
  const { state, dispatch } = useMail()
  const [messages, setMessages] = useState([
    { role: 'assistant', text: "Hi! Try: \"send an email to john@example.com about tomorrow's meeting\" or \"show unread emails from this week\"." },
  ])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const applyAction = (action) => {
    if (!action || action.type === 'none') return

    if (action.type === 'compose_email') {
      const p = action.payload
      dispatch({
        type: 'SET_COMPOSE_FIELDS',
        payload: {
          to: p.to,
          subject: p.subject,
          body: p.body,
          threadId: p.thread_id || null,
          inReplyToMsgId: p.in_reply_to_msg_id || null,
          filledByAssistant: true,
        },
      })
    } else if (action.type === 'search_results') {
      dispatch({ type: 'SET_EMAILS', payload: action.payload.emails })
      dispatch({ type: 'SET_VIEW', payload: 'inbox' })
    } else if (action.type === 'open_email') {
      dispatch({ type: 'SET_SELECTED_EMAIL', payload: action.payload.email })
    }
  }

  const submit = async (e) => {
    e.preventDefault()
    const text = input.trim()
    if (!text) return
    setMessages((m) => [...m, { role: 'user', text }])
    setInput('')
    setBusy(true)
    try {
      const res = await askAssistant(text, {
        current_view: state.view,
        open_email_id: state.selectedEmail?.id || null,
      })
      setMessages((m) => [...m, { role: 'assistant', text: res.reply }])
      applyAction(res.action)
    } catch (err) {
      setMessages((m) => [...m, { role: 'assistant', text: 'Something went wrong — is the backend running and are you logged in?' }])
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="w-80 shrink-0 border-l border-gray-200 flex flex-col bg-gray-50">
      <div className="px-4 py-3 font-semibold border-b border-gray-200">Assistant</div>
      <div className="flex-1 overflow-y-auto p-3 flex flex-col gap-2">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`text-sm px-3 py-2 rounded-lg max-w-[90%] ${
              m.role === 'user' ? 'bg-indigo-600 text-white self-end' : 'bg-white border border-gray-200 self-start'
            }`}
          >
            {m.text}
          </div>
        ))}
        {busy && <div className="text-xs text-gray-400 self-start">thinking...</div>}
        <div ref={bottomRef} />
      </div>
      <form onSubmit={submit} className="p-3 border-t border-gray-200 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Tell the assistant what to do..."
          className="flex-1 border rounded px-3 py-2 text-sm"
        />
        <button type="submit" disabled={busy} className="bg-indigo-600 text-white rounded px-3 py-2 text-sm hover:bg-indigo-700 disabled:opacity-50">
          Send
        </button>
      </form>
    </div>
  )
}
