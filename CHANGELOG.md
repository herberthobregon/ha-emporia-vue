# Changelog

## 1.0.0 - 2026-09-02

### Fixed

- Monthly and daily totals no longer crash with
  `TypeError: unsupported operand type(s) for +=: 'float' and 'NoneType'`
  when integrating a minute sample that has no kWh (for example `Mains_A` /
  `Mains_B`, which only report amps and volts). Those samples are skipped.
- Google / Apple (Hosted UI) token login no longer crashes with
  `TypeError: argument 'data': Cannot convert "<class 'str'>" instance to a buffer`.
  Hosted UI ID tokens include an OIDC `at_hash` claim. `pycognito` hashed the
  access token as a `str` and then compared `bytes` to that claim, which fails
  on Python 3.14. A runtime shim wraps `Cognito.verify_token` so SSO accounts
  can finish setup and refresh tokens.

### Added

- Optional **Current Minute Average** sensors (amps) for every channel that
  reports AmpHours. Conversion is `A = Ah × 60` for 1-minute readings.
- Optional **Voltage** sensors on Main (`1,2,3`) and the split-phase channels
  `Mains_A` / `Mains_B` only. Circuit CTs do not get a voltage entity.
- **Cost Today** and **Cost Billing Cycle** sensors: `kWh × cost_per_kwh`,
  calculated locally (not from the Emporia dollars API).
- Setup and reconfigure options:
  - Current Minute Average Sensor (`enable_amps`)
  - Line Voltage Sensor (`enable_volts`)
  - Cost per kWh (default `1.0`)
  - Cost Currency (default `USD`)
- Existing config entries keep amps and volts **off** until you enable them,
  so a reload does not create unexpected entities. New setups default those
  options to on.

### Changed

- **Balance** is no longer a generic device named `Balance`. The Home Assistant
  device is `{monitor name} Balance` (for example `Tablero 1 Balance`). Entity
  unique IDs are unchanged.
- **Mains_A** and **Mains_B** are no longer separate devices. They attach to
  the same device as Main (`{gid}-1,2,3`). Entity names are `Mains_A Current`,
  `Mains_B Current`, `Mains_A Voltage`, and `Mains_B Voltage`. Main itself
  still uses `Current Minute Average` and `Voltage`. Phase channels do not
  get Energy Today / Energy Billing Cycle or Cost Today / Cost Billing Cycle.
- Monthly energy and cost entities are named **Billing Cycle** (not This Month),
  matching the Emporia billing-cycle reset. Unique IDs are unchanged.
- After a reload, leftover devices named `Mains_A`, `Mains_B`, or `Balance`
  may remain in the device registry. They can be deleted manually.
