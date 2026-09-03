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


def test_phase_channels_have_no_energy_or_cost_entities() -> None:
    """Mains_A/B only expose current and voltage, not energy or cost."""
    assert not METRICS.has_energy_entities("Mains_A")
    assert not METRICS.has_energy_entities("Mains_B")
    assert METRICS.has_energy_entities("1,2,3")
    assert METRICS.has_energy_entities("Balance")
    assert METRICS.has_energy_entities("9")


def test_phase_channels_are_mains_a_and_b() -> None:
    """Only Mains_A and Mains_B attach to the monitor device."""
    assert METRICS.is_phase_channel("Mains_A")
    assert METRICS.is_phase_channel("Mains_B")
    assert not METRICS.is_phase_channel("1,2,3")
    assert not METRICS.is_phase_channel("Balance")
    assert not METRICS.is_phase_channel("9")


def test_phase_channels_share_main_device_id() -> None:
    """Mains_A/B use the same HA device identifier as Main."""
    assert METRICS.vue_channel_device_id(641199, "Mains_A") == "641199-1,2,3"
    assert METRICS.vue_channel_device_id(641199, "Mains_B") == "641199-1,2,3"
    assert METRICS.vue_channel_device_id(641199, "1,2,3") == "641199-1,2,3"
    assert METRICS.vue_channel_device_id(641199, "Balance") == "641199-Balance"
    assert METRICS.vue_channel_device_id(641199, "9") == "641199-9"


def test_device_name_for_balance_prefixes_monitor() -> None:
    """Balance is a named aggregate under the monitor, not a generic device."""
    assert (
        METRICS.vue_channel_device_name("Tablero 1", "Balance", "Balance")
        == "Tablero 1 Balance"
    )


def test_device_name_for_phases_is_the_monitor() -> None:
    """Phase channels live on the monitor device, not Mains_A/B devices."""
    assert (
        METRICS.vue_channel_device_name("Tablero 1", "Mains_A", "Mains_A")
        == "Tablero 1"
    )
    assert (
        METRICS.vue_channel_device_name("Tablero 1", "Mains_B", "Mains_B")
        == "Tablero 1"
    )
    assert METRICS.vue_channel_device_name("Tablero 1", "1,2,3", "Main") == "Tablero 1"


def test_device_name_for_unnamed_numbered_ct() -> None:
    """Spare numbered CTs stay distinct instead of collapsing onto the monitor."""
    assert METRICS.vue_channel_device_name("Tablero 1", "9", None) == "Tablero 1 Circuit 9"
    assert METRICS.vue_channel_device_name("Tablero 1", "9", "") == "Tablero 1 Circuit 9"


def test_device_name_for_named_ct_keeps_channel_name() -> None:
    """A CT named in the Emporia app keeps that circuit name."""
    assert METRICS.vue_channel_device_name("Tablero 1", "9", "Kitchen") == "Kitchen"
