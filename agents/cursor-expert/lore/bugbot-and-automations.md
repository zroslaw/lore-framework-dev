---
lore: 1
type: topic
summary: "Bugbot (PR review, rules, effort levels, Autofix, MCP, usage pricing since mid-2026) and Automations (scheduled and event-driven cloud agents, triggers, tools, automation memories), plus Security Agents, PR Routing, and Rollouts."
parent: lore/cursor-apps-and-surfaces.md
---

# Bugbot and Automations

Checked 2026-10-14. Documented unless a line says otherwise.

## Bugbot

- Reviews PR diffs on GitHub, GitLab, Bitbucket, Azure DevOps, and Origin. Runs on every PR update,
  or on demand with a `cursor review` or `bugbot run` comment. It reads existing PR comments.
- Configure in Automations (cursor.com/automations/from-cursor/bugbot).
- Rules: `.cursor/BUGBOT.md` files (root plus files found upward from changed files), team rules in
  Automations, and **learned rules** (per organization). Cursor project rules (`.cursor/rules`) do
  **not** apply. Limits: 30,000 characters per rule, 100,000 per review. `verbose=true` lists the
  rules used.
- Effort levels: Low, Default, High, and Smart (natural-language policy). High finds 35% more bugs
  in Cursor's internal runs (blog).
- **Autofix** starts a cloud agent to fix found bugs: new branch, or commit to the existing branch
  (max 3 attempts). Needs on-demand usage and storage (not Legacy Privacy Mode).
- Run it before you push: `/review-bugbot` or `/review` in the agent (Cursor 3.7+, web, CLI). A
  shared patch ID makes the PR review skip a diff it already reviewed.
- MCP tools for Bugbot: Team and Enterprise only. Bugbot API (trigger, analytics): Enterprise.

### Bugbot pricing

- Announced 2026-05-11: Bugbot moved from a $40 per seat per month subscription to usage-based
  billing. New customers: at once. Existing customers: from the next renewal after 2026-06-08.
- Average run: $1.00–$1.50, by PR size and complexity.
- Individuals: from included usage first, then on-demand. If on-demand is off, Bugbot pauses until
  the next cycle. Teams: from on-demand spend.
- The Start plan does not include Bugbot. In The X Subscription, Bugbot ("AI code reviews") starts
  at Premium. The pricing page gives no separate Bugbot rate.

## Automations

- Cloud agents that run on a schedule (cron) or on events. Create them in the Agents Window, at
  cursor.com/automations, with the `/automate` skill, or from Marketplace templates.
- Triggers: schedules; GitHub (PR, push, labels, CI, reviews, workflow runs), GitLab, Bitbucket
  Cloud; Slack (public channels: messages, emoji, new channel); webhooks (private endpoint plus API
  key); Linear; Sentry; PagerDuty.
- Tools: open PR, comment on PR (optionally approve), request reviewers, send to Slack, read Slack,
  MCP servers, **Memories**, computer use.
- **Memories**: persistent notes across runs of one automation, stored outside the working
  filesystem (`MEMORIES.md` by default); on by default; untrusted input can poison them.
- Run as **Me** (billed to the creator) or **Service account** (team pool). Billing follows cloud
  agent usage at maximum context. Not on the Start plan.

## Other Cursor-managed agents

- **Security Agents**: Security Reviewer (PRs on Origin, GitHub, GitLab) and Vulnerability Scanner
  (code at rest). Need Cloud Agents.
- **PR Routing & Approval**: assigns reviewers and can approve low-risk PRs.
- **Rollouts** (blog 2026-09-23): writes a rollout plan per PR, checks telemetry after each deploy
  (at deploy, 20 minutes, 1 hour, 1 day, 3 days), opens issues on regressions. Teams and
  Enterprise.

Sources: https://cursor.com/docs/bugbot.md ; https://cursor.com/help/ai-features/bugbot.md ;
https://cursor.com/help/account-and-billing/bugbot-usage-based-billing.md ;
https://cursor.com/blog/may-2026-bugbot-changes ; https://cursor.com/docs/cloud-agent/automations.md ;
https://cursor.com/docs/security-agents.md ; https://cursor.com/docs/approval-agents.md ;
https://cursor.com/docs/rollouts.md ; https://cursor.com/docs/models-and-pricing.md ; https://cursor.com/pricing
