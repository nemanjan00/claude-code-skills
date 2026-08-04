---
name: smartcards
description: Communicate with ISO-7816 contact smart cards — via a PC/SC reader (e.g. ACS ACR38/ACR39, OMNIKEY) or line-level via a Bus Pirate. Use to read a card's ATR, send/parse APDUs (SELECT, READ BINARY, GET RESPONSE, VERIFY, GET DATA), handle T=0 vs T=1, drive PC/SC tooling (pcscd, pcsc_scan, pyscard, opensc, GlobalPlatformPro), decode status words, or drop below a reader's ATR gate with a Bus Pirate when a card is rejected.
---

# Talking to ISO-7816 smart cards

Two ways in, depending on what you have and what you need:
- **A) PC/SC contact reader** (ACS ACR38/39, OMNIKEY, …) — the normal path. Reliable, handles T=0/T=1 for you.
- **B) Bus Pirate, line-level** — when you need to go *below* a reader's ATR/TCK validation (e.g. a card a normal reader calls “unresponsive”, or to read a raw/malformed ATR). See the **buspirate** skill.

## Fundamentals

**ATR (Answer To Reset)** — the bytes a card emits on reset:
`TS · T0 · [TA1 TB1 TC1 TD1 …] interface bytes · [historical bytes] · [TCK]`
- `TS` = `3B` (direct convention) or `3F` (inverse).
- `T0` high nibble Y = which interface bytes follow; low nibble K = number of historical bytes.
- `TDi` low nibble selects the protocol (**T=0** or **T=1**); `TDi` high nibble Y = which further interface bytes follow.
- `TCK` (checksum, XOR of everything after TS) is present when any protocol other than pure T=0 is offered.
- Parse online with `https://smartcard-atr.apdu.fr/` or `ATR_analysis` from pcsc-tools.

**APDU (command)**: `CLA INS P1 P2 [Lc <data>] [Le]` → response `[<data>] SW1 SW2`.
- Cases: 1 = header only; 2 = expect data (`Le`); 3 = send data (`Lc`+data); 4 = send+expect.
- Common status words: `90 00` ok · `61 XX` XX bytes available, do GET RESPONSE · `6C XX` wrong Le, retry with Le=XX · `6A 82` file/app not found · `6A 88` ref data not found · `69 82` security status not satisfied · `63 CX` verify failed, X tries left · `6D 00` INS unsupported · `6E 00` CLA unsupported.

**Common commands**: `00 A4` SELECT (P1=04 by AID/DF-name, 00 by FID, 00+`3F00` = MF) · `00 B0` READ BINARY · `00 B2` READ RECORD · `00 C0` GET RESPONSE · `00/80 CA` GET DATA · `00 20` VERIFY (PIN).

**T=0 vs T=1**:
- T=0 is byte-oriented with *procedure bytes*; data-out (case 2/4) usually needs a follow-up **GET RESPONSE** (`00 C0 00 00 Le`) after a `61 XX`. Under pcsclite this chaining is often automatic.
- T=1 is block-oriented (NAD/PCB/LEN/INF/LRC); the whole APDU + response go in one exchange. pcsclite handles the framing.

## A) PC/SC reader

```sh
systemctl status pcscd            # daemon (socket-activated on most distros)
pcsc_scan                         # live: shows readers, card insert/remove, and the ATR
opensc-tool -l                    # list readers
opensc-tool -a                    # print ATR
opensc-tool -s 00A404000E<hex>    # send a raw APDU (if opensc is installed)
```

Send APDUs from Python with **pyscard** (`pip install pyscard`) — see `sendapdu.py` next to this file:
```python
from smartcard.System import readers
from smartcard.util import toHexString
conn = readers()[0].createConnection()
conn.connect()                                   # negotiates T=0/T=1
print("ATR:", toHexString(conn.getATR()))
data, sw1, sw2 = conn.transmit([0x00, 0xA4, 0x04, 0x00, 0x00])   # SELECT default
print(f"{toHexString(data)} SW={sw1:02X}{sw2:02X}")
```
`sendapdu.py` runs a list of hex APDUs and prints responses, with a `--gr` option to auto-issue GET RESPONSE on `61 XX`.

**JavaCard / GlobalPlatform management** (install/list/delete applets, keys): use **GlobalPlatformPro** (`gp.jar`, needs Java 11+): `java -jar gp.jar --info` / `--list` / `--install app.cap`. Default test keys are `40 41 … 4F`.

### PC/SC gotchas
- **T=0 SELECT chaining**: `SCardTransmit` under pcsclite may auto-fetch the FCI on SELECT (returning it inline), while some cards/middleware expect the two-step SELECT→`9000` then GET RESPONSE→FCI. If a card behaves oddly after SELECT, check which convention it uses.
- **Reader ATR validation**: a reader's firmware validates the ATR (length, TCK) and returns `SCARD_W_UNRESPONSIVE_CARD` for a malformed one — you never get to send an APDU. That's when you drop to the Bus Pirate (path B).
- **Memory cards** (SLE44xx, I²C EEPROM cards) are *not* T=0/T=1 microprocessor cards — they need the reader's synchronous API (`FF …` pseudo-APDUs) and won't answer normal SELECTs.
- **Contactless vs contact**: a contact reader won't talk to a contactless-only card and vice-versa.

## B) Bus Pirate (line-level)
Use the **buspirate** skill. Summary: wire IO0=I/O, IO1=CLK, IO2=RST, Vout=VCC, GND=GND; HDUART at CLK÷372 (e.g. 9600 baud @ 3.5712 MHz), 8/Even/2; power + pull-ups; pulse RST to capture the raw ATR; then hand-roll T=0 (header→procedure byte→data→SW) or T=1 (I-block) exchanges. This reads/writes *below* the reader firmware, so it can reach cards a PC/SC reader rejects.

## Quick decision
- Normal card, normal reader → **PC/SC + pyscard/opensc**.
- Manage JavaCard applets/keys → **GlobalPlatformPro**.
- Card rejected as unresponsive / need the raw ATR / non-standard config → **Bus Pirate** (buspirate skill).
