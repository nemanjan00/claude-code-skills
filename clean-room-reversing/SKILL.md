---
name: clean-room-reversing
description: Structure and run a clean-room reverse-engineering + reimplementation project (radios/CPS, firmware, file formats, proprietary protocols) so nothing copyrighted lands in git — and so the work is evidence-tagged, pitfall-documented, and resumable by the next AI session. Use when starting/organizing an RE repo, deciding what is safe to commit vs. kept local (vendor binaries, firmware, decoded samples, image backups → gitignored; facts + your own code → tracked), writing a METHODOLOGY process doc (what/how/replicate), capturing rig/tool pitfalls (SHARP_EDGES), keeping a live STATE file, or tagging claims [HW]/[VM]/[INF]. Exemplar: /home/nemanjan00/rib.
---

# Clean-room reverse engineering & reimplementation

A repo layout and working method for reversing proprietary software/hardware and
shipping an open reimplementation **without redistributing anything copyrighted**,
in a way that stays **reproducible, evidence-tagged, and resumable across AI
sessions**.

Worked exemplar to read before using this: **`/home/nemanjan00/rib`** —
`METHODOLOGY.md` (the process), `CLAUDE.md` (conventions), `gm600/STATE.md` (live
state), `gm600/SHARP_EDGES.md` (pitfalls). The GM600 radio is its running example.

> This is a process + legal-hygiene pattern, not legal advice. "Functional facts
> aren't copyrightable" and interop carve-outs are jurisdiction-dependent; the
> discipline below is what keeps a project defensibly clean, not a guarantee.

---

## 1. The core split — two kinds of bytes

- **Vendor expression** — their binaries, installers, firmware images, decompiler
  output, help/manual text, sample files, **and every image backup you take off the
  radio** (codeplug/EEPROM/flash dumps are still *their* content). Copyrightable.
  **Never committed.** Lives only in gitignored dirs. A fresh clone has none of it.
- **Facts you extracted** — protocol framing, opcodes, file-format layout, field
  offsets/encodings, address maps, checksum algorithms, file hashes. Functional
  facts, **written in your own words**. These + your clean-room reimplementation
  are the repo.

**The one-line test for any file:** *"If this leaked, is it the vendor's work or
mine?"* Theirs → gitignored. Mine (a description, a hash, my own code) → tracked.

---

## 2. Repo layout

Two conventions exist; pick one and state it in `CLAUDE.md` so nobody footguns:

**A. Per-target folders (the `/rib` convention — preferred for hardware RE).**
Top level stays generic; each target gets its own tracked folder holding *all* its
findings. `docs/` is **gitignored** and holds only local vendor reference material.

```
project/
  README.md               ← TRACKED. What it does, how to use, legal note.
  CLAUDE.md               ← TRACKED. Conventions, dev setup, status, next steps.
  CLAUDE.local.md         ← GITIGNORED. Host-specific access (lab PC, keys, paths).
  METHODOLOGY.md          ← TRACKED. What was reversed, HOW, how to replicate.
  lib/ app/ cli/          ← TRACKED. Clean-room reimplementation + tooling.
  tests/                  ← TRACKED. Tests vs synthetic fixtures / a mock device.
  <target>/               ← TRACKED. e.g. gm600/ — all findings for one target:
    STATE.md              ←   live state, re-read FIRST after a compaction
    SHARP_EDGES.md        ←   rig/tool pitfalls, read BEFORE working
    PROTOCOL.md CODEPLUG.md FIRMWARE.md HARDWARE.md RECOVERY.md FAQ.md …
    <target>_codeplug.ksy ←   runnable format spec (Kaitai), not just prose
  docs/                   ← GITIGNORED. Vendor manuals/datasheets; re-fetch per
                              machine (list source URLs in CLAUDE.md).
  triage/  processed/     ← GITIGNORED (if used). Vendor-software drops & working
                              corpus — see convention B.
  *_backups/              ← GITIGNORED. codeplug_backups/, flash_backups/, golden
                              images. Theirs; also may hold the owner's serials/PII.
```

**B. triage/ + processed/ (for vendor-*software* version-tracking).** When the
subject is a desktop app you re-analyze across versions, add gitignored `triage/`
(raw drops, pre-identification) and `processed/<COMPONENT_VERSION>/` (organized
binaries), and put the *tracked* findings under `docs/<COMPONENT_VERSION>/` (here
`docs/` **is** tracked — the opposite of convention A, so don't mix the two names
in one repo without saying which you mean). A `FILE_MANIFEST.md` of SHA-256 hashes
per component is the provenance record and the dedup key: *identical hash = do not
re-reverse.*

---

## 3. What's tracked vs gitignored

**TRACKED (safe to commit):**
- Findings in prose — protocols, formats, algorithms, field meanings — **in your
  own words**, not pasted from their docs/help/decompiler.
- Offset/opcode/enum/address tables, checksum algorithms, bitfield layouts.
- File **hashes** (identify vendor files without containing them).
- Your reimplementation + a runnable format spec (Kaitai `.ksy`) + tests.
- **Synthetic** fixtures / a mock device you built (not vendor samples).
- Process docs: METHODOLOGY, per-target STATE & SHARP_EDGES, README, CLAUDE.md.

**GITIGNORED (never commit):**
- Vendor binaries/firmware/installers (`*.exe *.dll *.bin *.cab`, setup EXEs).
- Extracted/decoded vendor data: decoded codeplugs, their resource DLLs, CHM help.
- **All image backups**: codeplug/EEPROM/flash dumps, golden images (also PII risk).
- Decompiler/disassembler project databases (`*.idb *.i64 *.id0 *.nam *.til`).
- Vendor reference material (`docs/` in convention A), datasheets, manuals.
- Host-specific `CLAUDE.local.md`; build/sim artifacts (`*.vcd`, `build/`, `.venv/`).

**Grey zone:** decompiler output and their exact help/label strings are expression
— read them locally, but **transcribe the *logic/meaning* into tracked docs in your
own words**; don't paste the decompiled C or a paragraph of their help text.

---

## 4. Clean-room discipline (keep the reimplementation clean)

The implementation must be derivable from the **documented facts**, not transcribed
from their code. Flow: `binary → facts in a tracked doc → code from the doc`.

1. **Document first, implement from the doc.** If a function in `lib/` isn't
   justified by a line in a findings doc, you likely copied expression — write the
   fact in your own words first, then implement against it.
2. **Never paste their code / decompiler output into tracked files.**
3. **Prefer synthetic fixtures + a mock device.** A test that needs their sample
   file can't ship. Build the smallest synthetic artifact; gate any real-sample
   test behind a file-existence check so the suite passes on a clean clone.
4. **Encoders must round-trip vendor data byte-for-byte** (decode then re-encode
   what their tool wrote) — proven against local samples, which stay gitignored.

---

## 5. Evidence tags — mark how sure you are, everywhere

Tag every claim in every written artifact (docs, STATE, commit messages) with its
evidence level. Untagged = process/tooling, not a claim about the target.

- **[HW]** — measured on the real hardware (or byte-exact across multiple samples).
- **[VM]** — seen in the emulator/simulation only; **not** a hardware fact.
- **[INF]** — inferred / unverified; provisional.

Rules that cost `/rib` days when skipped:
- **An emulator-negative is not a firmware fact** — suspect unmodelled inputs first,
  confirm on hardware. Upgrade a tag only with new evidence.
- **Docs ported from another project start as [INF]**, however confident they read;
  re-check each claim against files/hardware you actually have.
- When an [INF] or [VM] claim is about to drive an irreversible step, test it [HW].

---

## 6. The working loop (what METHODOLOGY records)

One loop: **state a hypothesis → run the single cheapest experiment that can
disprove it → let the result decide → update → repeat.** Order instruments
cheapest-first; most lost days come from skipping the cheap one or trusting a
result with no positive control.

1. **Read what exists** — project docs, user/service manuals, the vendor tool's
   help/field list. (A user manual can answer in minutes what days of edits won't.)
2. **Get the PHY working**; prove it with an **unchanged read→write round-trip.**
3. **Back up every image before any write** — hash it, give each backup a new name
   (never overwrite), keep copies off the bench. The dated backup is also your
   diff baseline. These backups are **gitignored**.
4. **Capture the vendor tool** reading/writing before deep static work.
5. **Write-contrast**: change exactly one field in the vendor GUI, re-dump, `diff`;
   the bytes that moved are the field. Filter save/header/checksum noise.
6. **Live RAM as an instrument** (RAM-diff two known states) for what the codeplug
   doesn't show.
7. **Firmware static + emulator** only for what's left — then **confirm on hardware.**
8. **Your own code on the device** (RAM stubs) when the firmware won't do it.

Capture formats as a **runnable spec** (Kaitai), not just English.

---

## 7. Pitfall documentation is a first-class deliverable

Wrong turns are the most expensive and most reusable knowledge in RE. Capture them
deliberately — don't let them live only in scrollback:

- **Per-target `SHARP_EDGES.md`** — rig/tool gotchas. The CLAUDE.md should say
  *read it before RE work.* Each entry: the symptom, the real cause, the fix.
- **A "Pitfalls" section in METHODOLOGY** — the mistakes that generalize across
  targets (one-variable-per-experiment, coincidental terminators, checksum ranges
  hidden by padding, misread schematic pins, single-client PHY races, test patterns
  that alias a self-test like `888`, "a lost ACK ≠ not written", "a power-cycle
  revert" that was actually standby RAM).
- **Positive control before trusting a negative** — show the method detects a known
  change before you believe it detected nothing.
- **Irreversible steps get a hard gate**: every assumption has [HW] evidence, a
  verified backup exists (read back + compared), and a recovery route is known —
  before any flash/EEPROM write, hot air, or cut trace. `/rib`'s one brick came
  from a single unchecked assumption before an irreversible write.

Write the pitfall the moment it bites, with its evidence tag.

---

## 8. Lessons for AI/agent-run reversing

This method is tuned for an agent driving the bench with the owner often away:

- **Re-read the target's `STATE.md` FIRST after every context compaction**, and keep
  it short + current — update the "Now" section before ending a step. It is the
  resume point; findings live in docs, not in chat history.
- **Design eyes-free experiments.** Read the device's receive/display state from RAM
  or a live panel (screen/LEDs/flags over HTTP) instead of asking a human to look;
  use closed-loop GUI tooling, PSU control, and a webcam for proof.
- **Recompute every quoted number**, and **spot-check sub-agents' "proven" claims**
  against the actual disassembly/bytes. Don't copy numbers from pasted chats into
  docs without a source.
- **Print opcodes/addresses in hex, always** (a decimal counter once invented an
  opcode).
- **Liveness = a real reply** (a serial number, real data) — never "the socket is up".
- **Switch instruments early** (decompiler → RAM dump → emulator → capture) instead
  of grinding one for hours.
- **Ask the owner before writing to the real radio**; offer "impossible *without X*,
  here is X" rather than arguing from the emulator when they report a [HW] fact.

---

## 9. Setting it up

```sh
SKILL=~/.claude/skills/clean-room-reversing
cp $SKILL/templates/gitignore.template ./.gitignore     # merge if one exists
cp $SKILL/templates/METHODOLOGY.md     ./METHODOLOGY.md
mkdir -p <target>
cp $SKILL/templates/STATE.md        <target>/STATE.md
cp $SKILL/templates/SHARP_EDGES.md  <target>/SHARP_EDGES.md
# version-tracked vendor software instead? add docs/<COMPONENT>/FILE_MANIFEST.md:
# cp $SKILL/templates/FILE_MANIFEST.md docs/<COMPONENT>/FILE_MANIFEST.md
```

Verify nothing vendor-owned is staged, and that the ignores bite:

```sh
git status --porcelain | grep -iE '\.(exe|dll|bin|cab|cpg|cps|rdb|idb|i64|id0)$'
git check-ignore -v docs/ triage/ processed/ *_backups/ CLAUDE.local.md
git log origin/main.. --stat   # before pushing: not leaking another session's serials/PII
```

If a vendor binary/backup was **already committed** earlier, `git rm` isn't enough —
it's still in history. Flag it and plan a `git filter-repo` rewrite separately.

---

## Why it pays off

- **Legally defensible** — repo is facts + original code; point at the gitignore and
  say "we never redistributed their software or the owner's data."
- **Reproducible** — METHODOLOGY + hashes let anyone with their own vendor copy
  re-derive every finding.
- **Resumable** — STATE + per-target docs mean a new (AI) session continues instead
  of re-deriving from scrollback.
- **Self-correcting** — evidence tags and documented pitfalls stop an inference from
  hardening into a "fact" and stop you re-walking into the same trap.
