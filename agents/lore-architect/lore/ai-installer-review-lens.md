# A fourth review lens for onboarding docs: the literal AI-installer

`parallel-reviewer-fanout-pattern.md` already covers multi-lens pre-ship review generally and now lists this as one of its lenses. This topic is the onboarding-doc-specific detail: one session used three sonnet subagents on freshly-written onboarding docs — **newcomer/adopter**, **AI-agent-as-installer**, and **editorial/concision** — two rounds to convergence. Worth naming the middle lens explicitly as an addition to the onboarding-doc review toolkit specifically (alongside the narrative/newcomer and editorial/concision lenses already implied by `onboarding-doc-narrative-pattern.md`), built for the `paste-link-installer-doc-genre.md` genre.

## The AI-installer lens

Brief the reviewer to read the docs *as the agent that must execute them literally* — not as a human judging tone, but as an executor checking whether every instruction is something it can actually perform, whether every referenced file/command/URL is real, and whether engine-specific constraints (can't self-restart, can't self-invoke a skill that shell-falls-through, can't relaunch its own session) are stated where an agent would otherwise silently fail or misreport success.

## Why it's worth the separate lens, empirically

In one session, round 1 found real bugs across all three lenses, but round 2 — after fixes were applied — surfaced one *new* HIGH-severity bug, and it came only from the installer lens: an instruction to guess `docs/<skill>.md` for a Codex fallback, wrong wherever skill-name and doc-filename diverge (see `skill-doc-filename-divergence-bug-class.md`). Neither the newcomer nor the editorial lens would have caught it — it required cross-referencing the doc's own claim against real files on disk, which is exactly what "simulate literal execution" forces and prose-reading doesn't.

## Practical framing for the reviewer brief

Don't just ask "is this clear" — ask the reviewer to *trace* each instruction against the actual repo (grep for referenced files/commands, check they exist, check the exact wording against the profile doc it's meant to mirror). Cross-checking against the underlying `docs/*.md` / `skills/*/SKILL.md` sources, not just reading the onboarding prose in isolation, is what makes this lens catch execution-fidelity bugs a pure editorial pass misses.

**Executing the CLI's help is part of the brief.** For any install/refresh doc that recommends engine CLI commands, tell the reviewer to *run the CLI's own help* (`claude plugin --help`, `claude plugin marketplace --help`, and the equivalents on other engines) to enumerate the **real** subcommands, rather than trusting the doc's prose. A doc that recommends install commands as the *refresh* path reads as plausible prose no prose-reading reviewer flags — the catch on the INSTALL-CLAUDE refresh bug (`claude-engine-capabilities.md`; re-`install` where `claude plugin update` was meant) came only from running the live help. Briefs must say so explicitly, and sonnet reviewers **do** run CLIs when instructed — the earlier miss was a briefing gap, not a model-capability gap (`persistent-reviewer-rounds` finding in `parallel-reviewer-fanout-pattern.md`).

## See Also

- `parallel-reviewer-fanout-pattern.md` — the general multi-lens pattern this lens is one entry in.
- `paste-link-installer-doc-genre.md` — the onboarding-doc genre this lens is built for.
- `skill-doc-filename-divergence-bug-class.md` — the concrete bug this lens caught that others missed.
- `sonnet-subagent-review-pattern.md` — the general sonnet-boot-as-reviewer mechanism.
