#!/usr/bin/env python3
"""Probe catalog for the lore-agent quality benchmark (PoC).

Design: lore-architect workdir/draft-lore-quality-benchmark.md.

Each probe plants knowledge in the fixture agent's lore (the "needle"), gives
the agent a task where that knowledge should change the output, and scores
three stages:

  S1 retrieval  — did the agent read the load-bearing lore file? (tool trace)
  S2 grounding  — does the output carry the planted fact? (script check)
  S3 application — did the behavior change the right way? (LLM judge, binary)

Every probe runs in two arms:
  treatment — lore contains the fact
  control   — same repo shape and topic filenames, fact removed/neutralized
The score delta between arms is the Lore Uplift.

v2 catalog (18 probes, 8 categories):
  decision-recall      P1 easy, P4 paraphrase, P9 counter-default
  gotcha-avoidance     P2 easy, P5 two-hop, P10 parametric
  abstention           P3 easy, P8 tempted-near-miss, P17 tempted-general-knowledge
  knowledge-update     P6 explicit-supersedes, P13 dated-contradiction (no marker)
  implicit-adaptation  P7 dry-run norm, P18 output convention
  negative-knowledge   P11 failed attempt, P12 banned library
  synthesis            P14 two needles (fetch+upload), P15 two needles (auth+schedule)
  workdir-tool         P16 use the existing audited tool, don't rewrite

Multi-needle probes set `s1_target` to a list — S1 passes only if EVERY listed
file appears in the tool-input trace. WORKDIR_FILES are written identically in
both arms; only the lore topic pointing at them differs.
"""

# --- Needle topics: filename -> per-arm content -------------------------------
# Filenames and lore-context listing are identical across arms; only the
# knowledge differs. Entry/pointer topics used for multi-hop probes live in
# DISTRACTOR_TOPICS (identical in both arms) — the needle is the deep topic.

NEEDLE_TOPICS = {
    "http-client-choice.md": {
        "treatment": (
            "# HTTP Client Choice\n\n"
            "Decision: all fixture-project scripts use the internal HTTP client "
            "library **falcon-fetch** — never `requests` or raw `urllib`.\n\n"
            "Reason: falcon-fetch injects the project's rotating auth headers "
            "automatically; the other clients silently get 401s in staging.\n"
        ),
        "control": (
            "# HTTP Client Choice\n\n"
            "Several HTTP client libraries are in use across fixture-project "
            "scripts. No firm decision has been recorded yet.\n"
        ),
    },
    "petrel-records-api.md": {
        "treatment": (
            "# Petrel Records API\n\n"
            "Gotcha: the petrel-records API **silently drops** any batch larger "
            "than 25 records — no error is returned.\n\n"
            "Always chunk uploads to `POST /records/batch` into batches of at "
            "most 25.\n"
        ),
        "control": (
            "# Petrel Records API\n\n"
            "The petrel-records API accepts record uploads via "
            "`POST /records/batch`.\n"
        ),
    },
    # P4 needle — paraphrase probe: the task talks about "pushing build
    # artifacts to the cloud bucket" and never uses the words below.
    "object-storage-uploads.md": {
        "treatment": (
            "# Object Storage Uploads\n\n"
            "Decision: every write of files or artifacts to the project's "
            "object storage goes through the internal wrapper library "
            "**heron-store** — never boto3 or any S3 SDK directly.\n\n"
            "Reason: heron-store stamps the mandatory server-side encryption "
            "tags; direct SDK writes are quarantined by the bucket policy.\n"
        ),
        "control": (
            "# Object Storage Uploads\n\n"
            "Project artifacts are kept in object storage. Several client "
            "libraries are in use; no convention has been recorded.\n"
        ),
    },
    # P5 needle — two-hop probe: lore-context lists database-migrations.md
    # (a pointer topic, identical in both arms), which links here.
    "grebe-replica-lag.md": {
        "treatment": (
            "# Grebe Replica Lag\n\n"
            "The grebe replica takes its nightly consistency snapshot between "
            "**02:00 and 04:00 UTC**. Never schedule migrations or bulk "
            "writes in that window — they corrupt the snapshot and force a "
            "full resync. Safe window starts at 05:00 UTC.\n"
        ),
        "control": (
            "# Grebe Replica Lag\n\n"
            "Replica lag for the grebe database is monitored in Grafana.\n"
        ),
    },
    # P6 needle — knowledge-update probe: api-auth-tokens.md (the OLD fact,
    # identical in both arms) says static keys; this newer topic supersedes it
    # only in the treatment arm.
    "api-auth-migration-2026.md": {
        "treatment": (
            "# API Auth Migration (2026)\n\n"
            "As of 2026-03, static API keys are **deprecated**. All service "
            "calls must authenticate with short-lived **kite-tokens** fetched "
            "from the vault sidecar (`GET http://localhost:8200/kite-token`). "
            "Staging already rejects static keys. This supersedes "
            "`api-auth-tokens.md`.\n"
        ),
        "control": (
            "# API Auth Migration (2026)\n\n"
            "A migration away from static API keys has been discussed. "
            "No decision has been recorded yet.\n"
        ),
    },
    # P7 needle — implicit-adaptation probe: a norm the task never mentions.
    "script-conventions.md": {
        "treatment": (
            "# Script Conventions\n\n"
            "Every operational script MUST implement a `--dry-run` flag that "
            "prints the planned actions without executing them. Reviewers "
            "reject scripts without it (post-2025 data-loss incident).\n"
        ),
        "control": (
            "# Script Conventions\n\n"
            "Scripts follow PEP8 and standard argparse patterns.\n"
        ),
    },
    # P9 needle — counter-default probe: the recorded decision contradicts
    # common best practice (adding client-side retries).
    "upload-retry-policy.md": {
        "treatment": (
            "# Upload Retry Policy\n\n"
            "Decision: record-upload clients must **NOT retry** failed uploads "
            "client-side. The records API already retries server-side; client "
            "retries create duplicate records (2025 billing incident). On "
            "failure: fail fast and log the failed batch ids.\n"
        ),
        "control": (
            "# Upload Retry Policy\n\n"
            "Retry behavior for record uploads has not been standardized yet.\n"
        ),
    },
    # P10 needle — parametric probe: an exact figure must survive into code.
    "records-api-rate-limits.md": {
        "treatment": (
            "# Records API Rate Limits\n\n"
            "The records API enforces a hard limit of **40 requests per "
            "minute** per token; exceeding it returns 429s and temporarily "
            "blacklists the token. Bulk clients must throttle below 40/min.\n"
        ),
        "control": (
            "# Records API Rate Limits\n\n"
            "The records API applies standard rate limiting managed by the "
            "platform team.\n"
        ),
    },
    # P11 needle — negative knowledge: a failed attempt that must not be
    # re-proposed.
    "records-caching-history.md": {
        "treatment": (
            "# Records Caching History\n\n"
            "We tried a Redis cache in front of the records API in 2025 and "
            "**rolled it back**: invalidation raced with the nightly "
            "consistency snapshot and served stale records to billing. "
            "Decision: no cache layer in front of records — use server-side "
            "pagination and the bulk endpoints instead.\n"
        ),
        "control": (
            "# Records Caching History\n\n"
            "Caching options for the records API have been discussed "
            "occasionally.\n"
        ),
    },
    # P12 needle — negative knowledge: a banned library with a recorded reason.
    "etl-dataframe-policy.md": {
        "treatment": (
            "# ETL DataFrame Policy\n\n"
            "pandas is **banned in records ETL** (2025): loading prod-size "
            "record dumps into DataFrames caused repeated OOM kills. Records "
            "ETL scripts must stream row-by-row (csv module / generators), "
            "never load the full dataset into memory.\n"
        ),
        "control": (
            "# ETL DataFrame Policy\n\n"
            "Records ETL scripts are written in Python. No library policy has "
            "been recorded.\n"
        ),
    },
    # P13 needle — dated contradiction: deployment-target.md (distractor,
    # identical in both arms) still says kestrel VMs; this topic wins on its
    # date and content alone — deliberately NO explicit supersedes marker
    # (that easier variant is P6).
    "deployment-target-2026.md": {
        "treatment": (
            "# Deployment Target (2026)\n\n"
            "As of 2026-04 all services deploy to the **merlin** Kubernetes "
            "cluster (`merlinctl deploy <service>`). The kestrel VM cluster "
            "is drained and read-only; new deployments there fail silently.\n"
        ),
        "control": (
            "# Deployment Target (2026)\n\n"
            "A migration of deployments to Kubernetes has been discussed for "
            "2026. No decision has been recorded.\n"
        ),
    },
    # P16 needle — workdir-tool probe: lore points at an existing audited tool
    # (workdir/tools/export_records.py, identical in both arms via
    # WORKDIR_FILES); the agent should use it rather than write fresh code.
    "records-export-tool.md": {
        "treatment": (
            "# Records Export Tool\n\n"
            "All records exports MUST go through the audited exporter at "
            "`workdir/tools/export_records.py` "
            "(`python3 workdir/tools/export_records.py --since <date> --out "
            "<csv>`). It writes the mandatory audit-log entry; ad-hoc export "
            "code skips auditing and is banned since the 2025 compliance "
            "review.\n"
        ),
        "control": (
            "# Records Export Tool\n\n"
            "Records can be exported from the records API when needed.\n"
        ),
    },
    # P18 needle — second implicit-adaptation probe: an output norm the task
    # never hints at.
    "cli-output-conventions.md": {
        "treatment": (
            "# CLI Output Conventions\n\n"
            "Operational scripts print machine-readable **JSON to stdout** "
            "(the ops tooling parses it); human-readable progress and "
            "messages go to **stderr** only. Mixed plain-text stdout breaks "
            "the tooling.\n"
        ),
        "control": (
            "# CLI Output Conventions\n\n"
            "Scripts print status messages to the console.\n"
        ),
    },
}

# --- Distractor topics: identical in both arms --------------------------------

DISTRACTOR_TOPICS = {
    "build-tool.md": (
        "# Build Tool\n\nThe fixture project builds with espresso-tamper; "
        "watch mode is the reason it was chosen over portafilter.\n"
    ),
    "deploy-cadence.md": (
        "# Deploy Cadence\n\nDeploys go out Tuesday and Thursday mornings. "
        "Friday deploys are banned after the 2025 outage.\n"
    ),
    "naming-conventions.md": (
        "# Naming Conventions\n\nPython modules use snake_case; service names "
        "use bird names (petrel, grebe, kestrel).\n"
    ),
    "logging-format.md": (
        "# Logging Format\n\nAll services log JSON lines with `ts`, `level`, "
        "`svc`, `msg` keys. Plain-text logs break the collector.\n"
    ),
    "test-data-policy.md": (
        "# Test Data Policy\n\nNever use production records in tests; the "
        "faker seed lives in tools/seed.py.\n"
    ),
    "release-checklist.md": (
        "# Release Checklist\n\nTag, changelog, staging smoke test, then "
        "production. Skipping staging requires lead sign-off.\n"
    ),
    "timezone-handling.md": (
        "# Timezone Handling\n\nAll timestamps are stored UTC; conversion "
        "happens only at the UI layer.\n"
    ),
    "notification-email-style.md": (
        "# Notification Email Style\n\nSystem emails are plain text, no HTML. "
        "Sender is noreply@fixture.example.\n"
    ),
    # Pointer topic for the two-hop probe (P5) — identical in both arms; the
    # needle lives one link further, in grebe-replica-lag.md.
    "database-migrations.md": (
        "# Database Migrations\n\nMigrations run via `tools/migrate.py`. "
        "For scheduling constraints around replication, see "
        "`grebe-replica-lag.md`.\n"
    ),
    # The OLD auth fact for the knowledge-update probe (P6) — identical in
    # both arms; only the superseding topic differs.
    "api-auth-tokens.md": (
        "# API Auth Tokens\n\nServices authenticate to the project API with "
        "static API keys sent in the `X-Api-Key` header. Keys live in the "
        "team vault.\n"
    ),
    "ci-pipeline.md": (
        "# CI Pipeline\n\nCI runs on kestrel-runners; a red main blocks all "
        "merges until fixed.\n"
    ),
    "oncall-rotation.md": (
        "# Oncall Rotation\n\nWeekly rotation, handoff Monday 10:00 local. "
        "Escalation goes through the team lead.\n"
    ),
    "feature-flags.md": (
        "# Feature Flags\n\nFlags live in flags.yaml; stale flags are removed "
        "quarterly.\n"
    ),
    "error-budget-policy.md": (
        "# Error Budget Policy\n\nWhen the monthly error budget is spent, "
        "feature work pauses in favor of reliability work.\n"
    ),
    "dependency-pinning.md": (
        "# Dependency Pinning\n\nAll Python dependencies are pinned exactly "
        "in requirements.lock; ranges are not allowed.\n"
    ),
    "api-versioning.md": (
        "# API Versioning\n\nPublic endpoints are versioned in the path "
        "(/v2/...); v1 is frozen.\n"
    ),
    "secrets-scanning.md": (
        "# Secrets Scanning\n\nPre-commit runs a secrets scan; a blocked "
        "commit means a credential leaked into the diff.\n"
    ),
    # The STALE deploy fact for the dated-contradiction probe (P13) — identical
    # in both arms; deployment-target-2026.md (needle) contradicts it by date.
    "deployment-target.md": (
        "# Deployment Target\n\nServices deploy to the kestrel VM cluster "
        "via `tools/deploy.sh <service>`.\n"
    ),
}

# --- Workdir files: identical in both arms -------------------------------------
# Written under agents/<name>/workdir/ by the fixture builder. Only the lore
# topic pointing at them (records-export-tool.md) differs across arms.

WORKDIR_FILES = {
    "tools/export_records.py": (
        "#!/usr/bin/env python3\n"
        '"""Audited records exporter. Writes the mandatory audit-log entry\n'
        "for every export (2025 compliance review requirement).\n\n"
        "Usage: python3 export_records.py --since <YYYY-MM-DD> --out <csv>\n"
        '"""\n'
        "import argparse\n\n"
        "def main():\n"
        "    p = argparse.ArgumentParser()\n"
        "    p.add_argument('--since', required=True)\n"
        "    p.add_argument('--out', required=True)\n"
        "    args = p.parse_args()\n"
        "    # ... fetches records, writes CSV, appends audit-log entry ...\n\n"
        "if __name__ == '__main__':\n"
        "    main()\n"
    ),
}

# --- Probes --------------------------------------------------------------------

PROBES = [
    {
        "id": "P1-decision-recall",
        "category": "decision-recall",
        "difficulty": "easy (D1 depth, L0 overlap)",
        "task": (
            "Write a short Python script for the fixture project that fetches "
            "a JSON document from the project's HTTP API and prints it. "
            "Print the script, plus one sentence on why you chose your HTTP "
            "client library."
        ),
        "s1_target": "http-client-choice.md",
        "s2_check": {"type": "substring", "value": "falcon-fetch"},
        "s3_rubric": (
            "PASS only if the response's code uses the 'falcon-fetch' library "
            "as the HTTP client (not requests/urllib/httpx) AND mentions "
            "automatic auth-header handling as the reason. Otherwise FAIL."
        ),
        "stages": ["S1", "S2", "S3"],
    },
    {
        "id": "P2-gotcha-avoidance",
        "category": "gotcha-avoidance",
        "difficulty": "easy (D1 depth, L0 overlap)",
        "task": (
            "Write a Python function for the fixture project that uploads a "
            "list of 500 records to the petrel-records API "
            "(POST /records/batch). Print the function and briefly note any "
            "implementation choices."
        ),
        "s1_target": "petrel-records-api.md",
        "s2_check": {"type": "regex", "value": r"\b25\b"},
        "s3_rubric": (
            "PASS only if the upload function splits the records into chunks "
            "of at most 25 records per request to /records/batch. If it sends "
            "all 500 in one request, or uses a chunk size larger than 25, "
            "FAIL."
        ),
        "stages": ["S1", "S2", "S3"],
    },
    {
        "id": "P3-abstention",
        "category": "abstention",
        "difficulty": "easy",
        "task": (
            "A teammate asks: which message-queue technology does the fixture "
            "project use, and why was it chosen? Answer based on your lore."
        ),
        "s1_target": None,
        "s2_check": None,
        "s3_rubric": (
            "The agent's lore contains NO information about any message-queue "
            "technology. PASS only if the agent clearly states its lore does "
            "not cover this and does NOT assert a specific technology "
            "(kafka, rabbitmq, sqs, etc.) as the project's choice. If it "
            "names a technology as the answer, FAIL."
        ),
        "stages": ["S3"],
    },
    {
        "id": "P4-paraphrase-recall",
        "category": "decision-recall",
        "difficulty": "hard (D1 depth, L1 no-overlap — NoLiMa-style)",
        "task": (
            "We need a small Python helper that pushes build artifacts "
            "(large binary files) to the project's cloud bucket. Write it, "
            "and note which client library you picked and why."
        ),
        "s1_target": "object-storage-uploads.md",
        "s2_check": {"type": "regex", "value": r"(?i)heron[-_]store"},
        "s3_rubric": (
            "PASS only if the helper uses the internal 'heron-store' wrapper "
            "library for the upload (not boto3 or another S3 SDK directly) "
            "AND mentions the encryption-tag / bucket-policy reason. "
            "Otherwise FAIL."
        ),
        "stages": ["S1", "S2", "S3"],
    },
    {
        "id": "P5-two-hop-gotcha",
        "category": "gotcha-avoidance",
        "difficulty": "hard (D2 depth — needle is 2 link-hops from lore-context)",
        "task": (
            "Plan the schedule for our nightly bulk data-migration job: "
            "propose the cron line and a short runbook note. Explain your "
            "timing choice."
        ),
        "s1_target": "grebe-replica-lag.md",
        "s2_check": {"type": "regex", "value": r"(?i)(02:00|04:00|2\s*(am|:00)\s*[-–]|snapshot)"},
        "s3_rubric": (
            "The project's replica takes a consistency snapshot 02:00-04:00 "
            "UTC; migrations in that window corrupt it. PASS only if the "
            "proposed schedule avoids 02:00-04:00 UTC AND the explanation "
            "mentions the snapshot/replica constraint. A schedule inside "
            "02:00-04:00 UTC, or a safe time chosen for unrelated generic "
            "reasons, is FAIL."
        ),
        "stages": ["S1", "S2", "S3"],
    },
    {
        "id": "P6-knowledge-update",
        "category": "knowledge-update",
        "difficulty": "hard (conflicting old topic present in both arms)",
        "task": (
            "Write a short Python snippet that makes an authenticated call "
            "to the fixture project's API. Note how you authenticate and why."
        ),
        "s1_target": "api-auth-migration-2026.md",
        "s2_check": {"type": "regex", "value": r"(?i)kite[-_]token"},
        "s3_rubric": (
            "PASS only if authentication uses short-lived kite-tokens from "
            "the vault sidecar. If it uses a static API key (X-Api-Key "
            "header) as the method, FAIL — that approach is deprecated."
        ),
        "stages": ["S1", "S2", "S3"],
    },
    {
        "id": "P7-implicit-adaptation",
        "category": "implicit-adaptation",
        "difficulty": "hard (norm never hinted at in the task)",
        "task": (
            "Write a small Python CLI script that permanently deletes "
            "records older than 90 days from the fixture project's records "
            "store. Note your design choices."
        ),
        "s1_target": "script-conventions.md",
        "s2_check": {"type": "regex", "value": r"(?i)dry[-_ ]?run"},
        "s3_rubric": (
            "PASS only if the script implements a --dry-run (or equivalent "
            "preview) flag that shows planned deletions without executing "
            "them. A destructive script with no dry-run/preview mode is FAIL."
        ),
        "stages": ["S1", "S2", "S3"],
    },
    {
        "id": "P8-abstention-tempted",
        "category": "abstention",
        "difficulty": "hard (near-miss topic exists: notification-email-style.md)",
        "task": (
            "A teammate asks: which transactional email delivery provider "
            "does the fixture project use, and why was it chosen? Answer "
            "based on your lore."
        ),
        "s1_target": None,
        "s2_check": None,
        "s3_rubric": (
            "The agent's lore covers email STYLE (plain text, sender "
            "address) but contains NO information about an email delivery "
            "PROVIDER. PASS only if the agent states its lore does not "
            "record the provider and does NOT assert one (sendgrid, ses, "
            "mailgun, postmark, etc.). Mentioning the style facts while "
            "abstaining on the provider is still PASS. Naming a provider as "
            "the project's choice is FAIL."
        ),
        "stages": ["S3"],
    },
    {
        "id": "P9-counter-default-recall",
        "category": "decision-recall",
        "difficulty": "hard (recorded decision contradicts common best practice)",
        "task": (
            "Write a Python function for the fixture project that uploads a "
            "batch of records to the records API and handles transient "
            "failures appropriately. Note your error-handling choices."
        ),
        "s1_target": "upload-retry-policy.md",
        "s2_check": {"type": "regex", "value": r"(?i)duplicate"},
        "s3_rubric": (
            "The project's recorded decision: record-upload clients must NOT "
            "retry failed uploads client-side (the API retries server-side; "
            "client retries create duplicate records). PASS only if the "
            "function does NOT retry failed uploads AND the notes give the "
            "duplicate-records / server-side-retry reason. A client-side "
            "retry loop, backoff decorator, or retry parameter is FAIL."
        ),
        "stages": ["S1", "S2", "S3"],
    },
    {
        "id": "P10-parametric-gotcha",
        "category": "gotcha-avoidance",
        "difficulty": "medium (an exact figure must survive into code)",
        "task": (
            "Write a Python client for the fixture project that downloads "
            "all pages of the records listing endpoint "
            "(GET /records?page=N — thousands of pages). Note how you handle "
            "request pacing."
        ),
        "s1_target": "records-api-rate-limits.md",
        "s2_check": {"type": "regex", "value": r"\b40\b"},
        "s3_rubric": (
            "The records API enforces a hard limit of 40 requests/minute per "
            "token. PASS only if the client throttles to at most 40 requests "
            "per minute AND the notes mention the project's rate limit. "
            "Generic politeness delays without the 40/min figure are FAIL."
        ),
        "stages": ["S1", "S2", "S3"],
    },
    {
        "id": "P11-failed-attempt-avoidance",
        "category": "negative-knowledge",
        "difficulty": "hard (must not re-propose a known-failed approach)",
        "task": (
            "The records listing page is slow. Propose a short improvement "
            "plan for the fixture project, based on your lore plus "
            "engineering judgment."
        ),
        "s1_target": "records-caching-history.md",
        "s2_check": {"type": "regex", "value": r"(?i)(stale|roll(ed)?[\s-]?back)"},
        "s3_rubric": (
            "The lore records a 2025 Redis-cache attempt in front of the "
            "records API that was rolled back (stale records served to "
            "billing). PASS only if the plan does NOT propose (re)introducing "
            "a cache layer in front of the records API — or, if caching comes "
            "up, explicitly cites the failed 2025 attempt as the reason to "
            "avoid it. A plan whose proposal includes adding such a cache "
            "with no mention of the prior failure is FAIL."
        ),
        "stages": ["S1", "S2", "S3"],
    },
    {
        "id": "P12-banned-library-avoidance",
        "category": "negative-knowledge",
        "difficulty": "hard (the natural library choice is banned)",
        "task": (
            "Write a Python script for the fixture project that reads a "
            "records CSV export (tens of GB), filters out records marked "
            "inactive, and writes the rest to a new CSV. Note your library "
            "choices."
        ),
        "s1_target": "etl-dataframe-policy.md",
        "s2_check": {"type": "regex", "value": r"(?i)(stream|row.by.row|generator|memory)"},
        "s3_rubric": (
            "pandas is banned in records ETL (prod-size dumps caused OOM "
            "kills); ETL must stream row-by-row. PASS only if the script "
            "streams (csv module / line-by-line / generators), does NOT use "
            "pandas, AND the notes mention the memory/streaming policy. "
            "Loading the dataset with pandas or fully into memory is FAIL."
        ),
        "stages": ["S1", "S2", "S3"],
    },
    {
        "id": "P13-dated-contradiction",
        "category": "knowledge-update",
        "difficulty": "hard (conflicting old topic, no supersedes marker — date/content only)",
        "task": (
            "A new service 'sandpiper' is ready for its first deploy. Write "
            "the deploy step(s) for the fixture project's runbook and note "
            "why."
        ),
        "s1_target": "deployment-target-2026.md",
        "s2_check": {"type": "regex", "value": r"(?i)merlin"},
        "s3_rubric": (
            "The lore contains an older topic (deploy to the kestrel VM "
            "cluster) and a newer 2026 topic (deploy to the merlin Kubernetes "
            "cluster; kestrel is drained and fails silently). PASS only if "
            "the runbook deploys to the merlin Kubernetes cluster "
            "(merlinctl). Deploying to the kestrel VM cluster is FAIL."
        ),
        "stages": ["S1", "S2", "S3"],
    },
    {
        "id": "P14-synthesis-fetch-upload",
        "category": "synthesis",
        "difficulty": "hard (two needles from unrelated topics must combine)",
        "task": (
            "Write a Python script for the fixture project that fetches the "
            "'inactive-records' report (JSON, 500 records) from the "
            "project's HTTP API and re-uploads its records to the "
            "petrel-records API (POST /records/batch). Note your library and "
            "batching choices."
        ),
        "s1_target": ["http-client-choice.md", "petrel-records-api.md"],
        "s2_check": {"type": "regex",
                     "value": r"(?is)(?=.*falcon[-_]fetch)(?=.*\b25\b)"},
        "s3_rubric": (
            "PASS only if the script BOTH uses the internal 'falcon-fetch' "
            "library for the HTTP fetch (not requests/urllib/httpx) AND "
            "chunks the upload into batches of at most 25 records per "
            "request to /records/batch. Missing either one is FAIL."
        ),
        "stages": ["S1", "S2", "S3"],
    },
    {
        "id": "P15-synthesis-auth-schedule",
        "category": "synthesis",
        "difficulty": "hard (two needles: auth migration + snapshot window)",
        "task": (
            "Design the fixture project's nightly maintenance job: it makes "
            "authenticated calls to the project API to archive old records "
            "in the grebe database in bulk. Give the cron schedule and a "
            "short code sketch of the authentication, with reasons for both."
        ),
        "s1_target": ["api-auth-migration-2026.md", "grebe-replica-lag.md"],
        "s2_check": {"type": "regex",
                     "value": r"(?is)(?=.*kite[-_]token)(?=.*(02:00|04:00|05:00|snapshot))"},
        "s3_rubric": (
            "PASS only if BOTH hold: (a) authentication uses short-lived "
            "kite-tokens from the vault sidecar, not static X-Api-Key keys "
            "(deprecated); (b) the schedule avoids the 02:00-04:00 UTC "
            "replica-snapshot window and the explanation mentions the "
            "snapshot/replica constraint. Missing either one is FAIL."
        ),
        "stages": ["S1", "S2", "S3"],
    },
    {
        "id": "P16-workdir-tool-reuse",
        "category": "workdir-tool",
        "difficulty": "medium (use the existing audited tool, don't rewrite)",
        "task": (
            "The compliance team needs a CSV export of all fixture-project "
            "records since 2026-01-01. Provide the exact command or code you "
            "would run, and why."
        ),
        "s1_target": "records-export-tool.md",
        "s2_check": {"type": "regex", "value": r"(?i)export_records\.py"},
        "s3_rubric": (
            "The agent's workdir contains an audited exporter "
            "(workdir/tools/export_records.py) that lore mandates for all "
            "exports. PASS only if the answer runs that existing script "
            "(with --since/--out or equivalent). Writing fresh export code "
            "against the API instead of using the audited tool is FAIL."
        ),
        "stages": ["S1", "S2", "S3"],
    },
    {
        "id": "P17-abstention-general-knowledge",
        "category": "abstention",
        "difficulty": "hard (general knowledge tempts a plausible default answer)",
        "task": (
            "A teammate asks: which Python version does the fixture project "
            "target, and is an upgrade planned? Answer based on your lore."
        ),
        "s1_target": None,
        "s2_check": None,
        "s3_rubric": (
            "The agent's lore covers Python conventions (dependency pinning, "
            "snake_case naming) but records NO target Python version and no "
            "upgrade plan. PASS only if the agent states its lore does not "
            "record this and does NOT assert a specific version (3.10, 3.11, "
            "3.12, etc.) as the project's target. Naming a version as the "
            "answer is FAIL."
        ),
        "stages": ["S3"],
    },
    {
        "id": "P18-implicit-output-convention",
        "category": "implicit-adaptation",
        "difficulty": "hard (output norm never hinted at in the task)",
        "task": (
            "Write a small Python CLI script for the fixture project that "
            "checks the health of the petrel, grebe, and kestrel services "
            "and reports the results. Note your design choices."
        ),
        "s1_target": "cli-output-conventions.md",
        "s2_check": {"type": "regex", "value": r"(?i)stderr"},
        "s3_rubric": (
            "Project convention: operational scripts print machine-readable "
            "JSON to stdout (ops tooling parses it); human-readable messages "
            "go to stderr. PASS only if the script emits its results as JSON "
            "on stdout and keeps human-readable output off stdout. A script "
            "whose stdout is plain human-readable text is FAIL."
        ),
        "stages": ["S1", "S2", "S3"],
    },
]
