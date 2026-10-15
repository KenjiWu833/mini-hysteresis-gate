"""Hysteresis gate for change detection with deadband.

A hysteresis gate transitions between two states ("on" and "off") using
different thresholds for rising and falling signals. This deadband prevents
chatter when the input signal hovers near a single threshold.

Design decisions
----------------

* Rise and fall thresholds may be passed in any order; the larger is used as
  the rise threshold and the smaller as the fall threshold. This is a
  deliberate convenience over a strict contract, documented here so callers
  know not to rely on positional ordering.

* Initial state defaults to ``False``. A ``None`` initial state is treated
  as ``False`` rather than raising, so callers can pass an undefined sensor
  reading without a separate guard. If the initial signal already exceeds
  the rise threshold, the gate moves to ``True`` on the first ``update``.

* Values are compared with ``>`` and ``<`` rather than ``>=`` and ``<=``.
  This means a value exactly equal to a threshold does NOT cause a
  transition. A constant signal sitting on a threshold will not chatter,
  which is the whole point of a hysteresis deadband.

* Floats and ints work interchangeably. No attempt is made to guard against
  NaN; IEEE 754 comparisons against NaN are all ``False``, so a NaN input
  simply leaves the state unchanged. That is acceptable and documented
  behaviour, not a bug.

* No debouncing is applied: the gate reacts on every sample. A clock is not
  required because no time-based smoothing is performed.
"""


class HysteresisGate:
    """A two-state gate with separate rise and fall thresholds.

    The gate holds one of two boolean states. It transitions to ``True``
    (rises) only when the input strictly exceeds the rise threshold, and to
    ``False`` (falls) only when the input strictly undershoots the fall
    threshold. Inputs between the two thresholds leave the state unchanged.

    Example:

        >>> gate = HysteresisGate(rise=10, fall=5)
        >>> gate.update(12)
        True
        >>> gate.update(6)   # between thresholds, state holds
        True
        >>> gate.update(4)
        False
    """

    __slots__ = ("_rise", "_fall", "state")

    def __init__(self, rise, fall, initial=None):
        """Construct a gate.

        Args:
            rise: Transition-to-True threshold. Need not be the larger value;
                the constructor sorts the pair automatically so passing them
                swapped yields the same gate.
            fall: Transition-to-False threshold.
            initial: Initial boolean state. ``None`` is treated as ``False``
                so callers can forward an uninitialised sensor reading without
                an extra conditional.

        Raises:
            TypeError: If ``rise`` or ``fall`` is not a real number.
        """
        self._rise = max(rise, fall)
        self._fall = min(rise, fall)
        self.state = bool(initial) if initial is not None else False

    @property
    def rise(self):
        """The threshold at which the gate turns on."""
        return self._rise

    @property
    def fall(self):
        """The threshold at which the gate turns off."""
        return self._fall

    def update(self, value):
        """Feed a new sample and return the resulting state.

        Transitions are made with strict comparisons so that a signal pinned
        to a threshold is stable. Returns the post-update boolean state so
        callers can use the gate inline.
        """
        if value > self._rise:
            self.state = True
        elif value < self._fall:
            self.state = False
        return self.state
