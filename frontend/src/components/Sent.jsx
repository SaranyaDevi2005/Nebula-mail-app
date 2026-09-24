import React, { useEffect } from 'react'
import { useMail } from '../context/MailContext.jsx'
import { getSent } from '../api.js'
import EmailList from './EmailList.jsx'

export default function Sent() {
  const { dispatch } = useMail()

  useEffect(() => {
    dispatch({ type: 'SET_LOADING', payload: true })
    getSent()
      .then((data) => dispatch({ type: 'SET_EMAILS', payload: data }))
      .finally(() => dispatch({ type: 'SET_LOADING', payload: false }))
  }, [dispatch])

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="px-5 py-3 font-semibold border-b border-gray-200">Sent</div>
      <div className="flex-1 overflow-y-auto">
        <EmailList />
      </div>
    </div>
  )
}
