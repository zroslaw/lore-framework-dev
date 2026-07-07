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
]
