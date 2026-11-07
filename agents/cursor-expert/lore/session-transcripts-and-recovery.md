---
lore: 1
type: topic
summary: "Cursor transcript and recovery surfaces: CLI output, ACP loading, cloud streams, local per-agent store.db and JSONL copies (with subagent parent links), live subagent sources, and sensitive local fields."
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

## Local subagent records

Checked 2026-11-07 on macOS, Cursor app 3.28.7 and CLI `2026.11.05-86047df`. **Local** means
observed in files on one test Mac; it is not a documented schema and can change with any build.

- **Primary store (local):** `~/.cursor/chats/<workspace-hash>/<agentId>/store.db`, one SQLite
  database per agent, and each subagent has its own. Table `meta` (key `0`, hex-encoded JSON) and
  table `blobs` (encrypted; the key is in `meta`). Never print the key or the decrypted content.
- **Subagent `meta` (local):** `agentId`, `name` ("New Agent"), `createdAt` (ms), `mode`, and
  `subagentInfo {parentAgentId, rootParentAgentId, toolCallId, typeName}`. It has no status field.
  For a nested subagent, `parentAgentId` differs from `rootParentAgentId`, so the tree is
  recoverable from `meta` alone.
- **`meta.json` beside it (local):** `schemaVersion`, `createdAtMs`, `updatedAtMs`. Only some
  subagents have `isSubagent: true`; do not use that flag alone to find subagents.
- **Secondary JSONL copy (local):**
  `~/.cursor/projects/<project>/agent-transcripts/<rootId>/subagents/<childId>.jsonl`. It has no
  timestamps and no links between agents; nested children sit flat in the root's folder. The last
  entry is `turn_ended` with `success` or `aborted`. Users often take the JSONL for the main store;
  it is not.
- The editor's global `state.vscdb` did not hold these sessions. Which surface writes which store
  is unverified. Cloud Agents subagents are not in the local stores.

## Live subagent sources

**Documented** (https://cursor.com/docs/cli/acp ; https://cursor.com/docs/hooks.md ;
https://cursor.com/docs/cli/reference/output-format):

- ACP: with the `subagents` capability, subagents appear as child sessions that end completed,
  failed, or cancelled. Without it, `cursor/task` reports them, with an optional `agentId` and an
  outcome of completed, rejected, or cancelled. `rejected` means the spawn never ran.
  **Inference:** a hook deny or a policy causes `rejected`.
- Hooks: `subagentStart` and `subagentStop` ([hooks](hooks.md)).
- CLI `stream-json` has no subagent events.
- **Unverified:** whether the ACP child session ID, the hook `subagent_id`, and the store
  `agentId` are equal. Join records on `tool_call_id` (`toolCallId` in `meta`).

## Sensitive local fields

Treat these as private in any export, log, or shared record: `user_email`, `blobEncryptionKey`,
`latestRootBlobId`, task, prompt, and summary text, `modified_files`, `workspace_roots`,
`git_branch`, transcript paths, `generation_id`, and auth files.
