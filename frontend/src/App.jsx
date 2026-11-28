import { useState } from 'react'
import Dashboard from './pages/Dashboard'
import Simulation from './pages/Simulation'
import Optimization from './pages/Optimization'
import Results from './pages/Results'
import './styles.css'

const NAV = [
  ['dashboard', 'Vue générale'],
  ['simulation', 'Simulation'],
  ['optimization', 'Optimisation'],
  ['results', 'Résultats'],
]

export default function App() {
  const [page, setPage] = useState('dashboard')
  const [latestResult, setLatestResult] = useState(null)
  return <div className="app-shell">
    <header className="topbar">
      <div className="brand"><div className="brand-mark">RF</div><div><strong>RF Exposure Optimizer</strong><span>Simulation · Analyse · Optimisation</span></div></div>
      <nav>{NAV.map(([id, label]) => <button key={id} className={page === id ? 'nav-active' : ''} onClick={() => setPage(id)}>{label}</button>)}</nav>
    </header>
    <main>
      {page === 'dashboard' && <Dashboard onNavigate={setPage} />}
      {page === 'simulation' && <Simulation onResult={(result) => setLatestResult(result)} />}
      {page === 'optimization' && <Optimization onResult={(result) => setLatestResult(result)} />}
      {page === 'results' && <Results result={latestResult} />}
    </main>
    <footer>RF Exposure Optimizer · Prototype de recherche · Modèles à interpréter selon leurs hypothèses</footer>
  </div>
}
