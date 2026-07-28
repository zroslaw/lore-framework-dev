# Multi-Engine Review Protocol — v31 Boot Shortcut Pin

## Goal

Converge on a fix for the **versioned plugin-cache pin** in generated per-agent boot shortcuts (`register-repo.md` bakes an absolute `<agent-boot-path>` that dies on upgrade).

## Participants

Each engine writes as itself. Identify with one of: `cursor` | `claude` | `codex`.

## Layout

```
v31-feedback/
  PROTOCOL.md          # this file (editable by consensus)
  STATUS.md            # round counter, open questions, convergence flag
  CONCLUSION.md        # written only when STATUS.converged = yes
  messages/
    NNN-<engine>.md    # zero-padded sequence, one message per file
```

## Message format

Every file under `messages/` starts with YAML frontmatter, then body:

```yaml
---
engine: cursor|claude|codex
seq: 1
type: proposal|response|counter|agree|dissent|meta
in_reply_to: null        # or seq number
topic: shortcut-boot-pin
---
```

**Types**
- `proposal` — concrete fix recommendation
- `response` — reaction to prior message(s); may refine
- `counter` — alternative that conflicts with a proposal
- `agree` — accept a named proposal (cite `in_reply_to` or proposal seq)
- `dissent` — reject with reason; must offer a counter or open question
- `meta` — protocol / process only

## Rules

1. **Append only.** Never edit another engine's message. Edit your own only to fix typos before anyone has replied to it.
2. **One concern per section.** Use short headings; keep messages pointed.
3. **Cite evidence.** Paths, observed pins, missing dirs — not vibes.
4. **Convergence.** When every participating engine has an `agree` on the same proposal seq (or an explicitly named CONCLUSION draft), the last agreer writes `CONCLUSION.md` and sets `STATUS.md` → `converged: yes`.
5. **Poll.** Check `messages/` about every 10 seconds while waiting. Do not busy-loop; sleep between checks.
6. **Idle exit.** If no new messages for 3 minutes after your last post and STATUS is not converged, leave a `meta` note and stop polling until the user nudges.
7. **Seq uniqueness.** Prefer `NNN-<engine>.md` with NNN = max existing seq + 1. If two engines race and collide on NNN, **both messages stand**; the next writer uses max+1. Do not renumber others' files.

## Shared decision object

A proposal is "ready to conclude" when it specifies all of:

- Emitter change (`register-repo.md` template text)
- Healing of existing shortcuts (yes/no + how)
- Doctor / refresh guardrail (yes/no + where)
- Explicit non-goals (what we will not do)
