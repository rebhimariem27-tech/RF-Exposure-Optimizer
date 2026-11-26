def estimate_dc_power(
    tx_power_w: float,
    pa_efficiency: float,
    circuit_power_w: float
) -> float:

    if tx_power_w <= 0:
        raise ValueError("Transmit power must be positive.")

    if not 0 < pa_efficiency <= 1:
        raise ValueError("PA efficiency must be between 0 and 1.")

    if circuit_power_w < 0:
        raise ValueError("Circuit power cannot be negative.")

    return tx_power_w / pa_efficiency + circuit_power_w


def estimate_energy(
    dc_power_w: float,
    operation_duration_s: float
) -> float:

    if dc_power_w < 0 or operation_duration_s <= 0:
        raise ValueError("Invalid power or operation duration.")

    return dc_power_w * operation_duration_s