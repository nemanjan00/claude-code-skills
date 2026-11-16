# File Manifest — <COMPONENT_REGION_VERSION>

> SHA-256 of every vendor input file this analysis is based on. The files
> themselves are **not** in the repo (gitignored `processed/`); this table is the
> provenance record and the dedup key for cross-version diffing. A collaborator
> hashes their own copy and confirms it matches before trusting the docs here.

## Identity

- **Component:** <cps.exe / firmware image / installer>
- **Version:** <ProductVersion / build>
- **Region / variant:** <EMEA / NA / …>
- **Source location (local):** `processed/<COMPONENT_REGION_VERSION>/files/`
- **Analyzed:** <YYYY-MM-DD>

## Hashes

| File | Size | PE/FW version | SHA-256 |
|------|------|---------------|---------|
| `<name.dll>` | <bytes> | <ver> | `<full sha256>` |
| `<name.exe>` | <bytes> | <ver> | `<full sha256>` |

Generate / regenerate:

```sh
cd processed/<COMPONENT_REGION_VERSION>/files
sha256sum *.exe *.dll 2>/dev/null | sort -k2
```

## Diff vs <closest known version>

| File | Status | Note |
|------|--------|------|
| `<name.dll>` | IDENTICAL | hash matches <base version> — not re-analyzed |
| `<name.dll>` | CHANGED | see `DELTA.md` |
| `<name.dll>` | NEW | <what it adds> |

> **IDENTICAL = byte-identical = do not re-reverse.** Only CHANGED/NEW files get
> analyzed; findings go in `DELTA.md`.
