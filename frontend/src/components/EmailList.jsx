import React from 'react'
import { useMail } from '../context/MailContext.jsx'
import { getMessage } from '../api.js'

export default function EmailList() {
  const { state, dispatch } = useMail()

  const open = async (id) => {
    const full = await getMessage(id)
    dispatch({ type: 'SET_SELECTED_EMAIL', payload: full })
  }

  if (state.loading) return <div className="p-6 text-gray-400">Loading...</div>
  if (!state.emails || !state.emails.length) return <div className="p-6 text-gray-400">No emails to show.</div>

  return (
    <div className="divide-y divide-gray-100">
      {state.emails.map((email) => (
        <button
          key={email.id}
          onClick={() => open(email.id)}
          className="w-full text-left px-5 py-3 hover:bg-gray-50 flex flex-col gap-0.5"
        >
          <div className="flex justify-between items-center">
            <span className={`text-sm ${email.unread ? 'font-semibold text-gray-900' : 'text-gray-600'}`}>
              {email.sender}
            </span>
            <span className="text-xs text-gray-400">{email.date}</span>
          </div>
          <div className={`text-sm ${email.unread ? 'font-semibold' : ''}`}>{email.subject}</div>
          <div className="text-xs text-gray-400 truncate">{email.snippet}</div>
        </button>
      ))}
    </div>
  )
}
