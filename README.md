# RF-Exposure-Optimizer

Prototype for simulating RF exposure/network indicators and optimizing transmit power and antenna count using Particle Swarm Optimization (PSO).

> Scientific scope: this is a research prototype. The current SAR output is a 1-D 10 g column proxy, the thermal model is preliminary, and the membrane voltage is an exploratory RC proxy. Results are not regulatory compliance certification or medical conclusions.

## Repository structure

- `backend/app/models/`: physical and integrated simulation models.
- `backend/app/optimization/`: objective, constraints, fitness, PSO, and optimization problem.
- `backend/app/api/`: FastAPI routes and service layer.
- `backend/tests/`: tests for models, optimization, and API.
- `frontend/`: React + Vite application.
- `docs/`: architecture and model documentation.
- `results/`: output folders for exported simulations, optimizations, figures, and reports.

## 1. Start the backend

Open a terminal:

```bash
cd backend
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API documentation: <http://127.0.0.1:8000/docs>

## 2. Start the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>.

If the backend uses another address, create `frontend/.env` from `.env.example` and set `VITE_API_URL`.

## 3. Run tests

From `backend/` with the virtual environment active:

```bash
pytest -q
```

## Main API endpoints

### Health

```http
GET /api/health
```

### Run a simulation

```http
POST /api/simulation/run
Content-Type: application/json
```

```json
{
  "design": {"tx_power_w": 21, "n_antennas": 8},
  "scenario": {
    "frequency_hz": 2500000000,
    "distance_m": 50,
    "bandwidth_hz": 100000000,
    "operation_duration_s": 360
  }
}
```

### Run an optimization

```http
POST /api/optimization/run
Content-Type: application/json
```

An empty JSON object `{}` uses the default scenario, baseline, PSO settings, weights, and constraints. You can override them; see the OpenAPI schema at `/docs`.

## Notes

- The backend allows the default Vite origins on port `5173`; configure `FRONTEND_ORIGINS` in `backend/.env` if needed.
- The separate ULA antenna analysis exists at `/antenna/analyze`. Its detailed pattern is not yet integrated into the gain calculation of the main network simulator.
- The current weighted-sum PSO returns one best solution, not a Pareto front.
