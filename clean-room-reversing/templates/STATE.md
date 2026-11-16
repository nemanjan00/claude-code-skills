# <TARGET> — live state (re-read this FIRST, especially after a compaction)

Keep this file short and current. Update the **Now** section before finishing each
step. Durable rig/tool details are in `<target>/SHARP_EDGES.md` and the project
`CLAUDE.md`; host-specific access (lab PC, keys, paths) is in the gitignored
`CLAUDE.local.md`.

Evidence tags: **[HW]** measured on the device · **[VM]** emulator only · **[INF]**
inferred / unverified. Untagged = process or tooling, not a claim about the device.
Keep tagging new claims.

## Now

- **<YYYY-MM-DD HH:MM>: <the single most important current fact / what just
  happened>.** [HW/VM/INF] <device state, what's backed up (filename + sha256), what
  was read back, what is in progress.>
- **<next concrete action, and the exact command/procedure to run it>** (ref:
  `<target>/<DOC>.md`). <What gate/approval it needs; what would disprove it.>

## Backups on record (gitignored — never committed)

| Image | File | sha256 (first 8) | Device state when taken | Date |
|-------|------|------------------|-------------------------|------|
| EEPROM/codeplug | `…` | `…` | `…` | `…` |
| Full flash (golden) | `…` | `…` | `…` | `…` |

## Open questions

- <what is unknown, why it matters, and the cheapest experiment that would settle it>

## Done (brief)

- <milestone> [HW/VM]
