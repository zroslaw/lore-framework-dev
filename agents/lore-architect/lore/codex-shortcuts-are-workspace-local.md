---
lore: 1
type: topic
summary: "Codex loads skills from the repo root as well as ~/.codex/skills — so the framework's home-only shortcut location was our choice, not an engine limit; probe the engine before writing a limitation into four docs."
parent: lore-context.md
---

# Codex Shortcuts Are Workspace-Local (v37)

**The finding.** Codex CLI discovers `SKILL.md` skills from **two** roots, both listed to the model
on every turn:

- `<repo-root>/.codex/skills/<name>/SKILL.md` — repo-scoped, and `<repo-root>` is the **git root of
  the session's working directory**, or that directory itself outside a repo
- `~/.codex/skills/<name>/SKILL.md` — user-global, visible from anywhere
- `<repo-root>/.agents/skills/` also works; the framework does not use it, to keep one Codex-owned
  location per workspace and stay out of the shared `.agents/` namespace

Verified on `codex-cli 0.142.5`, 2026-08-10, with `codex debug prompt-input` — it renders the
model-visible prompt input as JSON, so a skill's presence can be confirmed **without a model call**.
Cheap enough to be the default way to answer "does this engine see X". The binary also carries
distinct `failed to stat skills root` / `failed to stat repo skills root` strings, which is what
suggested the second root existed.

**Why it mattered.** The framework had written Codex per-agent shortcuts to `~/.codex/skills/` since
v24, and by v37 that assumption had hardened into shipped prose: `workspace-push` said "no publish
path applies to them", finding S15 said they "can never arrive by git", `workspace_scan.py` carried a
`Deliberately NOT in this set` comment, and `docs/engines/codex.md` bound them to personal skills.
Four independent-looking statements, one unverified premise — Codex was the only engine whose
shortcuts a teammate could not receive by cloning the workspace.

**The generalisation.** A limitation that appears in several of your own docs is not corroborated by
appearing several times; it is one claim with copies. The copies make it *feel* settled, which is
exactly what stops anyone probing it. When a doc asserts what an external tool cannot do, ask when
that was last executed against the tool — and prefer a probe that needs no model in the loop.

Sibling of [engine-profile-must-be-observed-not-believed.md](engine-profile-must-be-observed-not-believed.md)
(observe the environment, don't believe it) and
[a-gate-cannot-be-a-model-self-report.md](a-gate-cannot-be-a-model-self-report.md) (ask what evidence
a claim rests on). Distinct from both in one way: nothing here was wrong when written — v24's Codex
may well have had one root. **A true fact about an engine has a shelf life**, and a doc gives no
signal when it expires. See also
[point-of-use-guardrails-beat-recorded-lore.md](point-of-use-guardrails-beat-recorded-lore.md): the
guardrail here is the empirical-basis line now in `docs/engines/codex.md`, naming the CLI version and
the probe command, so the next reader can re-run it instead of re-deriving it.

**What shipped in v37 (unshipped as of writing).** Registration writes
`<workspace>/.codex/skills/lr-<agent>-agent/SKILL.md`; the path joins `MANAGED_PATHS` so
`workspace-push` publishes it; `shortcut_inventory` gains a fourth key `codex_home` for the legacy
location; S15 is repurposed to "Codex shortcuts still in the home directory" and loses its
engine gate; `migrations/37.md` relocates them with a verify-before-delete rule and an
ownership check, because `~/.codex/skills` is user-global and a same-named shortcut may belong to
another workspace entirely. See [workspace-lifecycle-four-commands.md](workspace-lifecycle-four-commands.md).

**One asymmetry that remains, and is not a bug:** a Codex session started *inside* a child agent repo
resolves its repo root to that repo and sees none of the workspace's shortcuts. Claude Code's
`.claude/commands/` behaves the same way. The fix is to start the session at the workspace root, which
`docs/engines/codex.md` now says.
