const LABELS = {
  sar10g_w_kg: ['SAR proxy', 'W/kg'],
  delta_t_max_k: ['Élévation de température', 'K'],
  delta_vm_abs_v: ['Potentiel membranaire proxy', 'V'],
  energy_consumption_j: ['Énergie', 'J'],
  bitrate_mbps: ['Débit', 'Mbps'],
  infrastructure_cost: ['Coût infrastructure', 'unités'],
  sinr_db: ['SINR', 'dB'],
}

const fmt = (v) => Number(v).toLocaleString('fr-FR', { maximumFractionDigits: 6 })

export default function ResultsTable({ baseline, optimized }) {
  if (!baseline || !optimized) return null
  return (
    <div className="table-wrap">
      <table>
        <thead><tr><th>Indicateur</th><th>Initial</th><th>Optimisé</th><th>Écart</th></tr></thead>
        <tbody>
          {Object.entries(LABELS).map(([key, [label, unit]]) => {
            const before = baseline[key]
            const after = optimized[key]
            return <tr key={key}>
              <td>{label} <span className="muted">({unit})</span></td>
              <td>{fmt(before)}</td>
              <td>{fmt(after)}</td>
              <td>{fmt(after - before)}</td>
            </tr>
          })}
        </tbody>
      </table>
    </div>
  )
}
