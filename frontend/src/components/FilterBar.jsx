import React, { useState } from 'react'
import { useMail } from '../context/MailContext.jsx'
import { searchEmails } from '../api.js'

export default function FilterBar() {
  const { dispatch } = useMail()
  const [local, setLocal] = useState({ sender: '', keyword: '', dateAfter: '', unreadOnly: false })

  const apply = async () => {
    dispatch({ type: 'SET_FILTERS', payload: local })
    dispatch({ type: 'SET_LOADING', payload: true })
    const results = await searchEmails({
      sender: local.sender || undefined,
      keyword: local.keyword || undefined,
      date_after: local.dateAfter ? local.dateAfter.replaceAll('-', '/') : undefined,
      unread_only: local.unreadOnly,
    })
    dispatch({ type: 'SET_EMAILS', payload: results })
    dispatch({ type: 'SET_LOADING', payload: false })
  }

  return (
    <div className="flex flex-wrap gap-2 items-center p-3 border-b border-gray-200 bg-gray-50">
      <input
        placeholder="From..."
        className="border rounded px-2 py-1 text-sm"
        value={local.sender}
        onChange={(e) => setLocal({ ...local, sender: e.target.value })}
      />
      <input
        placeholder="Keyword..."
        className="border rounded px-2 py-1 text-sm"
        value={local.keyword}
        onChange={(e) => setLocal({ ...local, keyword: e.target.value })}
      />
      <input
        type="date"
        className="border rounded px-2 py-1 text-sm"
        value={local.dateAfter}
        onChange={(e) => setLocal({ ...local, dateAfter: e.target.value })}
      />
      <label className="text-sm flex items-center gap-1">
        <input
          type="checkbox"
          checked={local.unreadOnly}
          onChange={(e) => setLocal({ ...local, unreadOnly: e.target.checked })}
        />
        Unread only
      </label>
      <button onClick={apply} className="bg-indigo-600 text-white rounded px-3 py-1 text-sm hover:bg-indigo-700">
        Apply
      </button>
    </div>
  )
}
