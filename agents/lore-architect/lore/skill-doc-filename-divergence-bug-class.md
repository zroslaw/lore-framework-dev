# Skill-name → doc-filename divergence: a bug class, and it hid in a sibling profile

**The bug:** an instruction that tells an agent to find a skill's procedure by guessing the doc filename from the skill name — `docs/<skill>.md` — is wrong wherever the two names diverge. Confirmed divergences in `lore-framework`: `boot` → `docs/agent-boot.md`, `merge` → `docs/process-merge.md`, `reflect` → `docs/process-reflection.md`, `register-agent` → `docs/register-repo.md`. The mechanical guess produces a 404 on a real, common skill (`boot` is about as central as it gets).

**The correct pattern already existed — for one engine only.** `docs/engines/cursor.md` had explicitly named and guarded against this exact bug: *"Name mapping is not mechanical — always use the wrapper SKILL, not `docs/<skill>.md` guesswork."* Its fallback correctly reads `.cursor-skills/lr-<skill>/SKILL.md` (or, canonically, `skills/<skill>/SKILL.md`), which itself names the right doc.

**But `docs/engines/codex.md` had the exact same latent bug**, undetected until a sonnet subagent running an AI-installer review pass (see `ai-installer-review-lens.md`) traced an onboarding doc's Codex fallback instruction against the real files on disk and found it 404s for `boot`/`merge`/`reflect`/`register-agent`. Fixed at the source (`docs/engines/codex.md`, the invocation-syntax binding row) plus the onboarding docs that had copied the wording (`FIRST-STEPS.md`, `INSTALL-CODEX.md`) — confirmed on disk, all now point at `skills/<skill>/SKILL.md` instead of guessing `docs/<skill>.md`.

**The transferable lesson:** when one engine profile documents a named guardrail against a class of error, that class is not automatically engine-specific — check every sibling profile for the same latent bug rather than assuming the guardrail was only ever needed once. `docs/engines/{codex,cursor,claude}.md` share five bindings by design (`docs-engines-convention.md`); a fix in one binding's handling on one profile is a strong signal to audit the same binding on the others.

`docs/engines/codex.md` is lifecycle-harness-covered (`lifecycle-testing-harness.md`); this one-line fix was verified correct by direct file inspection, but the Codex lifecycle scenarios should still run before any further change to this binding is pushed, per the empirical pre-ship verification discipline (`role.md` § Lore-Curation Disciplines).

## See Also

- `ai-installer-review-lens.md` — the review lens that caught this, and why the newcomer/editorial lenses wouldn't have.
- `paste-link-installer-doc-genre.md` — the doc genre this bug appeared in.
- `docs-engines-convention.md` — the five-binding convention across engine profiles; audit siblings whenever one profile's binding gets a guardrail or a fix.
- `skill-doc-pattern.md` — the general skill/doc thin-pointer convention this bug is a mis-derivation of.
