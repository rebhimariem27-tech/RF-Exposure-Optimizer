# Validation protocol

## Automated software tests

Run `pytest -q` from `backend/`. Tests cover:

- Tissue-grid consistency and basic exposure scaling.
- Non-negative and monotonic thermal response for the tested inputs.
- Free-space field and link-metric behavior.
- Integrated simulator output structure.
- Objective, AHP, constraint, penalty, and PSO behavior.
- API health, simulation, optimization, and invalid-input behavior.

Passing unit tests establishes software-level consistency for tested cases; it does not validate the model against measurements or regulatory reference tools.

## Physical-model validation still required

1. Compare dielectric tissue properties against frequency-matched authoritative datasets.
2. Compare field propagation against analytical cases and/or a validated EM solver.
3. Compare SAR calculations against a 3-D dosimetry reference (not only a 1-D column proxy).
4. Validate thermal predictions with an appropriate bioheat reference and realistic perfusion/boundary conditions.
5. Validate link metrics against a documented link budget and realistic interference/channel assumptions.
6. Perform sensitivity analysis over frequency, distance, tissue parameters, bandwidth, and environmental assumptions.

Record reference source, frequency, geometry, units, tolerances, and errors for every comparison.
