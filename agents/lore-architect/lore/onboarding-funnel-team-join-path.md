# Onboarding funnels: the team-join path is the one that silently goes missing

A named bug class for the onboarding-doc toolkit, found and fixed across two review rounds (`lore-framework` commit `84948e8`).

## The bug class

An onboarding funnel written from the author's fresh-start perspective railroads every reader into the **create-your-first-agent** path. The reader **joining a team that already uses Lore Agents** — arguably the more strategically important adopter — is left with no visible route. The failure recurs at every layer of the funnel, and each layer must be checked separately:

1. **Human landing prose** — README's self-drive path pointed only at FIRST-STEPS (a fresh-start-only walkthrough); the joining branch existed only buried inside QUICKSTART's AI-operator playbook.
2. **Seams introduced by the fix itself** — round 1's new join branch linked into QUICKSTART's "After install" section without first saying *install the plugin*. Fixes create new gaps (see below).
3. **The AI-instruction layer** — the INSTALL-*.md "For the AI agent reading this" preambles unconditionally said "hand the user into FIRST-STEPS.md" — the same railroading reappearing at the agent-instruction layer even after the human-facing prose was fixed.

## The shape that now ships

- README "Get started" is three short paragraphs: paste-to-AI / self-drive-fresh / joining-a-team.
- Every INSTALL preamble asks joining-vs-fresh and routes accordingly.
- Every INSTALL file ends with an "## After install" section offering both branches.

## Two transferable signposting rules (editorial-lens findings)

- **A fork question repeated across a funnel is a wayfinding cue** — its phrasing must be **verbatim identical** at every site ("joining a team that already uses Lore Agents", now at ~9 sites) so readers recognize the fork. Near-synonyms ("already has agents") destroy the effect.
- **Name a link-source section after its destination heading** ("## After install" → QUICKSTART "## After install: pick your path"), and disambiguate multi-path targets inline ("(path A)").

## Review lesson

Fixes introduce new seams: round 2 found real MED–HIGH bugs *created by* round-1 fixes. This is the concrete argument for iterate-to-convergence over single-pass review, and for checking **every layer** — human prose AND the AI-agent preambles — when a routing bug is fixed at one layer. See `parallel-reviewer-fanout-pattern.md`.

## See Also

- `paste-link-installer-doc-genre.md` — the installer-doc genre whose preambles carry the AI-instruction-layer instance of this bug.
- `onboarding-doc-narrative-pattern.md` — the human-facing funnel where the landing-prose instance lives.
- `ai-installer-review-lens.md` — the lens that catches the preamble-layer railroading a prose lens misses.
- `parallel-reviewer-fanout-pattern.md` — iterate-to-convergence; fixes-create-seams.
- `lore-agents-product-name.md` — the product name that must appear verbatim in the fork question.
