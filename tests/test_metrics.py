"""Tests for derived Emporia Vue metrics."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

MODULE_PATH = (
    Path(__file__).parents[1] / "custom_components" / "emporia_vue" / "metrics.py"
)
SPEC = spec_from_file_location("emporia_vue_metrics", MODULE_PATH)
assert SPEC and SPEC.loader
METRICS = module_from_spec(SPEC)
SPEC.loader.exec_module(METRICS)


def test_amp_hours_to_amps_for_minute_scale() -> None:
    """A 1-minute AmpHours reading scales to average amps like kWh to W."""
    assert METRICS.amp_hours_to_amps(0.093688, "1MIN") == 0.093688 * 60


def test_energy_cost_multiplies_kwh_by_rate() -> None:
    """Cost is local kWh times the configured rate."""
    assert METRICS.energy_cost(2.5, 1.0) == 2.5
    assert METRICS.energy_cost(10.0, 0.15) == 1.5


def test_line_voltage_channels_are_mains_only() -> None:
    """Voltage entities belong on Main and phase channels, not CTs."""
    assert METRICS.is_line_voltage_channel("1,2,3")
    assert METRICS.is_line_voltage_channel("Mains_A")
    assert METRICS.is_line_voltage_channel("Mains_B")
    assert not METRICS.is_line_voltage_channel("9")
    assert not METRICS.is_line_voltage_channel("Balance")
