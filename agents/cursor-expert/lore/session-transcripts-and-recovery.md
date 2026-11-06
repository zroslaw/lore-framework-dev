---
lore: 1
type: topic
summary: "Cursor transcript and recovery surfaces: CLI output, ACP loading, cloud streams, and the limits of local storage observations."
parent: lore/cursor-apps-and-surfaces.md
---

# Session transcripts and recovery

Checked 2026-11-06. Cursor's editor, CLI, ACP, and cloud surfaces have different transcript and
recovery capabilities. Readable output alone does not establish that a session can be resumed or
moved to another machine.

**Documented:** CLI partial streaming can repeat content in flush events; print mode suppresses
thinking. Reconcile partial and complete messages instead of appending every event as new text.
Source: https://cursor.com/docs/cli/reference/output-format.

**Documented:** ACP has `session/load`. This establishes a loading operation, not a guarantee of
complete replay or portability. Source: https://cursor.com/docs/cli/acp.

**Documented:** Cloud Agents v1 provides run-scoped SSE with finite retention; tool payloads can be
truncated. Check current retention and payload limits before designing a consumer. Source:
https://cursor.com/docs/cloud-agent/api/endpoints.

**Observed in one controlled CLI test:** the JSONL transcript omitted request ID and usage that
appeared in the terminal result. The local SQLite store contained a content-hashed blob graph and
more material than the visible JSONL. This observation is version-specific: it does not establish
a stable file schema, complete history, or a supported restoration method. Do not assume local
storage is safe to share without inspection. The observation is not an official product guarantee.
