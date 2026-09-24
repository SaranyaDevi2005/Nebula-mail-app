import React from 'react'
import { useMail } from '../context/MailContext.jsx'

export default function Sidebar() {
  const { state, dispatch } = useMail()

  const item = (view, label) => (
    <button
      onClick={() => dispatch({ type: 'SET_VIEW', payload: view })}
      className={`text-left px-4 py-2 rounded-lg w-full ${
        state.view === view ? 'bg-indigo-600 text-white' : 'hover:bg-gray-100 text-gray-700'
      }`}
    >
      {label}
    </button>
  )

  return (
    <div className="w-48 shrink-0 border-r border-gray-200 p-3 flex flex-col gap-1">
      <div className="font-bold text-lg px-4 py-2 text-indigo-700">Nebula Mail</div>
      {item('inbox', 'Inbox')}
      {item('sent', 'Sent')}
      <button
        onClick={() =>
          dispatch({ type: 'SET_COMPOSE_FIELDS', payload: { to: '', subject: '', body: '' } })
        }
        className="mt-2 mx-4 bg-indigo-600 text-white rounded-lg px-4 py-2 hover:bg-indigo-700"
      >
        Compose
      </button>
    </div>
  )
}
