# `ps -o` with multiple fields prints one line, not one line per field (macOS)

`ps -p <pid> -o field1= -o field2=` prints BOTH fields on one line on macOS (confirmed on Darwin
25.5.0/BSD ps), not one field per line. Code that assumes multi-`-o` output is line-delimited per
field will silently concatenate them — e.g. Lore Beings' `_pid_identity` read a two-field
`lstart=`/`command=` query as one combined line, so the recorded "start time" identity anchor
actually embedded the full (mutable) command line.

Found on real macOS after three prior review passes on Lore Beings' Keeper — one running under a
sandbox that blocked `ps` entirely (Codex) — so the real-`ps` code path was never exercised until a
fourth pass. See `role.md` § Lore-Curation Disciplines for the general operating rule this
sharpened: a green suite from a review environment with a known-blocked capability doesn't verify
the code paths that depend on that capability (concrete instance detailed in
`lore-beings-mvp-takeover-review.md`).

Rule going forward: when a Keeper-style PID/process-identity check needs multiple `ps -o` fields,
issue **separate `ps` calls per field** rather than relying on any particular line-per-field
layout — portable across whatever `ps` variant is on PATH. Fixed in `scripts/lrb.py`'s
`_ps_field`/`_pid_identity` (v28).

## See Also

- `lore-beings-mvp-takeover-review.md` — the review history this bug surfaced in
- `portable-shell-in-framework-docs.md` — the broader BSD/macOS portability discipline
- `lore-beings-design.md` — the parent feature
