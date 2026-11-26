import numpy as np


# Speed of light in vacuum (m/s)
C0 = 299_792_458.0


def calculate_wavelength(frequency_ghz: float) -> float:
    """
    Calculate the wavelength from the operating frequency.

    lambda = c / f
    """

    if frequency_ghz <= 0:
        raise ValueError("Frequency must be positive.")

    frequency_hz = frequency_ghz * 1e9

    return C0 / frequency_hz


def calculate_element_positions(
    antenna_count: int,
    spacing_m: float
) -> np.ndarray:
    """
    Calculate the positions of ULA elements.

    The array is centered around x = 0.
    """

    if antenna_count < 1:
        raise ValueError("Antenna count must be positive.")

    if spacing_m <= 0:
        raise ValueError("Element spacing must be positive.")

    indices = np.arange(antenna_count)

    positions = (
        indices - (antenna_count - 1) / 2
    ) * spacing_m

    return positions


def calculate_steering_phases(
    positions_m: np.ndarray,
    wavelength_m: float,
    steering_angle_deg: float
) -> np.ndarray:
    """
    Calculate the phase shifts required to steer the beam.

    Angle convention:
    0 degree = broadside direction.

    Formula:
    phase_n = -k * x_n * sin(theta_0)
    """

    k = 2 * np.pi / wavelength_m

    theta_0 = np.deg2rad(steering_angle_deg)

    phases_rad = (
        -k * positions_m * np.sin(theta_0)
    )

    return phases_rad


def calculate_array_factor(
    positions_m: np.ndarray,
    wavelength_m: float,
    amplitudes: np.ndarray,
    phases_rad: np.ndarray,
    theta_deg: np.ndarray
) -> np.ndarray:
    """
    Calculate the complex array factor in the x-z plane.

    theta = 0 degree corresponds to broadside.

    AF(theta) = sum(
        w_n * exp(j * k * x_n * sin(theta))
    )
    """

    k = 2 * np.pi / wavelength_m

    theta_rad = np.deg2rad(theta_deg)

    phase_matrix = (
        k * positions_m[:, None]
        * np.sin(theta_rad)[None, :]
        + phases_rad[:, None]
    )

    field = np.sum(
        amplitudes[:, None] * np.exp(1j * phase_matrix),
        axis=0
    )

    return field


def calculate_array_directivity(
    positions_m: np.ndarray,
    wavelength_m: float,
    amplitudes: np.ndarray,
    phases_rad: np.ndarray
) -> float:
    """
    Estimate array-factor directivity for isotropic elements.

    The radiated intensity is integrated over the full sphere.
    This model does not include mutual coupling or real element patterns.
    """

    k = 2 * np.pi / wavelength_m

    # Spherical integration grid
    theta = np.linspace(0, np.pi, 181)

    phi = np.linspace(
        0,
        2 * np.pi,
        360,
        endpoint=False
    )

    # x-component of the observation direction
    ux = (
        np.sin(theta)[:, None]
        * np.cos(phi)[None, :]
    )

    # Phase contribution of each antenna
    phase_matrix = (
        k * positions_m[:, None, None]
        * ux[None, :, :]
        + phases_rad[:, None, None]
    )

    field = np.sum(
        amplitudes[:, None, None]
        * np.exp(1j * phase_matrix),
        axis=0
    )

    radiation_intensity = np.abs(field) ** 2

    # Integration over phi
    dphi = 2 * np.pi / len(phi)

    integral_phi = np.sum(
        radiation_intensity * np.sin(theta)[:, None],
        axis=1
    ) * dphi

    # Integration over theta
    total_radiated_power = np.trapz(
        integral_phi,
        theta
    )

    if total_radiated_power <= 0:
        raise ValueError("Invalid radiated power.")

    # Directivity = 4*pi*maximum intensity / total radiated power
    directivity = (
        4 * np.pi
        * np.max(radiation_intensity)
        / total_radiated_power
    )

    return float(directivity)


def analyze_ula(
    frequency_ghz: float,
    antenna_count: int,
    element_gain_dbi: float = 8.0,
    element_spacing_m: float | None = None,
    steering_angle_deg: float = 0.0,
    amplitudes: list[float] | None = None,
    phase_offsets_deg: list[float] | None = None
) -> dict:
    """
    Main function: analyze a Uniform Linear Array (ULA).
    """

    # 1. Calculate wavelength
    wavelength_m = calculate_wavelength(frequency_ghz)

    # 2. Default spacing = lambda / 2
    if element_spacing_m is None:
        element_spacing_m = wavelength_m / 2

    # 3. Calculate element positions
    positions_m = calculate_element_positions(
        antenna_count,
        element_spacing_m
    )

    # 4. Relative excitation amplitudes
    if amplitudes is None:
        amplitudes_array = np.ones(antenna_count)
    else:
        amplitudes_array = np.asarray(
            amplitudes,
            dtype=float
        )

    # Normalize amplitudes:
    # sum(|w_n|^2) = 1
    # This keeps the total excitation power constant.
    amplitudes_array = (
        amplitudes_array
        / np.linalg.norm(amplitudes_array)
    )

    # 5. Calculate automatic steering phases
    steering_phases_rad = calculate_steering_phases(
        positions_m,
        wavelength_m,
        steering_angle_deg
    )

    # 6. Additional phase corrections
    if phase_offsets_deg is None:
        phase_offsets_rad = np.zeros(antenna_count)
    else:
        phase_offsets_rad = np.deg2rad(
            np.asarray(phase_offsets_deg, dtype=float)
        )

    # Total phase = steering phase + correction
    total_phases_rad = (
        steering_phases_rad + phase_offsets_rad
    )

    # 7. Calculate radiation pattern in the x-z plane
    theta_deg = np.linspace(-90, 90, 721)

    field = calculate_array_factor(
        positions_m,
        wavelength_m,
        amplitudes_array,
        total_phases_rad,
        theta_deg
    )

    field_magnitude = np.abs(field)

    maximum_field = np.max(field_magnitude)

    normalized_field = field_magnitude / maximum_field

    # Convert normalized field to dB
    array_factor_db = 20 * np.log10(
        np.maximum(normalized_field, 1e-6)
    )

    # 8. Calculate ideal array-factor directivity
    directivity_linear = calculate_array_directivity(
        positions_m,
        wavelength_m,
        amplitudes_array,
        total_phases_rad
    )

    directivity_dbi = 10 * np.log10(directivity_linear)

    # Approximate gain using the element gain
    ideal_gain_estimate_dbi = (
        element_gain_dbi + directivity_dbi
    )

    # 9. Format phases between -180 and +180 degrees
    total_phases_deg = (
        np.rad2deg(total_phases_rad) + 180
    ) % 360 - 180

    return {
        "wavelength_m": float(wavelength_m),

        "element_spacing_m": float(element_spacing_m),

        "aperture_m": float(
            (antenna_count - 1) * element_spacing_m
        ),

        "normalized_amplitudes": amplitudes_array.tolist(),

        "element_phases_deg": total_phases_deg.tolist(),

        "steering_angle_deg": float(steering_angle_deg),

        "array_factor_directivity_linear": directivity_linear,

        "array_factor_directivity_dbi": float(directivity_dbi),

        "ideal_gain_estimate_dbi": float(ideal_gain_estimate_dbi),

        "theta_deg": theta_deg.tolist(),

        "array_factor_db": array_factor_db.tolist()
    }