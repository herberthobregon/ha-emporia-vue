"""Constants for the Emporia Vue integration."""

import voluptuous as vol

from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
import homeassistant.helpers.config_validation as cv

DOMAIN = "emporia_vue"
VUE_DATA = "vue_data"
AUTH_METHOD = "auth_method"
AUTH_METHOD_EMAIL_PASSWORD = "email_password"
AUTH_METHOD_TOKENS = "tokens"
CONF_ACCESS_TOKEN = "access_token"
CONF_ID_TOKEN = "id_token"
CONF_REFRESH_TOKEN = "refresh_token"
ENABLE_1S = "enable_1s"
ENABLE_1M = "enable_1m"
ENABLE_1D = "enable_1d"
ENABLE_1MON = "enable_1mon"
ENABLE_AMPS = "enable_amps"
ENABLE_VOLTS = "enable_volts"
SOLAR_INVERT = "solar_invert"
CONF_COST_PER_KWH = "cost_per_kwh"
CONF_COST_CURRENCY = "cost_currency"
DEFAULT_COST_PER_KWH = 1.0
DEFAULT_COST_CURRENCY = "USD"
CUSTOMER_GID = "customer_gid"
CONFIG_TITLE = "title"

AUTH_METHOD_SCHEMA = vol.Schema(
    {
        vol.Required(AUTH_METHOD, default=AUTH_METHOD_EMAIL_PASSWORD): vol.In(
            {
                AUTH_METHOD_EMAIL_PASSWORD: "Emporia email and password",
                AUTH_METHOD_TOKENS: "Emporia tokens (Google/SSO accounts)",
            }
        ),
    }
)

CONFIG_OPTIONS_SCHEMA = {
    vol.Optional(ENABLE_1M, default=True): cv.boolean,
    vol.Optional(ENABLE_1D, default=True): cv.boolean,
    vol.Optional(ENABLE_1MON, default=True): cv.boolean,
    vol.Optional(ENABLE_AMPS, default=True): cv.boolean,
    vol.Optional(ENABLE_VOLTS, default=True): cv.boolean,
    vol.Optional(SOLAR_INVERT, default=True): cv.boolean,
    vol.Optional(CONF_COST_PER_KWH, default=DEFAULT_COST_PER_KWH): vol.All(
        vol.Coerce(float), vol.Range(min=0)
    ),
    vol.Optional(CONF_COST_CURRENCY, default=DEFAULT_COST_CURRENCY): cv.string,
}

CONFIG_FLOW_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        **CONFIG_OPTIONS_SCHEMA,
    }
)

TOKEN_CONFIG_FLOW_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ID_TOKEN): cv.string,
        vol.Required(CONF_ACCESS_TOKEN): cv.string,
        vol.Required(CONF_REFRESH_TOKEN): cv.string,
        **CONFIG_OPTIONS_SCHEMA,
    }
)
