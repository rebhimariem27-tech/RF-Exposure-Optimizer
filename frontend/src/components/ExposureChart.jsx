export default function ExposureChart({ history = [] }) {
  if (!history.length) return null
  const width = 720
  const height = 210
  const padding = 24
  const min = Math.min(...history)
  const max = Math.max(...history)
  const span = max - min || 1
  const points = history.map((value, index) => {
    const x = padding + (index / Math.max(history.length - 1, 1)) * (width - 2 * padding)
    const y = height - padding - ((value - min) / span) * (height - 2 * padding)
    return `${x},${y}`
  }).join(' ')
  return (
    <div className="chart-card">
      <div className="section-heading"><div><h3>Convergence du PSO</h3><p className="muted">Meilleure fitness à chaque itération</p></div></div>
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Courbe de convergence du PSO">
        <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} className="axis" />
        <line x1={padding} y1={padding} x2={padding} y2={height - padding} className="axis" />
        <polyline points={points} className="chart-line" />
      </svg>
      <div className="chart-labels"><span>Itération 1</span><span>Itération {history.length}</span></div>
    </div>
  )
}
