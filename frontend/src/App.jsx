import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import DataTable from './pages/DataTable'
import TaskManager from './pages/TaskManager'
import Settings from './pages/Settings'
import QueryEditor from './pages/QueryEditor'

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/data-table" element={<DataTable />} />
          <Route path="/task-manager" element={<TaskManager />} />
          <Route path="/query-editor" element={<QueryEditor />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App
