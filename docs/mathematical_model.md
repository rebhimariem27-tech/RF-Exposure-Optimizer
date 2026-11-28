# Mathematical model — current prototype

## Design variables

The initial optimization problem has two decision variables:

- Transmit power `P_tx` in watts, continuous inside configured bounds.
- Number of antennas `N`, discrete in `{2, 4, 8, 16}` by default.

## Scenario variables

Frequency, distance, bandwidth, and operation duration are fixed for a given optimization run.

## Radio and exposure chain

The integrated simulator estimates array gain, far-field RMS electric field, layered-tissue transmission/attenuation, a 1-D SAR profile, and a 10 g column proxy. It also estimates received power, thermal noise, SINR, and bitrate.

The integrated gain model is a simplified ideal-array gain. The separate ULA endpoint calculates a more detailed array factor and steering pattern, but those results are not yet passed into the integrated propagation/exposure simulator.

## Thermal and membrane indicators

The temperature model is a preliminary 1-D numerical bioheat model. Default tissue perfusion is zero. The membrane voltage is an exploratory RC proxy, not a validated GHz biological response model.

## Objective

Six normalized components are combined with weights that sum to one:

`SAR + temperature + membrane proxy + energy + QoS deficit + cost`.

The QoS component is zero once the target bitrate is reached; it does not reward bitrate beyond the target.

## Constraints and fitness

The current default constraints are SAR proxy <= 2 W/kg, temperature rise <= 2 K, bitrate >= 100 Mbps, and SINR >= 5 dB. A quadratic penalty for violations is added to the weighted objective. Feasibility is checked separately in the returned result.

These are prototype configuration values. The 1-D SAR proxy is not a regulatory 3-D SAR 10 g compliance result.
