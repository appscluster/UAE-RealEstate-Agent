import React from 'react'
import { createRoot } from 'react-dom/client'
import '@fontsource/figtree/400.css'
import '@fontsource/figtree/600.css'
import '@fontsource/literata/600.css'
import './styles.css'
import { App } from './App'
import { ExplainPage } from './ExplainPage'

const path = window.location.pathname.replace(/\/$/, '') || '/'
createRoot(document.getElementById('root')!).render(path === '/explain' ? <ExplainPage /> : <App />)
