---
lore: 1
type: topic
summary: "A macOS login item's name comes from the filename of ProgramArguments[0] and its icon from a per-file custom-icon xattr on that same file — two unrelated sources, and no .app bundle icon is ever consulted."
parent: lore/lore-beings-design.md
---

# The Keeper's macOS Login Item: Name and Icon Come From Two Unrelated Sources

Established empirically 2026-09-05 on MacBookPro16,1 (Intel, macOS 26.6.2). This topic is the
canonical technique record; the **action item** is `framework-improvements-backlog.md` §
Autonomous Agents / Lore Beings and `workdir/what-to-improve.md` **B11**.

`lrb install` writes `ProgramArguments[0] = sys.executable` (`lore-framework/scripts/lrb.py:1511`),
so the Being Keeper (`com.lore-beings.keeper`) appears in **System Settings → General → Login Items
& Extensions → "App Background Activity"** as `python3.14` with the generic blank-document icon.
That is what every macOS Lore Beings user currently sees of their daemon.

**The load-bearing insight: the displayed name and the displayed icon have nothing to do with each
other, and fixing one does not fix the other.**

- **Name** = the *filename* of `ProgramArguments[0]`. Point launchd at a file literally named
  `Lore Keeper` and the row reads "Lore Keeper".
- **Icon** = a *per-file custom icon* on that same file: a `com.apple.ResourceFork` extended
  attribute holding an `.icns`, plus the `kIsCustomIcon` Finder flag. Set it with
  `-[NSWorkspace setIcon:forFile:options:]`. It is **not** read from an enclosing `.app` bundle's
  `CFBundleIconFile`.

## The negative result is worth more than the positive one

**macOS never resolves a `Contents/MacOS/…` path back to its enclosing bundle's icon.** Wrapping the
daemon in a proper `.app` buys the name and never the icon. Proven with a control on a known-good
comparable: Turbo Boost Switcher *does* show its icon in that pane, yet asking NSWorkspace for the
icon of its **inner** executable returns the byte-identical generic `exec` icon. It gets its icon
only because its plist runs `/usr/bin/open /Applications/Turbo Boost Switcher.app`, which makes
Background Task Management record the **bundle** path as the executable path.

## Three candidate mechanisms; only one works for a daemon

| Mechanism | Verdict |
|---|---|
| `AssociatedBundleIdentifiers` plist key (what GoogleUpdater uses) | **Blocked without a paid Developer ID.** Needs the associated bundle signed with a matching Team ID; ad-hoc signing yields `Developer Name: (null)` and BTM silently ignores the key. Verified: key added, association never recorded. |
| `ProgramArguments = ["/usr/bin/open", "<app>"]` (Turbo Boost's route) | **Unusable here.** `open` exits immediately, so `KeepAlive` respawns forever; and a LaunchServices-launched app does **not** inherit the plist's `EnvironmentVariables`, which the Keeper needs for `LRB_HOME` and a `PATH` containing `~/.local/bin` where `claude` lives. |
| **Per-file custom icon** | **Works.** No Team ID, touches only a file attribute, triggers no login-item re-registration. |

## Implementation constraints that cost real time to find

- The bundle's main executable must be a real **Mach-O binary**, not a shell script — with a script
  `codesign` reports `Format=app bundle with generic` and Launch Services refuses to treat the
  bundle as an app. A tiny C stub compiled with clang works.
- The stub must **`execv`**, not fork+exec, so the PID is preserved: launchd's `KeepAlive` tracks
  that PID and `lrb.py` records `os.getpid()` into `daemon.info`.
- Resource forks and code signing conflict, so the **ad-hoc signature must be removed before**
  setting the custom icon. Safe on Intel (unsigned x86_64 binaries execute normally). **arm64
  mandates a signature — this technique is UNVERIFIED on Apple Silicon and must be re-tested there
  before it can ship.** Treat that as an open blocker, not a formality.
- `_daemon_status()` is unaffected: it does only `os.kill(pid, 0)` and never matches on executable
  name — its own comment says it deliberately skips identity checks because framework Python
  re-execs into `Python.app`. A wrapper does not break status detection. (Verified by reading
  `lrb.py:1621`.)
- An `.app` inside a hidden dot-directory (`~/.lore-beings/`) is not indexed by Launch Services by
  default; `lsregister -f` makes it resolvable. The custom icon works regardless of location.

## Fragility

`lrb install` regenerates the plist from `sys.executable`, so **running it reverts both the name and
the icon**. Any hand-applied fix on this machine is one `lrb install` away from gone. The durable
fix belongs upstream, in `cmd_install` — which is exactly the point-of-use-guardrail argument
(`point-of-use-guardrails-beat-recorded-lore.md`): a cosmetic fix recorded only here protects one
machine for one week.

Evidence grade: **ran it** (the three mechanisms), plus **read the shipped code** (`lrb.py` claims
re-verified in this session) — `engine-bundle-reading-has-an-evidence-grade.md`. Reference
write-up, non-authoritative:
https://claude.ai/code/artifact/9f8f6482-686a-4bae-8210-d7eac86cc1cd

## See Also

- [lore-beings-design.md](lore-beings-design.md) § launchd install status — the live Keeper install
  this was found on.
- [a-displayed-attribute-can-have-more-than-one-source.md](a-displayed-attribute-can-have-more-than-one-source.md)
  — the transferable diagnostic this case named.
- [live-system-state-validate-on-a-copy-first.md](live-system-state-validate-on-a-copy-first.md) —
  what the six `bootout`/`bootstrap` cycles cost the user, and how to avoid repeating them.
- [framework-improvements-backlog.md](framework-improvements-backlog.md) § Autonomous Agents / Lore
  Beings — the upstream action item; `workdir/what-to-improve.md` **B11** is its ranked view.
