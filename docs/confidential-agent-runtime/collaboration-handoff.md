# Native agent integration collaboration handoff

Status: PROPOSED DIVISION OF DUTIES, 2026-10-26. The project owner approved phased delivery and local tickets. The M1 orchestrator design passed independent review. This document proposes the shared boundary for the Claude integration maintainer; it does not claim their agreement or upstream acceptance.

## Read this first

We are extending the existing Sandbox Orchestration Harness so it can own compute running an autonomous native agent without a Temporal Worker or Namespace credentials inside that compute. We will then compose native Claude execution with that lifecycle. The first contribution is useful independently of Claude.

The native SDK and CLI keep the agent loop. The harness keeps one compute lifecycle owner. We are not asking the Claude integration to restore a removed Sandbox abstraction or take over provider orchestration. Confidential execution later places the native SDK, content callbacks and content policy inside the approved runtime; an ordinary outside Workflow that reads tool arguments does not meet that boundary unchanged.

## Proposed ownership

| Area | Proposed lead | Boundary |
|---|---|---|
| Native Claude SDK integration, Transport parity, CLI protocol behavior and upstream samples | Claude integration maintainer | Retain ordinary SDK behavior and its upstream extension points. No generic compute lifecycle ownership is required here. |
| External runtime mode, capability checks, provider identity/adoption and compute cleanup | This project's harness contribution | Extend the existing Go harness and existing provider seams. Keep legacy mode unchanged and one existing lifecycle controller. |
| Early demo adapter and skill placement | Joint interface agreement; project prepares composition | Agree exact revision, launch/attach binding, readiness, package availability and shutdown contract. Do not assign new maintainer implementation work by assumption. |
| Accepted session/workspace recovery and effect uncertainty | This project's recovery composition, with native capability input | Qualify actual native behavior and reuse upstream support where it fits. M1 does not settle the recovery algorithm. |
| Attestation, independent keys, content release and deployment qualification | This project's deployment/security adapters | Later AWS profile and actual job policy; not generic Claude plugin acceptance criteria. |

Implementation of the M1 contribution lands in the [Sandbox Orchestration Harness](https://github.com/temporal-community/sandbox-orchestration-harness). This repository owns the project specification and local backlog. Native integration changes belong in the integration's own upstream contribution. Pin dependencies when composing; do not merge the full draft fork into this project as a prerequisite for M1. The Go lifecycle owner and Python runtime need an explicit binding for M2; no Python harness SDK or Nexus service is assumed.

## Interface to settle together

1. **Create or attach:** the harness owns provisioning and returns a resource binding. A Transport or supervisor uses that binding without creating a second sandbox. Confirm the existing four Activity seam can attach to externally owned compute for the ordinary interoperability option.
2. **Readiness:** distinguish provider machine readiness from a usable native CLI/supervisor. Agree a bounded runtime readiness check before the first native request.
3. **Close and delete:** distinguish connection close, CLI shutdown and compute deletion. Only the lifecycle owner decides compute removal. An attachment cannot delete another owner's workspace.
4. **Skill files:** select image packaging or an explicit delivery path. Prove the selected package and supporting files exist in a clean runtime; a source host path is insufficient. Do not assume automatic cross host transfer from the local plugin example.
5. **Dependencies and content:** agree exact integration/SDK/CLI pins. Label an ordinary trusted interoperability demo separately from the later sealed content profile. Do not route private tool content through an outside Worker to claim confidential execution.

These are joint checks, not an allegation that the generic integration must implement this project's full security or recovery requirements.

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

Current inspected integration head: [PR #169](https://github.com/temporalio/ai-integrations/pull/169), `32969f3ffa7688cb1cde250f1245e4ed70eb53d6`. Current inspected sample head: [PR #403](https://github.com/temporalio/samples-python/pull/403), `347cff1a1efce1afdc6ead9eaf2d565a29be99ad`. Harness baseline: `24f09129335f8057750f09f84a45b9c76c99d9c1`. Recheck implementation deltas before building against a newer revision. Source roles and immutable links are in the [ticket evidence](ticket-evidence.md).

This handoff is prepared for review. No message or PR comment has been sent on the project owner's behalf.
