import { useState } from 'react'
import MetricsCards from '../components/MetricsCards'
import ResultsTable from '../components/ResultsTable'
import ExposureChart from '../components/ExposureChart'
import { runOptimization } from '../services/api'

export default function Optimization({ onResult }) {
  const [form, setForm] = useState({ particles: 12, iterations: 20, duration: 360, minPower: 1, maxPower: 21, targetBitrate: 100, frequency: 2.5, distance: 50, bandwidth: 100 })
  const [data, setData] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const update = (key, value) => setForm(old => ({ ...old, [key]: value }))

  async function submit(event) {
    event.preventDefault(); setBusy(true); setError(''); setData(null)
    try {
      const payload = {
        scenario: { frequency_hz: Number(form.frequency) * 1e9, distance_m: Number(form.distance), bandwidth_hz: Number(form.bandwidth) * 1e6, operation_duration_s: Number(form.duration) },
        pso: { n_particles: Number(form.particles), n_iterations: Number(form.iterations), seed: 42 },
        bounds: { min_tx_power_w: Number(form.minPower), max_tx_power_w: Number(form.maxPower), min_antennas: 2, max_antennas: 16 },
        allowed_antennas: [2,4,8,16],
        constraints: { sar_limit_w_kg: 2, delta_t_limit_k: 2, minimum_bitrate_mbps: Number(form.targetBitrate), minimum_sinr_db: 5 },
      }
      const result = await runOptimization(payload)
      setData(result); onResult?.(result)
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }

  const optimization = data?.optimization
  return <section className="page-section">
    <div className="page-title"><div><div className="eyebrow">MOTEUR D’OPTIMISATION</div><h2>Recherche d’une configuration</h2><p className="muted">Le PSO teste des couples puissance / nombre d’antennes et évalue chacun avec le simulateur.</p></div></div>
    <form className="panel form-grid" onSubmit={submit}>
      <label>Nombre de particules<input type="number" min="2" max="200" value={form.particles} onChange={e => update('particles', e.target.value)} /></label>
      <label>Nombre d’itérations<input type="number" min="1" max="1000" value={form.iterations} onChange={e => update('iterations', e.target.value)} /></label>
      <label>Puissance minimale (W)<input type="number" min="0.01" step="0.1" value={form.minPower} onChange={e => update('minPower', e.target.value)} /></label>
      <label>Puissance maximale (W)<input type="number" min="0.02" step="0.1" value={form.maxPower} onChange={e => update('maxPower', e.target.value)} /></label>
      <label>Fréquence (GHz)<input type="number" min="0.1" max="6" step="0.01" value={form.frequency} onChange={e => update('frequency', e.target.value)} /></label>
      <label>Distance (m)<input type="number" min="0.1" step="1" value={form.distance} onChange={e => update('distance', e.target.value)} /></label>
      <label>Bande passante (MHz)<input type="number" min="0.1" step="1" value={form.bandwidth} onChange={e => update('bandwidth', e.target.value)} /></label>
      <label>Durée (secondes)<input type="number" min="0.1" step="1" value={form.duration} onChange={e => update('duration', e.target.value)} /></label>
      <label>Débit minimal (Mbps)<input type="number" min="0.1" step="1" value={form.targetBitrate} onChange={e => update('targetBitrate', e.target.value)} /></label>
      <div className="form-actions"><button disabled={busy}>{busy ? 'Optimisation en cours…' : 'Lancer le PSO'}</button></div>
    </form>
    {error && <div className="error-box">{error}</div>}
    {data && <div className="result-section">
      <div className="section-heading"><div><h3>Configuration retenue par le PSO</h3><p className="muted">Meilleure fitness trouvée : {optimization.total_fitness.toFixed(6)}</p></div><span className={`status ${optimization.feasible ? 'status-ok' : 'status-warning'}`}>{optimization.feasible ? 'Contraintes respectées' : 'Contraintes non respectées'}</span></div>
      <div className="summary-grid"><article className="summary-card"><span className="muted">Puissance retenue</span><strong>{optimization.best_design.tx_power_w.toFixed(3)} W</strong></article><article className="summary-card"><span className="muted">Nombre d’antennes</span><strong>{optimization.best_design.n_antennas}</strong></article><article className="summary-card"><span className="muted">Fitness</span><strong>{optimization.total_fitness.toFixed(6)}</strong></article></div>
      <h3>Métriques optimisées</h3><MetricsCards metrics={optimization.metrics} />
      <ExposureChart history={optimization.pso.history} />
      <h3>Comparaison avant / après</h3><ResultsTable baseline={data.baseline.metrics} optimized={optimization.metrics} />
      <p className="notice">Une solution « faisable » signifie qu’elle respecte les contraintes numériques configurées dans ce prototype. Cela ne vaut pas certification réglementaire.</p>
    </div>}
  </section>
}
