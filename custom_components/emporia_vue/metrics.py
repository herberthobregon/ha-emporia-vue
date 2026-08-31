"""Helpers for derived Emporia Vue metrics."""

from pyemvue.enums import Scale

VOLTAGE_CHANNEL_NUMS = frozenset({"1,2,3", "Mains_A", "Mains_B"})


def amp_hours_to_amps(amp_hours: float, scale: str) -> float:
    """Convert an AmpHours interval reading into an average current in amps."""
    if scale == Scale.MINUTE.value:
        return amp_hours * 60
    if scale == Scale.SECOND.value:
        return amp_hours * 3600
    if scale == Scale.MINUTES_15.value:
        return amp_hours * 4
    return amp_hours


def energy_cost(kilowatt_hours: float, cost_per_kwh: float) -> float:
    """Return the monetary cost for a kWh reading."""
    return kilowatt_hours * cost_per_kwh


def is_line_voltage_channel(channel_num: str) -> bool:
    """Return True if Voltage should be exposed for this channel."""
    return channel_num in VOLTAGE_CHANNEL_NUMS
