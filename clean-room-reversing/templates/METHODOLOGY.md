# Reverse-engineering <TARGET>: methodology

How <TARGET> was worked out, written generically so it transfers to the next one.
Concrete facts live in [`<target>/`](./<target>/); rig/tool gotchas in
[`<target>/SHARP_EDGES.md`](./<target>/SHARP_EDGES.md); live state in
[`<target>/STATE.md`](./<target>/STATE.md).

The whole thing is one loop: **state a hypothesis, run the one cheapest experiment
that can disprove it, let the result decide, update, repeat.** Most lost days come
from skipping the cheap instrument, or trusting a result that had no positive
control (§8).

> **Clean-room rule:** no vendor binary, firmware, decoded sample, decompiler
> output, or image backup is committed. This repo is extracted *facts* (in our own
> words) + our *original* reimplementation. Vendor files and all dumps live in
> gitignored dirs; supply your own to reproduce.

## 0. Order of work — cheapest instrument first

1. **Read what already exists** — project docs, owner/service manuals, the vendor
   tool's help/field list. (A user manual can answer in minutes what days of edits
   can't.)
2. **Get the PHY working** and prove it with an unchanged read→write round-trip.
3. **Back up every image before any write that could change it.** Hash each, record
   the device state, keep copies off the bench, **never overwrite** (new name each
   time). These backups are gitignored (they're the vendor's content + may hold the
   owner's serials/PII). A dated backup is also your diff baseline.
4. **Capture the vendor tool** reading/writing *before* deep static address-map work.
5. **Write-contrast through the vendor GUI** for anything it can edit (§3).
6. **Live RAM as an instrument** for behaviour the codeplug doesn't show (§4).
7. **Firmware static + emulator** for what's left (§5, §6) — confirm on hardware.
8. **Your own code on the device** (RAM stubs, §7) when the firmware won't cooperate.

Ask the owner for one observable ground-truth value early (display text, a channel,
a label) and search for it — it anchors everything.

## 1. Protocol & file format — static, no device

Get the vendor programming software; run it in a VM if it needs a dead OS.
Disassemble it and recover: the **serial framing** (opcodes, length/escape,
checksum), the **file format** (obfuscation/crypto + field layout), and the **field
dictionary** (help topics / field registry name every field with ranges, enums,
scope). Then pair known plaintext (vendor file ↔ native dump) to solve encodings;
sanity-check against fixed constants (band edges, cal tables); make encoders
round-trip vendor data byte-for-byte. Print opcodes/addresses in hex, always.

## 2. The PHY

Implement the wire protocol with deterministic timing; match the reference device's
behaviour before adding cleverness. Prove it by reading the config and writing it
back **unchanged**. Trace every gate on the device's TX path on the schematic before
the first transmit.

## 3. Capture, then decode fields by write-contrast — the workhorse

Sniff the vendor tool's Read/Write; build a **mock device** and prove it faithful by
replaying the capture byte-for-byte. Then: change **exactly one** field → write/save
→ re-dump → `diff` a baseline. Bytes that moved = that field. Isolate one variable;
filter save/header/checksum noise; get the checksum algorithm from the firmware
validator, not by guessing. Capture the result as a **runnable spec** (Kaitai) plus
prose. Edit only through one safe write path (backup, refuse bad checksums, fix
checksums, write changed chunks, read back).

## 4. Live RAM as an instrument

If the protocol can read RAM while firmware runs: **RAM-diff two known states** (dump
twice in A, twice in B; keep bytes stable-within and different-between). Do this
before decoding any buffer by hand. Check uniqueness over the whole image; avoid
registers with read side effects; turn results into a live panel for eyes-free
observation.

## 5. Firmware — static

Dump the firmware (off-board programmer, or in-circuit RAM stub) and keep a hashed
**golden image** (gitignored). Raw-byte xref scans find dispatchers fast. Use the
**exact** MCU variant's register map. Identify a table's real consumer before giving
it meaning. The firmware's self-test is a pass/fail oracle for any patch.

## 6. The emulator as an oracle — and its limits

A cycle-level emulator that boots the real firmware is a force multiplier (tracing,
snapshots, safe experiments), but: **model inputs from hardware measurements** (an
all-zero input pin sent the VM into an endless scan and a week of invented
explanations); validate the CPU core; lockstep-diff good vs. patched runs to the
first divergent PC; port a routine and cross-check it against the firmware on random
inputs before trusting it. **An emulator-negative is [VM], not a firmware fact —
confirm on hardware.**

## 7. Running your own code on the device

Upload a RAM stub; launch it (e.g. a jump-to-address backdoor opcode). Know your
free RAM (zero in every dump, unreferenced); re-verify immediately before launch;
give every stub a self-check; tier the validation (trivial stub first). For flash
writes: trace **all** memory control pins (/CE /OE /WE) on the schematic; separate
"applied at reset" from "while running"; an unexpected before-image means **stop**;
verify through an independent read path; hash the deployed stub against the repo
before launching; back up the live sector first.

## 8. Evidence rules

- **Positive control**: before trusting a negative, show the method detects a known
  change.
- **Distinctive test patterns**: all-on/all-off alias boot self-tests (`888`); prove
  with something asymmetric (`686`, `HI`) and confirm the code still runs after the
  capture.
- **A lost ACK ≠ not written** — read back before deciding.
- **Persistence needs a real power-off test** (watch for standby RAM).
- **Recompute every quoted number**; spot-check sub-agents' "proven" claims in the
  disassembly. Don't copy numbers from pasted chats into docs without a source.
- **Liveness = a real reply** (a serial, real data), never "the socket is up".
- **Tag every claim**: **[HW]** measured on hardware · **[VM]** emulator only ·
  **[INF]** inferred. Untagged = process/tooling. Ported docs start **[INF]**.
  Upgrade a tag only with new evidence; test [INF]/[VM] on hardware before it drives
  a decision.
- **Irreversible steps get a hard gate**: (1) every assumption has [HW] evidence;
  (2) a verified, read-back backup exists; (3) a recovery route is known — before any
  flash/EEPROM write, hot air, or cut trace.

## 9. Working as an agent + with the owner

- Re-read `<target>/STATE.md` after every compaction; update its "Now" before ending
  a step. Docs record **findings**, not troubleshooting narrative.
- Design experiments that need no human eyes (RAM/live panel, GUI tooling, PSU,
  webcam); the owner is usually not at the bench.
- Switch instruments early instead of grinding one. Ask before writing to the real
  device; re-test an owner-reported [HW] fact rather than arguing from the emulator.

## Toolbox

| Tool | Use |
|---|---|
| <PHY, e.g. Glasgow> | the RIB-less PHY (deterministic timing) |
| IDA / r2 + Ghidra | disassemble vendor software + device firmware |
| Kaitai Struct | the config/codeplug as a runnable, viewable spec |
| QEMU | run dead vendor software (Win3.1 / DOS) |
| <emulator, e.g. emu6811> | boots the firmware: tracing, snapshots, safe experiments |
| Bench PSU (USB-controlled) | power-cycle = recovery from a hung stub |
| Webcam | eyes-free proof of display/LED state |
| Chip programmer (T48/…) | off-board flash read/write (golden image, recovery) |
| Logic analyzer | passively trace an external bus |

## Pitfalls hit along the way

> Append the moment one bites, with an evidence tag. Target-specific rig/tool gotchas
> go in `<target>/SHARP_EDGES.md`; the ones that generalize go here.

- **One variable per experiment** — treat header, save-metadata and checksum deltas
  as noise.
- **Coincidental terminators** — a `0xFFFF` after a table was padding, not an end
  marker. Prefer a known count over a sentinel.
- **Checksum ranges hidden by padding** — a run of `0xFF` makes many range-ends give
  the same sum; settle it with a contrast write just inside vs. outside, or read the
  validator.
- **Single-client PHY races** — the vendor tool (or its VM serial chardev) can
  re-grab a single-client socket between reads; take exclusive access.
- **Misread schematic pins** — verify grid designators; tap the accessible end of a
  net; watch for not-fitted parts that make a pin dead.
- **<add target-specific pitfalls as they happen — [HW]/[VM]/[INF]>**

## Untested approaches — ideas, not done here

- **<e.g. bootstrap mode, differential firmware diff, newer-MCU BDM access>** — note
  what was tried, why it stalled, and what it needs next.
