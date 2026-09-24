import React, { createContext, useContext, useReducer } from 'react'

const MailContext = createContext(null)

const initialState = {
  view: 'inbox',            // 'inbox' | 'sent' | 'compose' | 'detail'
  emails: [],
  selectedEmail: null,
  composeFields: { to: '', subject: '', body: '', threadId: null, inReplyToMsgId: null, filledByAssistant: false },
  filters: { sender: '', keyword: '', dateAfter: '', dateBefore: '', unreadOnly: false },
  loading: false,
  lastAssistantReply: '',
}

function reducer(state, action) {
  switch (action.type) {
    case 'SET_VIEW':
      return { ...state, view: action.payload }
    case 'SET_EMAILS':
      return { ...state, emails: action.payload }
    case 'SET_SELECTED_EMAIL':
      return { ...state, selectedEmail: action.payload, view: 'detail' }
    case 'SET_COMPOSE_FIELDS':
      return {
        ...state,
        composeFields: {
          ...state.composeFields,
          ...action.payload,
          filledByAssistant: action.payload.filledByAssistant ?? state.composeFields.filledByAssistant,
        },
        view: 'compose',
      }
    case 'RESET_COMPOSE':
      return { ...state, composeFields: initialState.composeFields }
    case 'SET_FILTERS':
      return { ...state, filters: { ...state.filters, ...action.payload } }
    case 'SET_LOADING':
      return { ...state, loading: action.payload }
    case 'SET_ASSISTANT_REPLY':
      return { ...state, lastAssistantReply: action.payload }
    default:
      return state
  }
}

export function MailProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState)
  return <MailContext.Provider value={{ state, dispatch }}>{children}</MailContext.Provider>
}

export function useMail() {
  const ctx = useContext(MailContext)
  if (!ctx) throw new Error('useMail must be used within MailProvider')
  return ctx
}
