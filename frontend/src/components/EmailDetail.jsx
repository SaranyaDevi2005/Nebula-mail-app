import React from 'react'
import { useMail } from '../context/MailContext.jsx'

export default function EmailDetail() {
  const { state, dispatch } = useMail()
  const email = state.selectedEmail
  if (!email) return <div className="p-6 text-gray-400">No email selected.</div>

  const reply = () => {
    dispatch({
      type: 'SET_COMPOSE_FIELDS',
      payload: {
        to: email.sender,
        subject: email.subject.toLowerCase().startsWith('re:') ? email.subject : `Re: ${email.subject}`,
        body: `\n\nOn ${email.date}, ${email.sender} wrote:\n${email.body?.slice(0, 300) || ''}`,
        threadId: email.threadId,
        inReplyToMsgId: email.id,
      },
    })
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="px-5 py-3 border-b border-gray-200 flex justify-between items-center">
        <div>
          <div className="font-semibold text-lg">{email.subject}</div>
          <div className="text-sm text-gray-500">
            {email.sender} · {email.date}
          </div>
        </div>
        <button onClick={reply} className="bg-indigo-600 text-white rounded px-3 py-1.5 text-sm hover:bg-indigo-700">
          Reply
        </button>
      </div>
      <div className="p-5 whitespace-pre-wrap text-sm text-gray-800 overflow-y-auto">{email.body}</div>
    </div>
  )
}
