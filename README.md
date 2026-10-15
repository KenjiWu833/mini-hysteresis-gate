# mini-hysteresis-gate

A tiny, dependency-free hysteresis gate for change detection with separate rise and fall thresholds.

## Usage

```python
from mini_hysteresis_gate import HysteresisGate

gate = HysteresisGate(rise=10, fall=5)
print(gate.update(12))   # True  (rises above 10)
print(gate.update(6))    # True  (between 5 and 10, state holds)
print(gate.update(4))    # False (falls below 5)
```

## Why this exists

When a noisy signal crosses a single threshold repeatedly, a naive on/off
checker chatters between states. A hysteresis gate uses two thresholds — one
to rise, a lower one to fall — creating a deadband where small fluctuations
are ignored.

The trade-off here is simplicity over smoothing. This gate makes no attempt
to debounce over time; it reacts on every sample. If your signal needs both
deadband *and* time-based smoothing, compose this with a separate debounce.

## Edge cases

Thresholds are normalized: the larger of the two becomes the rise threshold,
the smaller the fall threshold, so you may pass them in either order.

Comparisons are strict (`>` and `<`). A value exactly equal to a threshold
does **not** trigger a transition; this is what stops a signal pinned to a
threshold from chattering. If you need `>=` / `<=` behaviour, shift your
thresholds by a small epsilon.

`NaN` inputs leave the state unchanged because every IEEE 754 comparison
against `NaN` is `False`. If your data stream may contain `NaN`, filter it
before the gate or accept that those samples are no-ops.

The initial state may be passed as `None`, which is treated as `False`. This
lets callers forward an uninitialised sensor reading without an extra guard.

## Exports

- `HysteresisGate(rise, fall, initial=None)` — the gate class.
  - `.rise` — property, the normalized rise threshold.
  - `.fall` — property, the normalized fall threshold.
  - `.state` — current boolean state, readable and writable.
  - `.update(value)` — feed a sample, returns the new boolean state.
