from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationMetrics:

    # 1. Electromagnetic exposure
    sar10g_w_kg: float

    # 2. Thermal response
    delta_t_max_k: float

    # 3. Membrane potential variation
    delta_vm_abs_v: float

    # 4. Energy consumption
    energy_consumption_j: float

    # 5. Communication performance
    bitrate_mbps: float

    # 6. Infrastructure cost
    infrastructure_cost: float

    # Additional QoS indicator for constraint checking
    sinr_db: float