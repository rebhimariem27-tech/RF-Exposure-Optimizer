import MetricsCards from '../components/MetricsCards'
import ResultsTable from '../components/ResultsTable'
import ExposureChart from '../components/ExposureChart'

export default function Results({ result }) {
  if (!result) return <section className="empty-state"><h2>Aucun résultat disponible</h2><p>Lance une simulation ou une optimisation pour afficher les résultats ici.</p></section>
  if (result.optimization) {
    return <section className="page-section"><div className="page-title"><div><div className="eyebrow">ANALYSE</div><h2>Résultats de l’optimisation</h2></div></div><div className="summary-grid"><article className="summary-card"><span className="muted">Puissance</span><strong>{result.optimization.best_design.tx_power_w.toFixed(3)} W</strong></article><article className="summary-card"><span className="muted">Antennes</span><strong>{result.optimization.best_design.n_antennas}</strong></article><article className="summary-card"><span className="muted">Faisabilité</span><strong>{result.optimization.feasible ? 'Oui' : 'Non'}</strong></article></div><MetricsCards metrics={result.optimization.metrics} /><ExposureChart history={result.optimization.pso.history} /><ResultsTable baseline={result.baseline.metrics} optimized={result.optimization.metrics} /></section>
  }
  return <section className="page-section"><div className="page-title"><div><div className="eyebrow">ANALYSE</div><h2>Résultats de la simulation</h2></div></div><MetricsCards metrics={result.metrics} /><pre className="json-output">{JSON.stringify(result.model_scope, null, 2)}</pre></section>
}
