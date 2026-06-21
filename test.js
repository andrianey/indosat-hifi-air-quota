const fetch = global.fetch;

const ORIGIN_URL = "https://hifi.ioh.co.id";
const BASE_URL = "https://isaleshifiapi.ioh.co.id";
const DEFAULT_TOKEN = "012345678909876543210";
const AUTH_KEY = "website|ftth";
const AUTH_SECRET = "1234";
const DEVICE_ID = "werwerpoopip34i5pip353323";

function rc4Hex(input, key = "ftth") {
  const s = new Array(256);
  const k = new Array(256);
  for (let i = 0; i < 256; i += 1) {
    s[i] = i;
    k[i] = key.charCodeAt(i % key.length);
  }
  let j = 0;
  for (let i = 0; i < 256; i += 1) {
    j = (j + s[i] + k[i]) % 256;
    [s[i], s[j]] = [s[j], s[i]];
  }
  let i = 0;
  j = 0;
  let out = "";
  for (const ch of input) {
    i = (i + 1) % 256;
    j = (j + s[i]) % 256;
    [s[i], s[j]] = [s[j], s[i]];
    const t = (s[i] + s[j]) % 256;
    const keystream = s[t];
    out += String.fromCharCode(ch.charCodeAt(0) ^ keystream);
  }
  let hex = "";
  for (const ch of out) {
    hex += ch.charCodeAt(0).toString(16).padStart(2, "0");
  }
  return hex;
}

function signBody(body, token = DEFAULT_TOKEN) {
  const saltSource = token || DEFAULT_TOKEN;
  let salt = "";
  for (let i = 0; i < saltSource.length; i += 2) {
    salt += saltSource[i];
  }
  const payload = `REQBODY=${JSON.stringify(body)}&SALT=${salt}`;
  const crypto = require("crypto");
  return crypto.createHash("sha512").update(payload).digest("hex").toUpperCase();
}

function buildUid() {
  const now = new Date();
  const pad = (value, size) => value.toString().padStart(size, "0");
  const formatted = `${now.getFullYear()}${pad(now.getMonth() + 1, 2)}${pad(
    now.getDate(),
    2
  )}${pad(now.getHours(), 2)}${pad(now.getMinutes(), 2)}${pad(
    now.getSeconds(),
    2
  )}${pad(now.getMilliseconds(), 3)}`;
  const random = Math.floor(Math.random() * 1000)
    .toString()
    .padStart(3, "0");
  return `${formatted}${random}`;
}

function buildHeaders(token, body, cookieHeader) {
  return {
    Accept: "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en",
    Authorization: rc4Hex(AUTH_KEY, AUTH_SECRET),
    "Cache-Control": "no-cache",
    Connection: "keep-alive",
    "Content-Type": "application/json",
    Pragma: "no-cache",
    "X-IMI-APP-CHANNEL": "website",
    "X-IMI-CHANNEL": "website",
    "X-APP-OS": "web",
    "X-IMI-LANGUAGE": "ID",
    "X-IMI-TOKENID": token || DEFAULT_TOKEN,
    "X-IMI-UID": buildUid(),
    "X-DEVICEID": DEVICE_ID,
    "x-imi-oauth": signBody(body, token || DEFAULT_TOKEN),
    Origin: ORIGIN_URL,
    Referer: `${ORIGIN_URL}/topup-hifiair`,
    "User-Agent":
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    ...(cookieHeader ? { Cookie: cookieHeader } : {}),
  };
}

async function getCookies() {
  const response = await fetch(`${ORIGIN_URL}/topup-hifiair`, {
    headers: {
      Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
      "Accept-Language": "en",
      "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
      Connection: "keep-alive",
      "Cache-Control": "no-cache",
      Pragma: "no-cache",
    },
  });
  const setCookies = response.headers.getSetCookie ? response.headers.getSetCookie() : response.headers.raw()["set-cookie"];
  if (!setCookies || !setCookies.length) {
    return undefined;
  }
  const pairs = setCookies.map((c) => c.split(";")[0]).filter(Boolean);
  return pairs.join("; ");
}

async function fetchGuestToken() {
  const cookieHeader = await getCookies();
  const body = {
    channel: "website",
    language: "ID",
    appos: "web",
  };
  const headers = buildHeaders(undefined, body, cookieHeader);
  const response = await fetch(`${BASE_URL}/api/v4/token/guest`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  const text = await response.text();
  console.log("status", response.status);
  console.log("raw", text);
}

fetchGuestToken().catch((err) => {
  console.error(err);
  process.exit(1);
});
