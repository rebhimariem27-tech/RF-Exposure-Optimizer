export default function Dashboard({ onNavigate }) {
  return (
    <section className="hero">
      <div className="eyebrow">OUTIL DE SIMULATION ET D’AIDE À LA DÉCISION</div>
      <h2>Étudier le compromis entre exposition RF et performances réseau.</h2>
      <p className="hero-copy">Configure un scénario radio, simule ses indicateurs physiques et réseau, puis lance le PSO pour explorer les puissances d’émission et les nombres d’antennes possibles.</p>
      <div className="hero-actions">
        <button onClick={() => onNavigate('simulation')}>Lancer une simulation</button>
        <button className="button-secondary" onClick={() => onNavigate('optimization')}>Lancer une optimisation</button>
      </div>
      <div className="info-grid">
        <article><span className="info-number">01</span><h3>Modèles physiques</h3><p>Propagation en espace libre, tissus multicouches, estimation SAR et réponse thermique 1D.</p></article>
        <article><span className="info-number">02</span><h3>Qualité réseau</h3><p>Puissance reçue, bruit, SINR et estimation du débit selon les hypothèses configurées.</p></article>
        <article><span className="info-number">03</span><h3>Optimisation PSO</h3><p>Recherche d’une configuration qui réduit la fitness tout en contrôlant les contraintes.</p></article>
      </div>
      <p className="notice"><strong>À lire :</strong> les indicateurs SAR 10 g et potentiel membranaire affichés sont des proxies du prototype, et non des résultats de conformité réglementaire ou une validation biologique.</p>
    </section>
  )
}
