import math
import unittest

from mini_hysteresis_gate import HysteresisGate


class TestHysteresisGate(unittest.TestCase):

    def test_rises_above_rise_threshold(self):
        gate = HysteresisGate(rise=10, fall=5)
        self.assertTrue(gate.update(12))

    def test_falls_below_fall_threshold(self):
        gate = HysteresisGate(rise=10, fall=5, initial=True)
        self.assertFalse(gate.update(3))

    def test_holds_between_thresholds_when_on(self):
        gate = HysteresisGate(rise=10, fall=5, initial=True)
        self.assertTrue(gate.update(7))

    def test_holds_between_thresholds_when_off(self):
        gate = HysteresisGate(rise=10, fall=5)
        self.assertFalse(gate.update(7))

    def test_value_at_rise_threshold_does_not_rise(self):
        gate = HysteresisGate(rise=10, fall=5)
        self.assertFalse(gate.update(10))

    def test_value_at_fall_threshold_does_not_fall(self):
        gate = HysteresisGate(rise=10, fall=5, initial=True)
        self.assertTrue(gate.update(5))

    def test_thresholds_normalized_when_passed_swapped(self):
        gate = HysteresisGate(rise=5, fall=10)
        self.assertEqual(gate.rise, 10)
        self.assertEqual(gate.fall, 5)

    def test_initial_none_treated_as_false(self):
        gate = HysteresisGate(rise=10, fall=5, initial=None)
        self.assertFalse(gate.state)

    def test_initial_true_persisted(self):
        gate = HysteresisGate(rise=10, fall=5, initial=True)
        self.assertTrue(gate.state)

    def test_initial_truthy_value_coerced(self):
        # A non-bool truthy value is coerced to True via bool().
        gate = HysteresisGate(rise=10, fall=5, initial=1)
        self.assertIs(gate.state, True)

    def test_chatter_resistance_at_threshold(self):
        # Signal oscillating exactly on the rise threshold must not chatter.
        gate = HysteresisGate(rise=10, fall=5)
        for _ in range(100):
            self.assertFalse(gate.update(10))
        self.assertTrue(gate.update(10.0001))

    def test_full_rise_and_fall_cycle(self):
        gate = HysteresisGate(rise=10, fall=5)
        self.assertFalse(gate.update(0))
        self.assertFalse(gate.update(8))
        self.assertTrue(gate.update(11))
        self.assertTrue(gate.update(8))
        self.assertFalse(gate.update(4))

    def test_equal_thresholds_act_as_strict_trigger(self):
        # With a zero deadband the gate becomes a strict-comparator.
        gate = HysteresisGate(rise=7, fall=7)
        self.assertFalse(gate.update(7))
        self.assertTrue(gate.update(8))
        self.assertTrue(gate.update(7))
        self.assertFalse(gate.update(6))

    def test_nan_input_leaves_state_unchanged(self):
        # IEEE 754: every comparison with NaN is False, so NaN cannot trigger.
        gate = HysteresisGate(rise=10, fall=5, initial=True)
        self.assertTrue(gate.update(float("nan")))
        gate2 = HysteresisGate(rise=10, fall=5)
        self.assertFalse(gate2.update(float("nan")))

    def test_negative_thresholds(self):
        gate = HysteresisGate(rise=-10, fall=-20)
        self.assertFalse(gate.update(-15))
        self.assertTrue(gate.update(-5))
        self.assertTrue(gate.update(-15))
        self.assertFalse(gate.update(-25))

    def test_float_thresholds_and_values(self):
        gate = HysteresisGate(rise=1.0, fall=0.5)
        self.assertFalse(gate.update(0.9))
        self.assertTrue(gate.update(1.1))
        self.assertTrue(gate.update(0.7))
        self.assertFalse(gate.update(0.4))


if __name__ == "__main__":
    unittest.main()
