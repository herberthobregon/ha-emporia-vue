"""Helpers for derived Emporia Vue metrics."""

from pyemvue.enums import Scale

MAIN_CHANNEL_NUM = "1,2,3"
PHASE_CHANNEL_NUMS = frozenset({"Mains_A", "Mains_B"})
VOLTAGE_CHANNEL_NUMS = frozenset({MAIN_CHANNEL_NUM, *PHASE_CHANNEL_NUMS})


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


def is_phase_channel(channel_num: str) -> bool:
    """Return True if this is a split-phase mains channel."""
    return channel_num in PHASE_CHANNEL_NUMS


def vue_channel_device_id(device_gid: int | str, channel_num: str) -> str:
    """Return the Home Assistant device identifier suffix for a channel."""
    if is_phase_channel(channel_num):
        return f"{device_gid}-{MAIN_CHANNEL_NUM}"
    return f"{device_gid}-{channel_num}"


def vue_channel_device_name(
    device_name: str,
    channel_num: str,
    channel_name: str | None,
) -> str:
    """Return the Home Assistant device name for a Vue channel."""
    if is_phase_channel(channel_num) or channel_num == MAIN_CHANNEL_NUM:
        return device_name
    if channel_num.isdigit():
        if channel_name:
            return channel_name
        return f"{device_name} Circuit {channel_num}"
    if channel_name:
        return f"{device_name} {channel_name}"
    return device_name
