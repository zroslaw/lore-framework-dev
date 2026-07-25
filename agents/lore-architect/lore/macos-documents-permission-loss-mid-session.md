# macOS Documents-Permission Loss Mid-Session (Environment Ailment)

An environment failure that looks exactly like a code or repo bug and is neither. Worth recognizing
fast, because every verdict produced across the transition is uninterpretable.

## Symptom

Partway through a session, every read under `~/Documents` began failing with `Operation not permitted`
/ `EPERM` — from the Bash tool, from the Read tool, and from a spawned test subprocess. `ls ~` and
`~/.claude/jobs/...` kept working. File modes were normal (`-rw-r--r--`), and the same paths had been
readable minutes earlier. Since the whole workspace lives under `~/Documents/agent-workspace`, this
takes out the framework, the agent repos, and the test fixtures at once.

## Misdiagnoses to skip

- **A file-permission or xattr problem** — it is not; `chmod` and `xattr` also return `Operation not
  permitted`.
- **Session CWD drift after a `cd`** — restoring the cwd changes nothing.
- **Something the test harness did to the repo** — the *main* checkout, untouched all session, is
  equally blocked.

## Diagnosis

macOS **TCC** (System Settings → Privacy & Security → Files and Folders / Full Disk Access) for the
terminal or engine app was revoked or reset mid-session. The scope is the *protected directory*, not
the repo: **`~/Documents` blocked while `~` is fine is the signature.** Confirm with a one-liner that
probes `~`, `~/Documents`, and a non-protected dir separately.

## Fix

The user re-grants the terminal/engine access in System Settings → Privacy & Security, then starts a
fresh session. **Nothing an agent can repair itself** — recognizing it and saying so is the whole job.

## Blast radius on a lifecycle run

It corrupted one invocation in two different ways: one scenario's engine subprocess hung to its full
900s timeout (it could not read the plugin under test), and the next scenario failed in
`build_fixture` reading `VERSION`. **A green/red result spanning the transition is uninterpretable —
re-run after the fix rather than attributing the failures to the code under test.**

This is a concrete instance of the sandboxed/degraded-environment blind spot in `role.md`
§ Lore-Curation Disciplines: before believing either verdict, check whether the environment blocked a
capability the test depends on. It is also what made v30's post-convergence edits unverifiable — see
`post-convergence-edits-need-their-own-gate.md`.

## Framework follow-up

Candidate for the `/lr:doctor` ailment catalog (`doctor-macos-tcc-permission-loss`): the symptom is
distinctive, the diagnosis is a one-line probe, and the fix is a one-line instruction to the user. It
clears the universality gate — any macOS user with a workspace under a TCC-protected directory can hit
it. Filed in `framework-improvements-backlog.md` § Ailment Catalog.

## See Also

- `ailment-catalog-pattern.md` — the catalog this belongs in, and the authoring schema for a member.
- `lifecycle-testing-harness.md` — the run this corrupted; the debug discipline for ambiguous results.
- `verify-before-acting-on-suspected-bugs.md` — verify *which* bug before fixing anything.
- `post-convergence-edits-need-their-own-gate.md` — why a destroyed recheck is not a neutral event.
- `execution-testing-catches-blind-ambiguity.md` — TCC prompts also surfaced in the original
  `agent-boot.md` fidelity work, when haiku escalated to a filesystem-wide `find`.
