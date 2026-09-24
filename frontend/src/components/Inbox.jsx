import React, { useEffect, useCallback } from 'react'
import { useMail } from '../context/MailContext.jsx'
import { getInbox } from '../api.js'
import EmailList from './EmailList.jsx'
import FilterBar from './FilterBar.jsx'

const POLL_MS = 45000 // real-time-sync trade-off: short polling instead of Gmail Pub/Sub push (see README)

export default function Inbox() {
  const { dispatch } = useMail()

  const load = useCallback(async () => {
    const data = await getInbox()
    dispatch({ type: 'SET_EMAILS', payload: data })
  }, [dispatch])

  useEffect(() => {
    dispatch({ type: 'SET_LOADING', payload: true })
    load().finally(() => dispatch({ type: 'SET_LOADING', payload: false }))
    const interval = setInterval(load, POLL_MS)
    return () => clearInterval(interval)
  }, [load, dispatch])

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="px-5 py-3 font-semibold border-b border-gray-200">Inbox</div>
      <FilterBar />
      <div className="flex-1 overflow-y-auto">
        <EmailList />
      </div>
    </div>
  )
}
