---
name: buspirate
description: Talk to a Bus Pirate 5/6 over USB serial — the BPIO2 binary interface (preferred, reliable) or the VT100 terminal (fallback). Use when scripting bus transactions (I2C/SPI/UART/HDUART/1-Wire), controlling power/pull-ups/IO pins/frequency generation, or doing ISO7816 smartcard work (read ATR, exchange APDUs, recover a card a normal reader rejects). Covers device detection, terminal quirks (DTR wake, VT100 prompt, async reads), and the smartcard recipe.
---

# Talking to a Bus Pirate 5/6 (Next-Gen, RP2040/RP2350)

## Two USB serial ports — know which is which
The Next-Gen Bus Pirate exposes **two CDC serial ports**:
- **Terminal** (`…-if00`, usually `/dev/ttyACM0`): the interactive VT100 console.
- **binmode** (`…-if02`, usually `/dev/ttyACM2`): a binary interface for scripting.

Find them:
```sh
ls -l /dev/serial/by-id/ | grep -i buspirate
```

**Rule of thumb: use BPIO2 for anything programmatic.** The terminal is fine for a human but miserable to script (see quirks below). Only drive the terminal if BPIO2 can't be enabled.

## BPIO2 — the reliable path (do this)
BPIO2 is a FlatBuffers/COBS binary interface: deterministic, framed, no text parsing.

1. Enable it once from the terminal: type `binmode`, choose **“BPIO2 flatbuffer interface”** (optionally save as default binmode).
2. `pip install pyserial cobs pybpio` (or grab the bundled tooling from the BPIO2 repo).
3. Talk on the **second** port:
```python
from pybpio.bpio_client import BPIOClient
from pybpio.bpio_i2c import BPIOI2C          # also bpio_spi, bpio_uart, bpio_1wire, bpio_led
c = BPIOClient("/dev/ttyACM2")
c.show_status()                               # sanity check
i2c = BPIOI2C(c)
i2c.configure(speed=400000, pullup_enable=True, psu_enable=True,
              psu_voltage_mv=3300, psu_current_ma=0)   # current 0 = unlimited
print(i2c.transfer(write_data=[0xA0, 0x00], read_bytes=2))
```
- Mode classes share config kwargs: `speed, data_bits, parity, stop_bits, flow_control, signal_inversion, clock_polarity, clock_phase, chip_select_idle`, plus hardware: `psu_enable/psu_set_mv/psu_set_ma, pullup_enable, io_direction(_mask)/io_value(_mask), led_color`.
- Data ops mirror the bus syntax: `start()/write()/read()/stop()` or one-shot `transfer(write_data, read_bytes)`.
- Getters: `get_status()` (one round-trip for everything), or individual `get_psu_measured_mv()` etc.
- If the 2nd port is silent: confirm BPIO2 is the active binmode and you’re on the *non-terminal* port.

## VT100 terminal — fallback only (finicky)
A robust helper is in **`bp_terminal.py`** next to this file. Quirks, all learned the hard way:
- **Wake it:** on connect, toggle **DTR low→high** to trigger the boot banner. It asks `VT100 compatible color mode? (Y/n)>` — answer **`n`** (plain text is far easier to parse).
- **Latency is high and variable** right after connect — use **expect-style** waits for a known prompt (`HiZ>`, `HDUART>`, …), never fixed sleeps.
- **Bus syntax:** `[0x00 0xA4 0x04 0x00 r:2]` — `[`/`]` = start/stop, hex = write, `r:N` = read N bytes. Pin/PSU commands: `W`(power) `P`(pullups) `G`(freq gen) `a x`/`A x`/`@ x`(IO x low/high/read).
- **Reads are noisy:** `r:N` often prints `0x00 (No data to read)` placeholders while the *real* bytes arrive **asynchronously** on the next `PROMPT> 0xNN …` line. **Parse only the bytes after the prompt**, and drop `(No data to read)`.
- **Never open at 1200 baud** — on RP2040/RP2350 that jumps to the BOOTSEL bootloader.

```python
from bp_terminal import BusPirate
bp = BusPirate("/dev/ttyACM0"); bp.wake()
print(bp.cmd("i"))                 # version/info
bp.close()
```

## ISO7816 smartcard over HDUART (read ATR, exchange APDUs, recover a card)
The BP can act as the **reader/host** on a card’s contacts — useful to read a raw ATR *below* a real reader’s ATR/TCK validation (i.e. recover a card a PC/SC reader calls “unresponsive”).

Wiring (BP pin → card contact): **IO0 = I/O (C7), IO1 = CLK (C3), IO2 = RST (C2), Vout = VCC (C1), GND = GND (C5)**.

Terminal recipe (adapt mode-menu numbers to your firmware; verify with `m`):
1. `m` → **HDUART**, **9600 baud, 8 data, Even parity, 2 stop** (baud = CLK ÷ 372).
2. `W` → `3.3` → `0`  (VCC 3.3 V, no current limit); `P` (pull-ups on).
3. `G` → **IO1** → `3.5712mhz` → `50%`  (continuous clock; 9600 × 372 = 3.5712 MHz. Duty needs the `%`.)
4. `[`  (open async read), then pulse RST on IO2: `a 2` (low), ~100 ms, `A 2` (high). The card clocks out its **ATR** on I/O — it prints after the prompt, starting `0x3b …`.
5. **APDUs** (pick protocol from the ATR’s TD1: low nibble `1` ⇒ T=1, else T=0):
   - **T=0**: write header `[CLA INS P1 P2 Lc r:1]` → read procedure byte; then `[<data…> r:2]` → SW.
   - **T=1**: one I-block `[NAD PCB LEN <APDU…> LRC r:N]`, `NAD=0x00`, `PCB=0x00`/`0x40` toggling N(S) per I-block, `LRC = XOR(all)`; success = response contains `0x90 0x00`.

Notes: the emitted protocol/ATR depends on the card, and after a card reset it stays on the power-up protocol for the whole session. Reads/writes still go through the terminal’s async quirks — parse the `HDUART> 0xNN` lines. For heavy smartcard scripting, prefer BPIO2’s HDUART data transactions instead.

## Gotchas checklist
- Two ACM ports — don’t cross terminal (if00) and binmode (if02).
- BPIO2 must be the **selected** binmode before the 2nd port responds.
- The terminal re-shows the VT100 prompt on **every** DTR toggle.
- 1200-baud open = BOOTSEL. Avoid.
- Prefer BPIO2 for anything you want to be repeatable.
