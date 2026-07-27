# Literate Accelerator Pattern

A refinement of the **Accelerator** half of the Script Fallback Contract
(`lore-framework/docs/conventions.md` § Script Fallback Contract): instead of a script that
accelerates a procedure documented separately in a `docs/*.md` file, the procedure lives inside the
script itself, as instructional comments — docstrings and inline `# Step N:` blocks written as
freestanding instructions a reader could execute *without running the code*. The script is one
artifact that serves two purposes: it runs, and its own text is the fallback spec when it can't.

## The problem this solves

Plain "Accelerator" (prose doc normative, script implements it) still leaves two versions of the
same truth in two files. Nothing stops them from drifting: someone tweaks the script's logic and
forgets the doc, or edits the doc's wording and the script quietly no longer matches it. Worse,
the doc is the thing a caller falls back to exactly when the script — the thing most likely to
have been kept current by whoever last touched the *behavior* — has just failed. The fallback the
framework trusts most, in the moment it's needed most, is the one most likely to have rotted.

Collapsing procedure and implementation into one file removes the seam. There's nothing left to
drift apart, because there's only one thing.

## The cost: the pattern cannot self-serve when the artifact is gone

The seam this removes was also a redundancy. A plain accelerator's fallback lived in a *different*
file from the thing that broke, so it was present by construction; a literate accelerator's
fallback rides in the artifact that just failed. That is fine for the common failures — a bad exit,
a missing interpreter, unparsable output all leave the file readable — but it has no floor when the
script is **missing, truncated, or unreadable**. The pattern then specifies nothing at all, and an
executor left to improvise from a function name produces a silent partial imitation of the
procedure, which is worse than a reported inability to run it.

So any literate accelerator must **name its floor explicitly** in the contract rather than leaving
the executor to discover the gap mid-failure: recover the procedure from git history or another
install, and failing that, say plainly which operation cannot be performed. This was found by the
hand-executor lens in v31's trilens round 1 — the doc set covered every failure mode *except* the
one that makes the design different from its predecessor. Generalizes: when a design removes a
redundancy, audit the case the redundancy used to cover.

## The one rule that makes it work

**A comment must read as an instruction, not as an annotation of the adjacent code.**

- Not this: `# call git pull` (describes what the next line does — useless if you can't run it)
- This: `` Run `git -C <repo> pull --ff-only` with `GIT_TERMINAL_PROMPT=0` and
  `GIT_SSH_COMMAND='ssh -o BatchMode=yes -o ConnectTimeout=10'` so an unauthenticated remote fails
  fast instead of hanging on a prompt. `` (a step a person could execute by hand, with the exact
  command and the reason for each flag)

Concretely this means: exact commands with exact flags, exact file paths (not "the stamp file" but
`<absolute-git-dir>/lr-last-pull`), and the decision rules for branching (what counts as "fresh,"
what "skip" vs "fail" means and why the distinction matters). If a step references another
function for its detail, name that function so the reader knows where to look next — don't
inline a partial restatement.

## What changes in the doc/script relationship

- The script's module docstring and each `cmd_*`/helper function's docstring **are** the
  procedure. A doc that delegates to it carries a **short pointer**: what to call, what the output
  fields mean, and — on failure — *which function* names the steps to execute.
  `docs/agent-boot.md`, `docs/auto-pull.md`, `docs/attach.md`, `docs/consult.md`,
  `docs/lore-search.md`, `docs/process-merge.md`, `docs/pull-lore.md`, and `docs/being.md` all
  follow this now for `scripts/lr-core`.
- **Point at the function that carries the steps, not the one that does the work.** Round 1 of
  v31's review caught `consult.md` and `lore-search.md` pointing at `discover_workspace`/`scan_lore`
  — the implementation halves, which have no docstrings at all — while the numbered procedures live
  in `cmd_discover`/`cmd_scan`. A pointer that lands on the non-literate half fails the pattern
  exactly where it is supposed to pay off, and nothing detects it automatically.
- Conceptual framing that *isn't* duplicated by the script stays in the doc — e.g. `auto-pull.md`
  keeps the per-calling-site reporting-verbosity table (boot/attach/merge silent vs. `/lr:pull-lore`
  verbose), because that's caller-side policy the script doesn't decide, not a restatement of what
  `pull_repo()` does.
- On a script failure, the caller reads the named function's comments in the script itself and
  executes those steps by hand — not a separate prose doc.

## First instance

`scripts/lr-core`, v31. Still on branch `wip/lr-core-v31` and not shipped at the time of writing —
see `v31-lr-core-parked-2026-07-25.md` (that topic lives on this repo's `main`, which this branch
has not yet merged, so the link resolves only after the branch catches up). The
redesign was applied across the whole script: the module docstring's "WHAT THIS IS NOT" claim
flipped from "procedure docs remain normative" to naming the script's own comments as the spec;
`cmd_preflight`/`cmd_discover`/`cmd_scan` each gained numbered step docstrings; `pull_repo`,
`compare_versions`, `detect_teammate`, and `_resolve_agent` had their docstrings tightened from
"why we did this" framing to "do this — here's why," with exact commands/paths/rules spelled out.
No behavioral change — comments and surrounding prose only.

## Applying this to future scripts

Reach for this pattern whenever a new accelerator script is proposed: write its procedure as the
script's own instructional comments from the start, rather than drafting a companion prose doc and
mechanizing it later. The distinction from **Implementation** scripts
(`scripts/workspace-pull`, `scripts/lrb.py`, etc. — the script *is* the spec, nothing to fall back
to) is unchanged; this pattern only applies to the Accelerator half of the split.

See `subagent-as-optimization-vs-subagent-as-semantics.md` for a related but distinct classification
question (what a *subagent* is for, not what a *script's* fallback is) and
`single-canonical-source-discipline.md` for the general principle this is one instance of.
