---
lore: 1
type: topic
summary: "An interval constant must be priced against the real cadence of the event it throttles and against any configured knob it silently overrides; one constant answering both 'is this stale?' and 'may I retry?' is wrong in both directions."
parent: lore-context.md
---

# A Rate Floor Is Wrong in Both Directions

C5 of the v46 spec keyed the workspace-refresh TTL on `last-success` instead of `last-attempt` —
correct, and the fix for a workspace that fails every attempt yet reports fresh for 16 hours. It then
added `retry_floor = 900` seconds, ANDed unconditionally, to stop a permanently-failing workspace
attempting on every boot. Two independent round-4 lenses found that one constant wrong in **opposite**
directions:

- **Too weak.** Real boots are hours apart, so a 900s floor never engages between them. The workspace
  that can never sync — offline, expired credentials, a Codex sandbox blocking `.git` network — went
  from one bounded 90s `workspace-pull` per 16 hours to one on *every boot*, permanently. A ~64×
  increase for exactly the population the floor was written to protect.
- **Too strong.** Applied regardless of outcome, it floors *every* refresh at 900s whatever the
  configured TTL, so `--workspace-ttl 0` stops meaning "always refresh" — a documented CLI contract
  pinned by two shipped tests (`test_workspace_refresh.py`, `test_ttl_zero_always_refreshes` at both
  the direct and CLI call sites;
  [a-change-set-is-wider-than-its-diff.md](a-change-set-is-wider-than-its-diff.md)).

**Both failures come from one error: a single constant answering two different questions.** "Is this
stale?" and "may I retry yet?" are separate, and the second depends on the **outcome** of the last
attempt, not merely its age. The fix: keep staleness on `last-success`; gate retries on outcome — no
floor at all when the last attempt succeeded, and `min(ttl, base * 2**(n-1))` backoff after a failure
with a `consecutive-failures` counter. A counter is safe here, unlike the marker's withdrawn ones,
because every write happens under this workspace's lock.

## Checks to run on any interval constant before shipping it

- **Compare it to the real cadence of the event it throttles.** If events are rarer than the interval,
  it does nothing — except to the population it was written for
  ([guarding-on-a-normal-state-excludes-what-matters-most.md](guarding-on-a-normal-state-excludes-what-matters-most.md)).
- **Check whether it silently overrides a configured knob**, and whether a test pins that knob's
  contract.
- **Assign every status the producing function can return to a bucket.** `setup-required` fell between
  "succeeded" and "failed" here, leaving `backoff(0)` to evaluate `2**-1` as a silent 450 seconds.
- **Gate on the real condition, not a convenient proxy** —
  [short-circuit-on-the-condition-not-a-proxy.md](short-circuit-on-the-condition-not-a-proxy.md),
  [widening-a-source-drops-its-validation.md](widening-a-source-drops-its-validation.md).

Design context: [workspace-auto-refresh-design.md](workspace-auto-refresh-design.md),
[v46-sync-hardening-tiered-plan.md](v46-sync-hardening-tiered-plan.md).
