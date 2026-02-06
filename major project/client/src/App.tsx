import { Link, Outlet } from 'react-router-dom'
import './App.css'

function App() {
  return (
    <div>
      <nav className="p-4 border-b flex gap-4">
        <Link to="/" className="text-blue-600 hover:underline">Home</Link>
        <Link to="/results" className="text-blue-600 hover:underline">Results</Link>
      </nav>
      <main className="p-4">
        <Outlet />
      </main>
    </div>
  )
}

export default App
