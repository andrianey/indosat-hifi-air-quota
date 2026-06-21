"""Constants for the Indosat HiFi Air integration."""

DOMAIN = "indosat_hifi_air"
DEFAULT_NAME = "Indosat HiFi Air"

BASE_URL_SALES = "https://isaleshifiapi.ioh.co.id"
BASE_URL_HIFI = "https://hifi.ioh.co.id"
REFERER_URL = "https://hifi.ioh.co.id/topup-hifiair"

DEFAULT_TOKEN = "012345678909876543210"
RC4_KEY = "ftth"
AUTH_KEY = "website|ftth"
AUTH_SECRET = "1234"

DEVICE_ID = "werwerpoopip34i5pip353323"
PROJECT_ID = "101"
CAT_ID = "1"
API_CHANNEL = "HIFI_AIR_PWA"

ENDPOINT_TOKEN_GUEST = "/api/v4/token/guest"
ENDPOINT_CHECKALTNO = "/api/v4/onboarding/checkaltno"
ENDPOINT_VALIDATE_CALLPLAN = "/api/hifiair/payment/validatecallplan"
ENDPOINT_QUOTA_DETAILS = "/api/hifiair/payment/quota/details/v2"

UPDATE_INTERVAL_MINUTES = 60

SCAN_INTERVAL_OPTIONS = {
    "30": 30,
    "60": 60,
    "180": 180,
    "360": 360,
}
DEFAULT_SCAN_INTERVAL = "60"

