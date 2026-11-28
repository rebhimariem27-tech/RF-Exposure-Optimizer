# Architecture — RF Exposure Optimizer

## Runtime flow

```text
React / Vite frontend
        | HTTP JSON
        v
FastAPI routes (/api/*)
        |
        v
API services (input-to-domain conversion)
        |
        +--------------------+
        |                    |
        v                    v
Simulation engine       Optimization problem
(antenna, propagation,  (objective, constraints,
tissues, exposure,       fitness, PSO)
thermal, membrane)             |
        |                      |
        +----------<-----------+
                   |
                   v
          JSON results to frontend
```

## Existing scientific core

- `app/models/`: physical and network calculations.
- `app/optimization/`: metrics, objective, constraints, fitness, PSO, and optimization problem.
- `app/api/services/`: calls the existing core without embedding calculations in HTTP routes.
- `app/api/routes/`: transport layer and HTTP status handling.
- `app/schemas.py`: Pydantic request validation.

## API routes

- `GET /api/health`
- `POST /api/simulation/run`
- `POST /api/optimization/run`
- Compatibility endpoints: `/`, `/health`, `/config/default`, `/config/validate`, `/antenna/analyze`.

Swagger/OpenAPI is available at `/docs` while the backend is running.

## Important design boundaries

The API layer must not reimplement the physical formulas. It validates and converts input data, calls a service, and serializes the returned result. The simulation service calls `simulate_network`; the optimization service calls `optimize_network` and uses the same simulator for each candidate.

The current antenna pattern analysis (`analyze_ula`) is an additional analysis endpoint. It is not yet coupled to the gain calculation used inside `simulate_network`; the integrated simulator currently uses `ideal_array_gain_dbi`.

A future refactor may move the shared `SimulationMetrics` dataclass to a neutral `core` or `models` module. The current location under `optimization` is retained to avoid breaking existing imports and tests.
