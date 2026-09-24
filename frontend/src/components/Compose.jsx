import React, { useState, useEffect } from 'react'
import { useMail } from '../context/MailContext.jsx'
import { sendEmail } from '../api.js'

export default function Compose() {
  const { state, dispatch } = useMail()
  const [fields, setFields] = useState(state.composeFields)
  const [sent, setSent] = useState(false)

  // keep local form in sync when the assistant (re)fills composeFields
  useEffect(() => {
    setFields(state.composeFields)
    setSent(false)
  }, [state.composeFields])

  const submit = async (e) => {
    e.preventDefault()
    await sendEmail({
      to: fields.to,
      subject: fields.subject,
      body: fields.body,
      thread_id: fields.threadId,
      in_reply_to_msg_id: fields.inReplyToMsgId,
    })
    setSent(true)
    dispatch({ type: 'RESET_COMPOSE' })
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="px-5 py-3 font-semibold border-b border-gray-200">Compose</div>
      <form onSubmit={submit} className="p-5 flex flex-col gap-3 max-w-2xl">
        {fields.filledByAssistant && (
          <div className="rounded border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
            Drafted by the assistant — review before sending.
          </div>
        )}
        {sent && <div className="text-green-600 text-sm">Sent!</div>}
        <input
          placeholder="To"
          className="border rounded px-3 py-2"
          value={fields.to}
          onChange={(e) => setFields({ ...fields, to: e.target.value })}
          required
        />
        <input
          placeholder="Subject"
          className="border rounded px-3 py-2"
          value={fields.subject}
          onChange={(e) => setFields({ ...fields, subject: e.target.value })}
          required
        />
        <textarea
          placeholder="Body"
          rows={10}
          className="border rounded px-3 py-2"
          value={fields.body}
          onChange={(e) => setFields({ ...fields, body: e.target.value })}
          required
        />
        <button type="submit" className="bg-indigo-600 text-white rounded px-4 py-2 w-fit hover:bg-indigo-700">
          Send
        </button>
      </form>
    </div>
  )
}
