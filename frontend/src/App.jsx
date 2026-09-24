import React, { useEffect, useState } from 'react'
import { useMail } from './context/MailContext.jsx'
import { authStatus, loginUrl } from './api.js'
import Sidebar from './components/Sidebar.jsx'
import Inbox from './components/Inbox.jsx'
import Sent from './components/Sent.jsx'
import Compose from './components/Compose.jsx'
import EmailDetail from './components/EmailDetail.jsx'
import AssistantPanel from './components/AssistantPanel.jsx'

export default function App() {
  const { state } = useMail()
  const [authed, setAuthed] = useState(null)

  useEffect(() => {
    authStatus()
      .then((r) => setAuthed(r.authenticated))
      .catch(() => setAuthed(false))
  }, [])

  if (authed === null) {
    return <div className="h-screen flex items-center justify-center text-gray-400">Checking login...</div>
  }

  if (!authed) {
    return (
      <div className="h-screen flex flex-col items-center justify-center gap-4">
        <div className="text-xl font-semibold text-indigo-700">Nebula Mail</div>
        <a href={loginUrl()} className="bg-indigo-600 text-white rounded-lg px-5 py-2.5 hover:bg-indigo-700">
          Sign in with Google
        </a>
      </div>
    )
  }

  return (
    <div className="h-screen flex">
      <Sidebar />
      {state.view === 'inbox' && <Inbox />}
      {state.view === 'sent' && <Sent />}
      {state.view === 'compose' && <Compose />}
      {state.view === 'detail' && <EmailDetail />}
      <AssistantPanel />
    </div>
  )
}
