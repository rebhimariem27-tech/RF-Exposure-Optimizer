import { useState } from 'react'
import MetricsCards from '../components/MetricsCards'
import { runSimulation } from '../services/api'

const initial = { txPower: 21, antennas: 8, frequency: 2.5, distance: 50, bandwidth: 100, duration: 360 }

export default function Simulation({ onResult }) {
  const [form, setForm] = useState(initial)
  const [data, setData] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const update = (key, value) => setForm((old) => ({ ...old, [key]: value }))

  async function submit(event) {
    event.preventDefault(); setBusy(true); setError(''); setData(null)
    try {
      const result = await runSimulation({
        design: { tx_power_w: Number(form.txPower), n_antennas: Number(form.antennas) },
        scenario: { frequency_hz: Number(form.frequency) * 1e9, distance_m: Number(form.distance), bandwidth_hz: Number(form.bandwidth) * 1e6, operation_duration_s: Number(form.duration) },
      })
      setData(result); onResult?.(result)
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }

  return <section className="page-section">
    <div className="page-title"><div><div className="eyebrow">MOTEUR PHYSIQUE</div><h2>Simulation d’un scénario réseau</h2><p className="muted">Définis les caractéristiques de la station et de la liaison radio.</p></div></div>
    <form className="panel form-grid" onSubmit={submit}>
      <label>Puissance d’émission (W)<input type="number" min="0.01" step="0.1" value={form.txPower} onChange={e => update('txPower', e.target.value)} required /></label>
      <label>Nombre d’antennes<select value={form.antennas} onChange={e => update('antennas', e.target.value)}>{[2,4,8,16].map(n => <option key={n}>{n}</option>)}</select></label>
      <label>Fréquence (GHz)<input type="number" min="0.1" max="6" step="0.01" value={form.frequency} onChange={e => update('frequency', e.target.value)} required /></label>
      <label>Distance (m)<input type="number" min="0.1" step="1" value={form.distance} onChange={e => update('distance', e.target.value)} required /></label>
      <label>Bande passante (MHz)<input type="number" min="0.1" step="1" value={form.bandwidth} onChange={e => update('bandwidth', e.target.value)} required /></label>
      <label>Durée (secondes)<input type="number" min="0.1" step="1" value={form.duration} onChange={e => update('duration', e.target.value)} required /></label>
      <div className="form-actions"><button disabled={busy}>{busy ? 'Simulation en cours…' : 'Exécuter la simulation'}</button></div>
    </form>
    {error && <div className="error-box">{error}</div>}
    {data && <div className="result-section"><div className="section-heading"><div><h3>Résultats de la simulation</h3><p className="muted">{data.design.tx_power_w} W · {data.design.n_antennas} antennes · {(data.scenario.frequency_hz / 1e9).toFixed(2)} GHz</p></div></div><MetricsCards metrics={data.metrics} /><p className="notice">Le SAR affiché est un proxy 1D sur une colonne de tissus. Consulte les hypothèses retournées par l’API avant toute interprétation physique.</p></div>}
  </section>
}
