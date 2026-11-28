const METRICS = [
  ['sar10g_w_kg', 'SAR proxy', 'W/kg'],
  ['delta_t_max_k', 'Élévation thermique', 'K'],
  ['bitrate_mbps', 'Débit', 'Mbps'],
  ['sinr_db', 'SINR', 'dB'],
  ['energy_consumption_j', 'Énergie', 'J'],
  ['infrastructure_cost', 'Coût infrastructure', 'unités'],
]

function format(value) {
  if (value === null || value === undefined) return '—'
  return Number(value).toLocaleString('fr-FR', { maximumFractionDigits: 6 })
}

export default function MetricsCards({ metrics }) {
  if (!metrics) return null
  return (
    <div className="metrics-grid">
      {METRICS.map(([key, label, unit]) => (
        <article className="metric-card" key={key}>
          <span className="muted">{label}</span>
          <strong>{format(metrics[key])}</strong>
          <small>{unit}</small>
        </article>
      ))}
    </div>
  )
}
