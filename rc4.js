function rc4Hex(str, key = "ftth") {
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
  for (const ch of str) {
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

const [input, key] = process.argv.slice(2);
console.log(rc4Hex(input || "", key || "ftth"));
