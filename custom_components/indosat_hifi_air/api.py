"""API client for Indosat HiFi Air."""

from __future__ import annotations

import hashlib
import json
import random
from datetime import datetime

import aiohttp

from .const import (
    API_CHANNEL,
    AUTH_KEY,
    AUTH_SECRET,
    BASE_URL_HIFI,
    BASE_URL_SALES,
    CAT_ID,
    DEFAULT_TOKEN,
    DEVICE_ID,
    ENDPOINT_CHECKALTNO,
    ENDPOINT_QUOTA_DETAILS,
    ENDPOINT_TOKEN_GUEST,
    ENDPOINT_VALIDATE_CALLPLAN,
    PROJECT_ID,
    RC4_KEY,
    REFERER_URL,
)


def _rc4_encrypt(plaintext: str, key: str = RC4_KEY) -> str:
    """RC4 encrypt plaintext and return hex string."""
    s = list(range(256))
    k = [ord(key[i % len(key)]) for i in range(256)]
    j = 0
    for i in range(256):
        j = (j + s[i] + k[i]) % 256
        s[i], s[j] = s[j], s[i]

    i = 0
    j = 0
    out = ""
    for ch in plaintext:
        i = (i + 1) % 256
        j = (j + s[i]) % 256
        s[i], s[j] = s[j], s[i]
        out += chr(ord(ch) ^ s[(s[i] + s[j]) % 256])

    hex_out = ""
    for ch in out:
        h = hex(ord(ch))[2:]
        if len(h) == 1:
            h = "0" + h
        hex_out += h
    return hex_out


def _build_salt(token: str) -> str:
    """Derive salt from token by taking every other character."""
    return "".join(token[i] for i in range(0, len(token), 2))


def _sign_body(body: dict, token: str) -> str:
    """Generate x-imi-oauth SHA512 signature."""
    salt = _build_salt(token)
    payload = f"REQBODY={json.dumps(body, separators=(',', ':'))}&SALT={salt}"
    return hashlib.sha512(payload.encode("utf-8")).hexdigest()


def _build_uid() -> str:
    """Build X-IMI-UID: YYYYMMDDHHMMSSmmmRRR."""
    now = datetime.now()
    rand = str(random.randint(0, 999)).zfill(3)
    return (
        f"{now.year}{now.month:02d}{now.day:02d}"
        f"{now.hour:02d}{now.minute:02d}{now.second:02d}"
        f"{now.microsecond // 1000:03d}{rand}"
    )


def _normalize_msisdn(phone: str) -> str:
    """Normalize phone to 62... format. Accepts 0..., 62..., or bare 8..."""
    digits = "".join(c for c in phone if c.isdigit())
    if digits.startswith("0"):
        digits = "62" + digits[1:]
    elif not digits.startswith("62"):
        digits = "62" + digits
    return digits


class IndosatHifiAirAPI:
    """Async API client for Indosat HiFi Air."""

    def __init__(self, session: aiohttp.ClientSession | None = None) -> None:
        self._session = session
        self._token: str = DEFAULT_TOKEN
        self._own_session = session is None

    async def _headers(
        self,
        body: dict,
        token: str | None = None,
        x_app_os: str = "website",
    ) -> dict:
        """Build request headers."""
        t = token if token is not None else self._token
        return {
            "Accept": "*/*",
            "Accept-Language": "en",
            "Authorization": _rc4_encrypt(AUTH_KEY, AUTH_SECRET),
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "Origin": BASE_URL_HIFI,
            "Referer": REFERER_URL,
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
            ),
            "X-APP-OS": x_app_os,
            "X-DEVICEID": DEVICE_ID,
            "X-IMI-APP-CHANNEL": "website",
            "X-IMI-CHANNEL": "website",
            "X-IMI-LANGUAGE": "ID",
            "X-IMI-TOKENID": t,
            "X-IMI-UID": _build_uid(),
            "x-imi-oauth": _sign_body(body, t),
        }

    async def _request(
        self,
        base_url: str,
        endpoint: str,
        body: dict,
        token: str | None = None,
        x_app_os: str = "website",
    ) -> dict:
        """Make an authenticated POST request."""
        if self._session is None:
            self._session = aiohttp.ClientSession()

        headers = await self._headers(body, token, x_app_os)
        url = f"{base_url}{endpoint}"

        body_json = json.dumps(body, separators=(",", ":"))
        async with self._session.post(url, headers=headers, data=body_json) as resp:
            text = await resp.text()
            data = json.loads(text)
            # Update token if returned in header
            new_token = resp.headers.get("X-IMI-TOKENID")
            if new_token:
                self._token = new_token
            return data

    async def get_guest_token(self) -> dict:
        """Fetch a guest token."""
        return await self._request(
            BASE_URL_SALES,
            ENDPOINT_TOKEN_GUEST,
            {},
            token=DEFAULT_TOKEN,
            x_app_os="web",
        )

    async def checkaltno(self, phone: str) -> dict:
        """Check alternate number."""
        enc = _rc4_encrypt(_normalize_msisdn(phone))
        return await self._request(
            BASE_URL_HIFI,
            ENDPOINT_CHECKALTNO,
            {"msisdn": enc},
        )

    async def validate_callplan(self, phone: str) -> dict:
        """Validate call plan and obtain user token."""
        enc = _rc4_encrypt(_normalize_msisdn(phone))
        return await self._request(
            BASE_URL_HIFI,
            ENDPOINT_VALIDATE_CALLPLAN,
            {
                "msisdn": enc,
                "projectid": PROJECT_ID,
                "catid": CAT_ID,
                "pushnotificationid": None,
                "api_channel": API_CHANNEL,
            },
        )

    async def get_quota(self, phone: str) -> dict:
        """Fetch quota details."""
        enc = _rc4_encrypt(_normalize_msisdn(phone))
        return await self._request(
            BASE_URL_HIFI,
            ENDPOINT_QUOTA_DETAILS,
            {
                "msisdn": enc,
                "projectid": PROJECT_ID,
                "catid": CAT_ID,
            },
        )

    async def get_quota_data(self, phone: str) -> dict:
        """Orchestrate the full flow and return quota info."""
        # Step 1: try guest token (optional fallback to DEFAULT_TOKEN)
        guest = await self.get_guest_token()
        if guest.get("status") == "0" and guest.get("data", {}).get("token"):
            self._token = guest["data"]["token"]

        # Step 2: check alternate number
        alt = await self.checkaltno(phone)
        if str(alt.get("status", "1")) != "0":
            raise IndosatAPIError(f"checkaltno failed: {alt.get('message', alt)}")

        # Step 3: validate call plan (this returns the real user token)
        val = await self.validate_callplan(phone)
        if str(val.get("status", "1")) != "0":
            raise IndosatAPIError(f"validatecallplan failed: {val.get('message', val)}")

        # Step 4: get quota
        quota = await self.get_quota(phone)
        if str(quota.get("status", "1")) != "0":
            raise IndosatAPIError(f"quota/details failed: {quota.get('message', quota)}")

        return quota.get("data", {})

    async def close(self) -> None:
        """Close the aiohttp session if we own it."""
        if self._own_session and self._session is not None:
            await self._session.close()
            self._session = None


class IndosatAPIError(Exception):
    """API error."""

