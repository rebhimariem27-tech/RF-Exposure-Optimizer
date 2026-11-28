# Optimization method

The optimizer uses Particle Swarm Optimization (PSO). Each particle represents `[transmit_power_w, antenna_count]`.

At each objective evaluation:

1. Convert the particle to a `NetworkDesign`.
2. Run `simulate_network(design, scenario)`.
3. Compute the six normalized objective components.
4. Evaluate the four constraints.
5. Add the weighted quadratic penalty to the objective.
6. Return the scalar fitness to PSO.

PSO updates each particle using inertia, its personal best (Pbest), and the swarm global best (Gbest). The antenna count is projected to one of the allowed discrete values after movement.

The present implementation is a weighted-sum single-objective optimizer. Although `pareto.py` contains analysis helpers, the current optimization endpoint does not produce a true Pareto front. A Pareto UI should be added only after a multi-objective search and result contract are implemented.
