# Draft — `lr-dev`: SDLC Extension for the Lore Framework (general concept)

> **Status: active exploration, not decided.** Opened 2026-05-31 with the user (zroslaw). This is the design home for the *general* lr-dev concept. The first feature — bug-finding & test-coverage, plus the standardized bug/scenario/report formats — has its own companion draft: **`draft-lr-dev-quality.md`**. Foundational framings flagged in §10 get promoted to standalone lore topics at finalization (per `naming-foundational-principles.md`).

## 1. North star & where this fits

**North star (user, long-horizon):** convert the SDLC into a *dark factory* — software development done internally and autonomously by lore agents, with only inputs + occasional follow-ups from humans. Same direction as `autonomous-agents-vision.md` (always-on background agents with persistent task state that raise for input only when they can't decide alone, and the raising is itself a learning event).

**First concrete step:** automatically **find bugs/inconsistencies** and **raise unit-test coverage** in existing production repos — see `draft-lr-dev-quality.md`.

**Why QA is the correct beachhead (not just an easy one):** a dark factory needs *trustable autonomy*; trustable autonomy needs *cheap, automatic verification*. QA is the one SDLC activity that carries its own verification oracle — a test compiles or doesn't, passes or fails, coverage moves or doesn't, a bug reproduces or doesn't. Plus near-zero blast radius: generated tests are additive, bug reports advisory; neither mutates production behavior. So this slice lets us practice autonomy + the learning loop on safe, self-checking ground before pointing agents at code that *changes* behavior.

## 2. The spine: a three-tier knowledge model

The framework today has two knowledge tiers (universal framework + per-agent). `lr-dev` introduces a **middle tier**, and that's the unlock.

| Tier | Answers | Lives in | Bound to | Lifecycle |
|---|---|---|---|---|
| **Framework lore** | how `lr` / `lr-dev` work | the `lr` plugin | universal | framework releases |
| **Repo lore** *(new)* | **what is true about *this codebase*** (product + technical + per-artifact) | a `lore/` dir (its own repo for now) | the **repo**, not any agent | curated by lr-dev agents at finalization |
| **Agent lore** | **what *this worker* learned doing the work** | `agents/<name>/lore/` | the agent | reflect → merge |

**The cut (objective vs subjective):** repo lore describes *the artifact* and survives onboarding a fresh agent; agent lore is *the worker's experience* and is lost if the agent is deleted. Test: delete the agent → repo lore is untouched, agent lore is gone.

**Ownership rule (user-confirmed):** repo lore is **agent-agnostic**, but **only lr-dev-enabled agents may write it** (see §3 capability gate). Every other agent is **read-only** on repo lore. Writers curate it at finalization as a work product; it is stored repo-side because it's about the code, not the worker. This is the maximal expression of `team-shared-knowledge-principle.md` — shared with everyone who touches the repo, eventually merged into the repo itself so even non-LRF devs benefit.

## 3. `lr-dev` — a *module/mode* in the `lr` plugin (not a separate plugin)

User decision: keep `lr-dev` inside the same `lr` plugin; it's a **mode** an agent enters, plus a **family of dev skills**. Activation has **two independent gates**, and writing repo lore requires **both**:

**Gate A — repo is lr-dev-enabled.** A **soft signal in the source repo's `CLAUDE.md`** marks participation and points to where the repo lore lives:
- It carries the **remote location of the repo lore** so *any* agent — even non-lr-dev ones — can grasp the repo is enabled and where to read from.
- Two forms: (i) points to a **separate `dev-repo-lore` repo's remote**; or (ii) states **"the repo lore is this repo itself"** — the matured end-state where lore was merged into the source repo's `lore/`.
- **Local availability:** the working agent resolves the repo-lore's **local clone** from the workspace at runtime. **If it isn't cloned locally, we don't operate on repo lore locally this session** (curation effectively disabled; the signal still tells us it exists remotely).

**Gate B — agent is in lr-dev mode.** Either **permanent** (declared in the agent's `role.md`) or **temporary** (switched on for a session via a skill).

**Capability gate:** `write repo lore  ⟺  (Gate A) ∧ (Gate B)`. Otherwise read-only. Keeps repo lore clean (no accidental writes by agents lacking dev context) while letting any agent *consume* it.

**Skill family.** Same plugin, so skills are `lr:` skills grouped as the "lr-dev family." Working name form `lr:dev-<action>` (e.g. `lr:dev-on`, `lr:dev-analyze-file`, `lr:dev-review`). Exact namespacing syntax is open (§9).

**lr-dev is a growing *feature catalog*.** The module hosts an open, accreting set of **features**, added over time. Each feature can be **complex in its own right** — multiple workflows, instructions, and mixed manual/automated flows — and is elaborated on its own. The first feature is **bug-finding & coverage** (`draft-lr-dev-quality.md`); many more will follow. (Accretion discipline like `ailment-catalog-pattern.md`, but for capabilities rather than diagnoses.)

### 3.1 Mode-switch mechanism (proposal)

**Key insight:** in this framework a "mode" isn't a persisted runtime flag — it's **loaded operating context + an acknowledged capability**, exactly like boot already works (boot = read role + lore-context → behave accordingly). So *entering lr-dev mode = loading the lr-dev operating doc + resolving Gate A*; the conversation itself carries the state. No daemon, no state file.

- **Temporary (per session):** `/lr:dev-on [<repo>]` loads the lr-dev operating doc, verifies **Gate A** (find the `CLAUDE.md` signal + the `dev-repo-lore.md` store; check it's cloned locally), then announces: *"lr-dev mode active for `<repo>`; repo lore at `<local path>`; curation unlocked."* If the store isn't cloned → announce read-only/absent, stay out of curation. Optional `/lr:dev-off`.
- **Permanent (by role):** the agent's `role.md` declares it; boot auto-enters + runs the Gate A check for its repos.
- **Enforcement is by-convention, not by-ACL** — consistent with the framework's agent-driven nature. "Only lr-dev agents write repo lore" holds because the loaded context says so, the same way every other lore discipline holds. There is no hard permission boundary; the gate is a behavioral contract.
- **lr-dev mode is a behavioral *overlay*** that does three things: (1) unlocks repo-lore writes, (2) **extends finalization** — reflect/merge also ask "did you touch/understand an artifact? update its `.lore.md` / category topic," and (3) exposes the feature skills.
- **Boot auto-suggest:** when boot sees the `CLAUDE.md` lr-dev signal but the agent isn't a permanent lr-dev agent, emit a one-liner: *"this repo is lr-dev-enabled — `/lr:dev-on` to curate its lore."*

**Open decision — how `role.md` declares permanent mode.** Today `role.md` frontmatter is `description`-only (a convention). Options: **(a)** add a frontmatter field like `extensions: [lr-dev]` — cleanest for machine-detection, but a `role.md` schema bump (→ migration + `/lr:check` validator); **(b)** a role-*body* marker section boot parses — keeps frontmatter pure but messier to detect. Lean **(a)**.

## 4. Repo lore — structure & physical form

**Physical form (now → later).** For now, a **separate repo-lore repo per source repo** (a sibling), so it doesn't clutter the source tree or confuse devs unfamiliar with Lore. Its entire payload is a `lore/` directory, designed so it can later be **copied/merged into the source repo's root** when the team matures into a single repo holding code + lore.

**New descriptor type — `dev-repo-lore.md`.** Distinct from the agent-repo `lore-repo.md`, and its filename is the **discovery marker** for this new repo *kind* (parallel to how `lore-repo.md` marks an agent repo — tooling distinguishes the two by descriptor filename). Frontmatter:
- `version` — the lore-framework version this store is stamped at, **so future migrations run the same way as for agent repos** (single source of truth = `lore-framework/VERSION`).
- `source-repo` — the **remote URL** of the source repo this lore shadows (stable, shareable; mirrors how agent `lore-repo.md` `repos:` stores remotes, not local paths).
- `description`.
- *Local clone location is deliberately NOT committed* — machine-specific. The working agent resolves the source repo's local checkout from the workspace at runtime (§3 Gate A). A merged store (`lore/`-is-this-repo) sets `source-repo` to its own remote.

**Layout (2-level taxonomy):**
```
<repo-lore>/lore/
  dev-repo-lore.md             ← repo-lore descriptor (not an agent lore-repo.md)
  product/                     ← tech-agnostic: what problem, features, business logic
    product-lore-context.md    ← entry-point index for product lore
    overview.md
    features/
    domain-glossary.md
    constraints.md             ← SLAs, compliance, non-functional
  technical/                   ← how it's built/run
    tech-lore-context.md       ← entry-point index for technical lore
    architecture.md
    stack.md                   ← languages, frameworks, versions
    build-deploy.md
    runtime-ops.md             ← envs, servers, config
    integrations.md            ← external systems, contracts
    artifacts/                 ← per-file lore mirror (leaf of technical)
      src/foo/bar.swift  →  artifacts/src/foo/bar.lore.md
```
Category → sub-area → topics. Sub-areas above are a *starter template*, refined per repo. Cross-links allowed (knowledge-graph principle).

**Category separation & entry points (user-directed).** Product and technical lore are stored **separately**; a fact has **one home category** and is **not duplicated** across both — cross-link instead of copy (single source of truth). Each category gets its own compressed entry-point index, mirroring the agent `lore-context.md` pattern: **`product-lore-context.md`** and **`tech-lore-context.md`**. Per-artifact `.lore.md` files stay **lean and refer *up* to the specific technical topics** (or product topics, when essential) rather than restating them — pointers into the category lore, not standalone explanations.

**Per-artifact lore (`*.lore.md` mirror).** Mirrors the source folder structure; one `.lore.md` per artifact *only where warranted*.
- **Sparse + lean (user-confirmed):** include *only* what's impossible/costly/slow to derive from the file itself or the surrounding codebase. The mirror *structure* is the addressing scheme; population is sparse, not file-for-file.
- **Freshness via finalization-on-touch (user-confirmed):** at finalization, an lr-dev agent that *touched or newly understood* a file considers updating its `.lore.md`. No auto-regeneration; curated-on-touch, gated on lr-dev mode. (Staleness between touches remains an open seam — §9.)

## 5. Reusable: multi-lens code-review skill

The user's three-subagent independent review (lenses chosen by the orchestrator; address-then-decide-if-another-round) **is** my `parallel-reviewer-fanout-pattern.md`, already used in framework finalization. Promote it to a first-class **lr-dev skill** (`lr:dev-review`, name TBD) usable in *any* code-change operation — not just the quality feature. It inherits the accumulated wisdom: mutually-exclusive lenses; **round-2 = a single focused reviewer for cross-cutting drift**; **real-tool / filesystem verification, not prose-only**; graceful degradation on stalled reviewers. The quality workflow (`draft-lr-dev-quality.md`) is its first consumer.

## 6. Terminology decisions (hygiene)

- "Repo lore" / "agent lore" / "framework lore" — the three tiers (§2).
- "lr-dev mode" / "lr-dev-enabled" (repo) / "lr-dev agent" (permanent) — the activation vocabulary (§3).
- Workflow role names (`file quality analyst`, `unit quality analyst`) are defined in `draft-lr-dev-quality.md`; the rule is lowercase, function-named, deliberately **not** "...Agent" (`terminology-domain-collision-trap.md`).

## 7. (reserved)

## 8. Deferred (general)

- **No autonomous switchboard yet** — run interactively / via `/lr:spawn-teammate`; learn the loop before automating it.
- **Trust threshold** — what the agent decides alone vs. raises to the human (the dial that defines "dark"); user will define later.
- Feature-specific deferrals live in the relevant feature draft (`draft-lr-dev-quality.md` §Deferred).

## 9. Seams

**Resolved:**
- **Repo-lore descriptor** — `dev-repo-lore.md` (§4). Frontmatter: `version`, `source-repo` remote, `description`. Local clone path NOT committed — resolved at runtime.
- **Repo-enabled signal** — soft notion in the **source repo's `CLAUDE.md`** pointing to the repo-lore remote, with a "this repo itself" form for the merged end-state (§3 Gate A).
- **Repo-lore repo discovery** — the **`dev-repo-lore.md` filename is the discovery marker** for this new repo kind, parallel to `lore-repo.md` for agent repos.

**Still open:**
- **`role.md` permanent-mode declaration** — frontmatter `extensions: [lr-dev]` (schema bump) vs role-body marker (§3.1). Lean frontmatter.
- **Skill-namespacing syntax** — `lr:dev-<action>` flat vs. a cleaner sub-namespace if the plugin system allows.
- **Mode-switch skill specifics** — exact skill names (`/lr:dev-on` / `-off`), and whether boot auto-suggests on the `CLAUDE.md` signal.
- **Migrations over the new repo kind** — repo-lore stores carry a framework `version`; `/lr:update`, boot auto-upgrade, and version-check/auto-pull need to recognize/migrate/stamp `dev-repo-lore.md` repos. (Logged in `framework-improvements-backlog.md` § lr-dev.)
- **Per-artifact staleness between touches** — finalization-on-touch covers files an lr-dev agent worked; files changed by *non-lr-dev* commits drift. A staleness flag / `/lr:check`-style validator? (`freshness-contracts-at-session-boundaries.md`.)

## 10. Foundational framings to promote to lore topics (at finalization)

Per `naming-foundational-principles.md`:
- **three-tier knowledge model** (framework / repo / agent) — the spine.
- **repo lore vs agent lore** (objective artifact-knowledge vs subjective work-experience; survives-onboarding test).
- **lr-dev as mode + capability gate** (two gates; write-repo-lore requires both; else read-only; mode = loaded context, enforcement by-convention).
- **lr-dev as a growing feature catalog** (capabilities accrete; each feature may be complex/multi-workflow).
- **repo-lore structure** (separate-repo-now → mergeable `lore/` later; 2-level product/technical taxonomy with separated categories — no cross-duplication — and `product-`/`tech-lore-context` entry points; `dev-repo-lore.md` descriptor).
- **per-artifact lore mirror** (sparse `.lore.md` shadow tree; finalization-on-touch freshness).
- **multi-lens review as a reusable skill** (promotion of `parallel-reviewer-fanout-pattern.md` into lr-dev).
- *(quality-feature framings live in `draft-lr-dev-quality.md`.)*

## 11. See also

- `draft-lr-dev-quality.md` — the first feature (bug-finding & coverage) + standardized formats.
- `autonomous-agents-vision.md`, `autonomous-agents-substrate.md`, `spawn-teammate-feature.md` — the north-star direction and current substrate.
- `parallel-reviewer-fanout-pattern.md` — the multi-lens review the §5 skill promotes.
- `knowledge-vs-skills-distinction.md` — repo/agent lore are both *knowledge*; the workflow is *skills*.
- `team-shared-knowledge-principle.md` — repo lore as the maximal team-shared form.
- `framework-as-engine-not-kb.md`, `agents-are-executors-first.md` — identity framings.
- `framework-scope-vs-agent-scope.md`, `plugin-vs-agent-repo-separation.md` — placing the workflow (skills) vs the lore (content).
- `terminology-domain-collision-trap.md` — terminology hygiene.
- `freshness-contracts-at-session-boundaries.md` — extends to per-artifact staleness.
- `design-doc-before-implement.md` — why this draft exists before any framework edits.
- `framework-improvements-backlog.md` § lr-dev — backlog home.
