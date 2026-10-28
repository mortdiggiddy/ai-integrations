# Native agent integration collaboration handoff

Status: OWNERSHIP SPLIT CONFIRMED, 2026-10-27. The operator supplied the integration maintainer's agreement: the harness owns host provisioning, attachment and deletion; the integration starts and stops Claude Code on that host. Skill files must already be on the CLI host, and their delivery belongs to the orchestrator. Exact adapter mechanisms and dependency admission still require review. This agreement does not constitute upstream acceptance of the harness PR or full M2 design approval.

## Read this first

We are extending the existing Sandbox Orchestration Harness so it can own compute running an autonomous native agent without a Temporal Worker or Namespace credentials inside that compute. We will then compose native Claude execution with that lifecycle. The first contribution is useful independently of Claude.

The native SDK and CLI keep the agent loop. The harness keeps one compute lifecycle owner. Following the harness maintainer's clarification supplied by the operator on 2026-10-27, M1 uses provider configuration and existing `Start`; the earlier separate runtime mode/start interface proposal is superseded. The combined draft now supplies verified CNR-2 compatibility and CNR-3 concrete provider admission. Their tickets own exact implementation evidence. CNR-4 native lifecycle policy, the generic demo and full M1 acceptance remain required. The confirmed host/process ownership split and later roadmap remain unchanged. We are not asking the Claude integration to restore a removed Sandbox abstraction or take over provider orchestration. Confidential execution later places the native SDK, content callbacks and content policy inside the approved runtime; an ordinary outside Workflow that reads tool arguments does not meet that boundary unchanged.

## Ownership and remaining proposals

| Area | Proposed lead | Boundary |
|---|---|---|
| Native Claude SDK integration, Connector/Transport behavior, CLI protocol behavior and upstream samples | Claude integration maintainer | Start and stop Claude Code on the host. Retain ordinary SDK behavior; do not acquire generic host lifecycle ownership. |
| Provider configuration, operation checks, identity/adoption and compute cleanup | This project's harness contribution | Use existing `Start` and lifecycle interfaces. Keep unchanged configurations compatible and one existing lifecycle controller. Add only demonstrated missing provider/configuration checks. |
| Host skill files and runtime secrets | This project's orchestrator composition | Prepare files on the CLI host before execution and supply secrets through the selected runtime mechanism. The integration does not transfer skill files. Do not put secrets in Activity inputs. Exact delivery and secret policy remain design choices. |
| Early demo adapter | Joint interface agreement; project prepares composition | Use the Connector extension point. Agree exact revision, launch/attach binding, readiness, package availability and shutdown contract. Do not assign new maintainer implementation work by assumption. |
| Accepted session/workspace recovery and effect uncertainty | This project's recovery composition, with native capability input | Qualify actual native behavior and reuse upstream support where it fits. M1 does not settle the recovery algorithm. |
| Attestation, independent keys, content release and deployment qualification | This project's deployment/security adapters | Later AWS profile and actual job policy; not generic Claude plugin acceptance criteria. |

Implementation of the M1 contribution lands in the [Sandbox Orchestration Harness](https://github.com/temporal-community/sandbox-orchestration-harness). This repository owns the project specification and local backlog. Native integration changes belong in the integration's own upstream contribution. Pin dependencies when composing; do not merge the full draft fork into this project as a prerequisite for M1. The Go lifecycle owner and Python runtime need an explicit binding for M2; no Python harness SDK or Nexus service is assumed.

## Interface to settle together

1. **Create or attach:** the harness owns provisioning and returns a resource binding. A custom `Connector` uses that binding without creating a second sandbox. At the inspected revision, `ClaudeAgentSDKPlugin(connector=...)` registers the existing five transport Activities; custom composition supplies `Connector.connect` and `ClaudeCodeProcess`, not replacement Activities. `ConnectActivityInput` has no dedicated harness resource field, so the cross language binding remains a reviewed adapter decision.
2. **Readiness:** distinguish provider machine readiness from a usable native CLI/supervisor. Agree a bounded runtime readiness check before the first native request.
3. **Close and delete:** distinguish connection close, CLI shutdown and compute deletion. Only the lifecycle owner decides compute removal. An attachment cannot delete another owner's workspace.
4. **Skill files and secrets:** the orchestrator prepares skill files on the CLI host. Select image packaging, mounts or an explicit delivery path and prove all scripts and references exist in a clean runtime. Secret values must not enter `ClaudeAgentOptions.env`, which becomes Activity input and Workflow history. Select the runtime secret mechanism separately; the ordinary sample is not confidential deployment proof.
5. **Dependencies and content:** agree exact integration/SDK/CLI pins. Label an ordinary trusted interoperability demo separately from the later sealed content profile. Do not route private tool content through an outside Worker to claim confidential execution.

These are joint checks, not an allegation that the generic integration must implement this project's full security or recovery requirements.

## Adapter declaration and verification

The project owner selects explicit protocol inheritance for the future Python adapter where supported: `class HarnessConnector(Connector)` with `async def connect(self, request: ConnectActivityInput) -> ClaudeCodeProcess`, and a concrete process adapter declared as `class HarnessClaudeProcess(ClaudeCodeProcess)`. Import both protocols from the qualified integration package; do not duplicate their declarations. This records implementation intent and does not authorize M2 code or dependency adoption.

The integration calls the supplied connector through `ClaudeAgentSDKPlugin(connector=...)`. Our connector must attach to the harness owned host and return the process adapter. That adapter implements `write`, `end_input`, `read` and `close`; closing stops Claude Code and its children without deleting the host. The harness retains host deletion authority. The exact resource binding and remote execution mechanism remain open.

The bounded demo must run its pinned type checker on the adapter and injection path, including negative probes for missing methods, incompatible arguments and incorrect awaited results. Explicit inheritance does not establish runtime validation or lifecycle correctness. The inspected upstream protocols are not decorated with `runtime_checkable`; do not use `isinstance(value, Connector)` or `isinstance(value, ClaudeCodeProcess)` as conformance proof. A runtime checkable protocol would check member presence rather than signatures. Retain separate tests for retries, overlapping calls, Worker loss, package availability and process shutdown.

## Fastest useful demonstration

| Delivery | Demonstration | Proof and honest limit |
|---|---|---|
| M1 harness example | An outside Worker starts a harmless external process, observes completion and cleans up; a second case cancels; an unsupported profile refuses before provisioning | Fake provider conformance and exact launch request inspection. No model call or live cloud qualification is needed for this first review. |
| Early M2 joint demo | A harness owned local Docker runtime starts native Claude and runs one representative skill with its supporting files | Prove actual native loading/helper execution, clean runtime package placement, readiness, reconnect identity and shutdown ownership. Use synthetic input and a local scripted model where compatible. A paid model demonstration needs separate authorization. This is a bounded M2 subset, not complete M2 or confidentiality acceptance. |
| M3 recovery demo | Destroy the original runtime and restore selected accepted native state onto a replacement | Original host/disk access is disabled; compare conversation/workspace and effect counters. Uncertain actions stop. This is not part of the first joint demo. |
| M4 confidential demo | The approved attested runtime receives keys and executes under the selected release policy | Wrong image/job/identity key denial and isolation tests support only the qualified AWS profile and declared trust scope. |

The early M2 demo must receive a small reviewed integration design and its own implementation tickets after the M1 seam exists. Do not wait for all M3/M4 mechanisms to show the ordinary native execution path, and do not describe that early demonstration as confidential or host loss recovery.

## Share only the useful files

Send this handoff first, followed by the [M1 ticket set](tickets/m1-external-runtime.md) and the [M1 plan section](plan.md#m1-explicit-external-runtime-support). The [backlog guide](tickets/README.md) explains sequence and later milestones. The [upstream alignment review](evidence/upstream-alignment.md) is optional detail for skill placement and the existing sample limits. The full [specification](spec.md) is background for later phases, not required reading to review the first contribution.

Current inspected integration head: [PR #169](https://github.com/temporalio/ai-integrations/pull/169), `348ba4ff358bd8e9a285860f682e62a72733b9b7`. Current inspected sample head: [PR #403](https://github.com/temporalio/samples-python/pull/403), `b0c0239d596355cadc97d205cb20fa957033b988`. These replace the earlier TransportActivities candidate for the next composition review; no dependency was adopted. Harness baseline: `24f09129335f8057750f09f84a45b9c76c99d9c1`; combined existing-start compatibility and concrete SmolCloud provider contribution: [draft PR #7](https://github.com/temporal-community/sandbox-orchestration-harness/pull/7), `2a6c1db1bdc2d16ae34da428ca8a8cfaed6b21a7`. The single commit matches the independently verified source. CNR-4 policy, the generic demo and complete M1 acceptance remain open; the live provider path is unqualified. Recheck implementation deltas before building against a newer revision. Earlier source roles and immutable links remain in the [ticket evidence](ticket-evidence.md).

The inspected [Connector contract](https://github.com/temporalio/ai-integrations/blob/348ba4ff358bd8e9a285860f682e62a72733b9b7/python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_types.py) returns a process held in the outside Worker, with later Activities routed to that Worker. Its [README](https://github.com/temporalio/ai-integrations/blob/348ba4ff358bd8e9a285860f682e62a72733b9b7/python/claude_agent_sdk/README.md#custom-connector) explicitly permits process close without deletion of orchestrator owned compute. The [custom sample connector](https://github.com/temporalio/samples-python/blob/b0c0239d596355cadc97d205cb20fa957033b988/claude_agent_sdk_plugin/custom_transport/connector.py) instead creates and deletes its own sandbox, so reuse its process transport pattern without transferring host ownership. The integration requires safe overlapping calls and stopping Claude Code when its owning Worker stops; the adapter must define and test that behavior. Session resume still needs surviving session files and does not prove replacement recovery. Callbacks and content still pass through ordinary Workflow code, so the Connector alone does not establish the later sealed content boundary. This is source inspection, not an executed interoperability test.

This handoff is prepared for review. Sharing it is separate from the approved upstream PR comments.

The later [sandbox landscape review](evidence/sandbox-landscape-review.md) supplies confinement and checkpoint candidates for this project's M2/M3/M4 work. It changes no M1 duty or first demo dependency and adds no requirement to the integration PR. Candidate selection remains subject to the existing trust and mechanism review gates.
