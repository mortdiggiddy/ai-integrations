# Docker Sandbox coding demo reference

Source review: 2026-11-17. This note records an example for the ordinary runtime and native skill demonstrations. It is reference evidence, not runtime qualification or a change to milestone acceptance criteria.

## Sources and review limits

- Repository: https://github.com/nrolls/docker-agentic-s3-demo
- Inspected revision: `8638f9b4e64dff231684b5717ff1dcffbaab731a`.
- [Demo instructions](https://github.com/nrolls/docker-agentic-s3-demo/blob/8638f9b4e64dff231684b5717ff1dcffbaab731a/README.md).
- [Runtime kit](https://github.com/nrolls/docker-agentic-s3-demo/blob/8638f9b4e64dff231684b5717ff1dcffbaab731a/kits/taskapp-tools/taskapp-tools.yaml) and [agent instructions](https://github.com/nrolls/docker-agentic-s3-demo/blob/8638f9b4e64dff231684b5717ff1dcffbaab731a/kits/taskapp-tools/taskapp-tools-context.md).
- Docker documentation: [isolation](https://docs.docker.com/ai/sandboxes/security/isolation/), [Git workflows](https://docs.docker.com/ai/sandboxes/workflows/git/), and [kits](https://docs.docker.com/ai/sandboxes/customize/use-kits/). Confirm these moving contracts before implementation.

The review covers source, tests, prompts and kit configuration. A supplied webinar screenshot provides supplemental observations below. No demo code, agent, sandbox, model call or cloud resource was executed during this review. Repository tests cover the task application, not sandbox isolation or recovery. Upstream source owns installation, commands and kit schema. This note records project relevance without duplicating those procedures.

## What the example does

The repository is a small Python task application used as a coding target. The agent adds features, runs tests and commits changes inside a Docker Sandbox. The repository name refers to Session 3, not Amazon S3 storage. It contains no Temporal orchestration.

- Clone mode exposes the source repository read only and gives the agent a private writable clone. A person fetches and reviews commits before accepting changes.
- The kit packages Ruff, team instructions and a requested allowance for the holiday API. Instructions guide behavior; enforced network policy controls access.
- The exercise starts with a denied API request. An authorized policy change permits a retry. Organization governance takes precedence over local requests.
- The sandbox Git remote is available while the sandbox runs. Retain required commits and artifacts outside that sandbox before deletion.

## Supplemental webinar observations

The screenshot shows four read only skill entries at `/home/agent/.claude/skills`, a resolved Claude image digest, kit assembly, a writable workspace and a read only source mount. This supports ordinary placement: prepare skills and helpers on the host that runs the CLI. It does not establish confidential package delivery.

Claude permission bypass is enabled. The boundary therefore depends on enforced runtime controls rather than interactive agent approval prompts. A kit policy listing reports no active entries, while an effective network check allows the holiday API under organization governance. Inspect effective policy when qualifying a job; a single policy source listing cannot establish the full access decision. These observations were not independently reproduced.

## Where Temporal fits

The proposed composition preserves the [collaboration handoff](../collaboration-handoff.md). Docker Sandbox is a runtime reference, not a replacement lifecycle controller or a selected new provider dependency.

| Owner | Responsibility in this composition |
|---|---|
| Existing harness controller and provider | Provision, attach to and delete compute; retain resource identity and apply supported lifecycle policy |
| Runtime preparation | Place admitted skills, helpers and configuration where the CLI runs |
| Native integration and Connector | Start, communicate with and stop Claude on the prepared host |
| Docker Sandbox | Enforce configured execution, workspace, network and credential boundaries |
| Temporal application | Retain job progress, coordinate waits and cancellation, collect results and request lifecycle actions through the existing owner |

A candidate scenario is: accept a task application change request, admit its runtime configuration, obtain compute through the harness, prepare the skill package, run Claude through the integration, retain the resulting commit or artifact, obtain required review, and release compute through the harness. The native agent keeps its execution loop. The Temporal Worker and Namespace credentials remain outside the runtime.

An API denial can become a durable wait if the application exposes that condition: an authorized administrator changes policy, then an application approval or Signal permits a retry. Temporal does not grant network access. Retried provisioning and process operations must reconcile with retained identities to avoid duplicate resources or effects. See [Temporal Activity idempotency](https://docs.temporal.io/activity-definition#idempotency).

## Reuse and milestone boundaries

- Use the task application as a candidate harmless workload for the generic demonstration and the kit as a packaging reference for the native skill demonstration. This note does not select a workload, add a kit framework or authorize live execution.
- Bind qualified runs to resolved image and skill package identities. A mutable image tag or kit file alone does not identify all executed content.
- Retain results before cleanup. Task data persistence and Git commits do not preserve the complete Claude session and workspace.
- M1 retains its placement, admission, lifecycle and compatibility criteria. This review closes none of them.
- M2 can reference ordinary skill placement and tooling. Read only skills remain readable by the host operator. Confidential composition still requires the selected content boundary.
- M3 requires coherent session and workspace recovery after original host loss, including uncertain external effects. Temporal history and same sandbox restarts do not establish that guarantee.
- M4 requires qualified attestation, isolation and key release. The ordinary sandbox controls do not establish mutual confidentiality or attested execution.

The demo explicitly permits reading a source `.env` file through its read only mount. Read only protects against modification, not disclosure. Preserve this distinction when presenting private code and proprietary skills together.

Before implementation, check the pinned example against current Docker and integration contracts. The [plan](../plan.md) and [local backlog](../tickets/README.md) own requirements and execution authority.
