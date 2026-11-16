# <TARGET> — sharp edges (read BEFORE working)

Rig- and tool-specific gotchas that already cost time. Each entry: **symptom → real
cause → fix.** Append the moment one bites, with an evidence tag ([HW]/[VM]/[INF]).
The pitfalls that generalize to other targets go in `METHODOLOGY.md` instead.

## PHY / cabling

- **Symptom:** <e.g. first read works, the next fails.>
  **Cause:** <e.g. the vendor tool re-grabs the single-client socket between reads.>
  **Fix:** <take exclusive access while reading.> [HW]

- **Symptom:** <radio hears but never answers.>
  **Cause:** <a programming/HOOK gate on the TX path left open.>
  **Fix:** <drive the gate; trace it on the schematic first.> [HW]

## Vendor tool / VM

- **Symptom:** <...>  **Cause:** <...>  **Fix:** <...> [HW/VM]

## Codeplug / format

- **Symptom:** <a trailing `0xFFFF` looked like an end marker.>
  **Cause:** <padding from the next structure.>
  **Fix:** <use a known count, not a sentinel.> [INF→HW]

- **Checksum reach is ambiguous under padding** — a run of `0xFF` makes many
  range-ends sum the same; settle with a contrast write inside vs. outside, or read
  the validator. [HW]

## Firmware / emulator

- **Emulator sat in an endless scan** — every input pin read 0; model port/A-D
  registers from real idle measurements, and remember an emulator-negative is [VM],
  not a device fact.
- **Use the exact MCU variant's register map** — a textbook address mislabelled a
  peripheral and produced two wrong conclusions.

## Flash / irreversible

- **An unexpected before-image means STOP** — don't write over it; the bank math is
  probably wrong.
- **Hard gate before any flash/EEPROM write:** every assumption [HW]-backed, a
  verified read-back backup exists, a recovery route (off-board programmer + golden
  image) is in hand.

## Test / measurement

- **All-on / all-off patterns alias the boot self-test** (`888`) — prove with
  something asymmetric (`686`, `HI`) and confirm code still runs after the capture.
- **A lost ACK ≠ not written** — read back before deciding.
