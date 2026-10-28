# Confidential native agent runtime specification

## Source pin

Brownfield: this design extends the existing application source. A separate host Git observation resolved the origin repository `https://github.com/mortdiggiddy/ai-integrations` at commit `cad28f3e6024ccd992df44cba4306a74ff50140a` with uncommitted documentation and diagram changes. The packaged analyzer reported `source_snapshot.kind=non_git`, `git_revision=null`, content fingerprint `sha256:e157cfb4e532a0ef95f09ccba860da608ec42fb7237dd43f11c5aabf6606636f` and identity `sha256:e5b61eb6ed214782c768bba34fc245132634cbff3012a3381d9be534d6ae213f`; it supplied no Git or dirty tree fingerprint. The host Git commit above is separate corroboration, not a mapper Git pin. Its aggregate status was failed because inventory encountered 22 archived escaping symlink fixtures. The finalized Python result covered 25 selected maintained source/test files with 552 assertions; three computed queue/registration targets remain unresolved and fidelity is not qualified. EV-1 preserves that usable static lower bound and the 556 source region hash rechecks, not a successful full repository map or complete runtime topology.

The runtime source, tests, manifests and lock were unchanged at that commit during supplemental inspection. The retained lock resolves Claude Agent SDK 0.2.154 and Temporal 1.33.0. The current external candidate is upstream PR #169 at `32969f3ffa7688cb1cde250f1245e4ed70eb53d6`, read at EV-22 and EV-23; it locks SDK 0.2.163 and Temporal 1.34.0 and declares SDK >=0.2.163,<0.2.166. That is a separate candidate, not an adopted dependency or branch. EV-9 retains earlier source findings at their historical pins. Status: authored through the formal specification workflow for independent review, not runtime qualification.

## Objective

Run native Claude skills inside an approved content boundary while outside Temporal orchestration manages durable job state and one compute lifecycle without seeing confidential content.

## Background

The retained plugin is a different execution model: `ClaudeAgentPlugin` registers a generated segment Activity, `DurableClaudeAgent` schedules plaintext segment inputs and separate tool Activities, and a sample Worker obtains its queue from configuration. `SdkSessionControl` supplies local SDK lifecycle experience. These inspected paths are compatibility evidence, not an existing sealed supervisor or a complete production deployment map (EV-2 through EV-6, EV-21).

The extension must preserve the legacy plugin mode and tests while adding an opt in application boundary. Existing `SegmentInput`, tool outcomes and agent state must not be reused unchanged on outside Workers because they carry confidential prompts, tools and results. The current user facing requirement is one project home and a native runtime composition, not a replacement agent loop. The complete historical obligation map remains at EV-8.

The current upstream candidate uses four `TransportActivities` operations: launch, write stdin, watch output and stop. Its default subprocess runs with the Worker's user, environment and files; the documented Activities must reach that same host. The SDK and callbacks still execute in Workflow code. Custom Activities can change CLI placement, but do not move their SDK caller into the protected runtime. There is no longer an integration Sandbox interface, and the older launch/replacement findings in EV-9 must not be presented as current defects (EV-22).

## Goals

- Preserve native skill loading and the admitted SDK/CLI behavior on exact qualified versions.
- Keep confidential code, prompts, results and policy processing inside the approved runtime, with sealed operations and approved metadata outside.
- Keep Namespace credentials and Temporal Worker polling out of the external runtime.
- Establish one compute owner and coherent accepted native session/workspace recovery, including replacement without original host or disk access.
- Prevent uncertain external effects from becoming blind retries, while retaining unresolved exact call and independent authority obligations.
- Produce bounded acceptance evidence for one useful prototype before expanding providers, native feature breadth or a second harness.

## Non-goals

The initial prototype does not implement another Claude loop, mandatory Mods replay, universal provider streaming, a new Python harness SDK, mandatory Nexus, confidential inference, or arbitrary production mutations. It does not make a container demonstration equivalent to operator confidentiality. Optional ordinary remote SDK interoperability is not a prerequisite for the inside SDK/CLI route.

The final requirements below remain in scope even when an early milestone proves only an explicitly bounded subset. No historical acceptance result transfers automatically to the new composition.

## Scenarios

1. A caller starts a job with sealed input and immutable package/policy identities. Outside orchestration admits only the selected metadata and operations. The controller creates one runtime, whose supervisor validates input and runs the native SDK/CLI locally.
2. An outside Worker or output observer fails while the agent remains alive. Recovery attaches to the same runtime generation and does not allocate or restart the agent.
3. A create or launch reply is lost. The controller reconciles the original operation identity before another create or launch; uncertainty is not proof of nonexecution.
4. The original host and disk are unavailable. A replacement validates and restores one accepted native session/workspace state. Missing, corrupt, stale or mismatched accepted state stops recovery.
5. A controlled mutation may have completed before outcome acceptance. Affected continuation stops with its original identity retained. Neither a new tool ordinal nor native session restoration authorizes repeating the action.
6. A forged question answer, stale generation, wrong image or unauthorized key request is rejected. Only the permitted question/output contract releases content to a recipient.
7. A long session reaches a supported handoff boundary. Accepted references, identities and unresolved state survive the selected rollover policy; unsupported rollover remains refused until qualified.

These scenarios become the existing AC cases, not new claims that the implementation already behaves this way.

## Rigor tier

`spec-first`. This specification guides a bounded prototype and its first independent verification. Security, effect and state ownership decisions have high switching costs and therefore receive detailed requirements and explicit owner gates. Automated synchronization between future implementation and the specification is not claimed. Reconsider an anchored specification when a maintained runtime and service owner exist.

## Authority and scope

This is the sole active specification for the replacement architecture. The decision register owns the detailed choices and approval records. The compact owner table below mirrors their current Open status and blocking gates. The historical recovery tree is archived evidence; its source bytes and historical statuses remain unchanged.

The project owner confirmed staged delivery. The immediate design and build scope is M1: native process placement through provider configuration and existing Sandbox Orchestration Harness lifecycle interfaces, with only demonstrated missing validation. This follows the maintainer clarification supplied by the operator on 2026-10-27 and supersedes the earlier separate mode/start interface mechanism. The plan and BD-07 own that revised mechanism and its pending review. M2 adds a local native runtime, M3 qualifies recovery, and M4 activates the trusted AWS deployment and its security policies. Review each stage against its own outcome and prerequisites. A PASS for M1 is not a full future runtime PASS; unresolved M3/M4 mechanisms do not block the independent M1 contribution or disappear from this specification.

BD-01, BD-02 and BD-03 carry forward exact pending call recovery, selected protected dispatch authority and strict preventive spending. They are not reopened waiver questions. The approved synthetic local configuration also carries forward within its scope. Native mechanism designs, final deployment/disclosure choices and runtime acceptance remain pending; the decision register separates them.

## Requirements

Each CR identifier is stable. A prototype may prove a subset, but it cannot advertise the final confidential profile until all applicable requirements and blocking decisions are satisfied.

| ID | Required behavior | Acceptance owner |
|---|---|---|
| CR-01 | Preserve native skill execution through the SDK and CLI. Pin SDK, CLI, image, package and policy identities; qualify admitted skills and features on those exact versions. Make the admitted package and required supporting files available inside the runtime before launch, verify their identity, and refuse missing or mismatched packages. Package delivery must preserve CR-04's access boundary; a Worker local plugin path does not establish remote placement. | AC-01, AC-11 |
| CR-02 | Keep confidential prompts, code, tool arguments, results and content policy processing inside the approved runtime. Outside components handle sealed content and approved metadata only. | AC-02 |
| CR-03 | Run no Temporal Worker and store no Namespace credential inside external runtime compute. Use the restricted authenticated service boundary for orchestration. | AC-02, AC-03 |
| CR-04 | Enforce the party specific access policy for client code, protected skills and released artifacts. Neither party may decrypt protected combined material alone; release only explicitly permitted outputs. | AC-02, AC-10; BD-05, BD-06 |
| CR-05 | Gate final confidential activation on approved runtime identity, key release, administration restrictions and scope. Distinguish protection from the operator, cloud provider and model provider. | AC-10; BD-05 |
| CR-06 | Keep one compute owner and one active native input consumer per runtime generation. Reconcile an unknown allocation or launch result before another create or launch. Reconnect must not allocate. | AC-03, AC-04 |
| CR-07 | Bind every permitted operation to authenticated principal, job, generation and operation identity. Reject stale producers and cross job reads or mutations before acceptance. Content encryption alone is not authorization. | AC-04; BD-07 |
| CR-08 | Restore one selected accepted state binding native session files, workspace, required sidecars, package and policy identities, and required pending outcomes or model projections. Upload and verify required bytes before accepting their references. Independent latest pointers, stdout delivery and telemetry are not recovery authority. | AC-05, AC-06; BD-01, BD-04 |
| CR-09 | Restore from the accepted state on every runtime start, including same host restart. Prove replacement with original host and disk unavailable. Missing or corrupt accepted state must stop, not become an empty new session. Preserve the no loss objective for accepted state. | AC-05, AC-06 |
| CR-10 | Classify an action as not run, definitively completed, or uncertain using evidence. An uncertain external mutation must stop affected continuation until an authorized supported disposition; it must not automatically repeat or acquire a new identity. | AC-07; BD-01, BD-02 |
| CR-11 | Isolate untrusted generated commands from supervisor keys, credentials, policy files, recovery authority and control sockets. Enforce filesystem, process and egress boundaries; a permission callback or shared VM alone is insufficient. | AC-08 |
| CR-12 | Enforce fixed tool policy inside the content boundary for confidential mode. Permit questions and output release only through the selected content disclosure and authentication contract. Policy, environment and plugin overrides must not bypass it. | AC-08, AC-09; BD-06 |
| CR-13 | Apply the content policy to logs, failures, traces, metrics, UI views and stream subscribers. Use opaque identifiers and approved bounded metadata. Outside codecs cannot undo prior plaintext exposure in an outside Worker [EV-14]. | AC-02, AC-09 |
| CR-14 | Bound Workflow history, payloads, messages and carried state. Specify a safe Continue-As-New boundary, preserve accepted identities and unresolved state across handoff, and qualify reset and version transitions. Do not carry the full transcript in Workflow input. | AC-09, AC-11; BD-09 |
| CR-15 | Declare provider capabilities for requested placement, persistence and idle policy. Reject unsupported combinations before allocation. Initial autonomous runtime examples disable command based idle suspension unless runtime aware behavior is independently supported. | AC-03 |
| CR-16 | Define stop, terminal observation, replacement, cleanup, orphan reconciliation and retention ownership. Preserve required state and keys across live, stopped and unresolved recovery windows; uncertainty never authorizes destructive cleanup. | AC-04, AC-06, AC-11; BD-09 |
| CR-17 | Keep experiment execution separately authorized with finite request, time and spending allowances and retained accounting. Do not present monitoring as strict preventive enforcement. Preserve the earlier strict budgeting obligation pending an explicit decision. | AC-12; BD-03 |
| CR-18 | Keep each qualification claim bound to its actual revision, deployment and failure scenario. A fake provider, container, watcher retry or historical SDK proof cannot stand in for native, host loss or attestation proof. Preserve the broader second harness qualification obligation after primary runtime proof unless explicitly retired. | AC-01 through AC-12; BD-08 |

### Later stage implementation evidence

The [sandbox landscape review](evidence/sandbox-landscape-review.md) supplies supplemental implementation evidence at EV-33. It refines proof for CR-01, CR-07 through CR-13, CR-15 and CR-18 without selecting a new dependency or changing the reviewed M1 contract. Current vendor documentation and draft proposals remain candidate evidence, not project qualification.

Before implementing custom confinement controls in full M2/M4, compare the relevant native sandbox-runtime, nono and OpenShell components and record a bounded reuse or rejection decision under BD-07. Bind the selected enforcement profile to exact platform, backend, policy and version. Prove denied reads through native tools and child processes, unsafe environment/configuration inputs, inherited descriptors/control sockets, direct egress bypass and policy update semantics. Refuse permissive audit or policy override paths for admitted private jobs. The early trusted local skill demo remains a separate bounded M2 subset and does not wait for full confinement qualification.

For M3, portable RAM/disk checkpointing is an optional capture candidate under BD-01/BD-04/BD-08. A selection requires proof of accepted state, active-child behavior, compatible replacement without original host/disk, generation fencing, credential rebinding and external effect uncertainty. A successful VM restore alone cannot satisfy CR-08 through CR-10. Keep the candidate unselected until its scoped mechanism review; M1 still admits no restore or snapshot mode.

For M4, identify every component that can inspect protected plaintext, including credential brokers, TLS termination, diagnostics and checkpoint storage. Keep those components within the approved content/access boundary and qualify them under CR-04/CR-05/CR-13. Protecting a credential from the workload is not proof that content is protected from the host operator. Existing approval and deployment gates remain in force.

## Constitution

### INV-1 Failure model

Every Activity must have a finite Start-To-Close or Schedule-To-Close bound selected in its admitted profile. Retries and nonretryable classifications must be explicit for each operation; no implicit unlimited mutation retry is acceptable. Heartbeats provide progress and cancellation notification, not proof that a guest process has stopped. Product semantics are grounded at [EV-10](https://docs.temporal.io/develop/python/activities/timeouts) and [EV-12](https://docs.temporal.io/activity-definition#idempotency).

| Activity concern | Timeout and retry requirement | Failure and cancellation disposition |
|---|---|---|
| Allocate or reconcile compute | Finite attempt and total operation deadline; repeat only with receiver enforced stable identity and reconciliation | Unknown create/launch result keeps the original identity; stop if reconciliation cannot classify it |
| Send a sealed operation | Finite request deadline; deduplicate the original operation before a mutating retry | Timeout does not establish that the runtime did not accept or execute it |
| Observe runtime progress | Finite admitted lifetime and heartbeat timeout; retry may reconnect to the same generation and cursor | Cancellation closes the observer; it does not by itself kill compute or accept agent state |
| Capture, publish or restore | Finite deadline; retry immutable publication or exact reads only under the selected storage contract | Mismatch or missing accepted bytes stops; partial uploads do not advance accepted state |
| Stop and inspect | Finite bounded shutdown and inspection; reconcile the exact resource identity | Retain unresolved teardown; no replacement or destructive cleanup based only on an interrupt acknowledgment |

Assumption: A-78 and A-79 remain unproved; BD-04 and BD-07 must specify compatible native capture, operation schemas and bounded deadlines before dependent implementation, carrying forward the approved local profile. Stop and cleanup of allocated compute are lifecycle recovery, not compensation for an arbitrary external Bash mutation. Skill specific compensation is not supplied by this design. Unknown external effects retain BD-01/BD-02 and AC-07.

### INV-2 Worker and task queue topology

The current plugin registers a segment Activity on the Worker that installs it; sample queue names are caller configuration, not production defaults (EV-4, EV-21). The static map at EV-1 is a lower bound and does not establish dynamic registrations or a deployed fleet.

The proposed application separates job Workflow execution, lifecycle/provider I/O and restricted service operations as logical concerns. Deployment may co locate those concerns in a small prototype, but it must not place a Worker or Namespace credential inside agent compute. Exact queue names, registrations, concurrency and capacity belong to the BD-07 profile. Preserve existing plugin routing and use a separate opt in construction path for the new sealed models.

The initial change strategy preserves old code and immutable Worker/runtime build identities. Do not change command producing behavior for existing histories without the selected replay safe migration technique and AC-11 evidence. BD-09 must select production Worker deployment/versioning behavior and compatible state migration before that activation; no automatic upgrade guarantee is assumed.

Assumption: A-76, A-77 and A-87 require M1 source impact, registration and dependency qualification. The existing lock is not silently upgraded to the candidate upstream combination.

### INV-3 Workflow and activity modeling

Workflow code owns deterministic job transitions, the selected accepted reference, generation and approved metadata. Provider calls, model execution, filesystem/network I/O, nondeterministic key services and native processes run outside Workflow code. Use SDK deterministic time/identity facilities where needed; do not move the native SDK caller into the outside Workflow. [EV-11](https://docs.temporal.io/workflow-definition#deterministic-constraints) grounds the product boundary.

The SDK and CLI communicate locally inside the approved runtime. The outside application uses separate sealed request/result models; a codec on an outside Worker cannot undo plaintext exposure from the current segment models (EV-2 and EV-14). `SdkSessionControl` is a reuse reference, not a completed supervisor API (EV-3).

No new decorated Workflow, Activity name, gateway operation or schema is claimed to exist. BD-07 must fix the minimal service and lifecycle interfaces before code. A-75 and A-81 retire through the M2 native and confinement checks.

### INV-4 Long running behavior

Keep full transcripts, workspaces and raw output outside Workflow carried state. Carry the accepted encrypted reference, necessary identity/deduplication state and unresolved operations explicitly. Continue-As-New starts a new execution and requires deliberate state transfer; finish relevant handlers and resolve observer/child lifetime before handoff. [EV-13](https://docs.temporal.io/workflow-execution/continue-as-new) grounds the mechanism.

The current helper already drains handlers and carries its old `AgentState` (EV-6). That content bearing state and the existing handoff are not proof of the new external runtime contract. The Atlas conformance case at EV-18 demonstrates a bounded Update/Continue-As-New scenario and explicitly warns against using its blocking test synchronization in real Workflows.

Assumption: A-84 remains open. BD-09 carries forward the approved synthetic retention/reset horizon and must specify compatible state bounds, rollover conditions, child parent close policy and cleanup handoff. Before AC-11 qualifies rollover, the admitted prototype must remain within finite job/history bounds and must not advertise rollover support. No fixed event count, child survival policy or production retention duration is inferred from a sample.

### INV-5 State ownership and idempotency

The controller owns compute; the job's selected authority owns accepted references and generation; the runtime owns native execution and confidential content processing; the store holds immutable protected bytes. These are semantic responsibilities, not a requirement for three databases.

Activities can repeat after an external action completes but before reported completion. Idempotency and authoritative reconciliation belong at the receiver or effect boundary, not merely in the Activity attempt number. [EV-12](https://docs.temporal.io/activity-definition#idempotency) supports that failure model. Logical operation identities must remain stable across the supported retry and recovery horizon; a Run ID change cannot silently create permission to repeat an unresolved action.

Upload and validate required bytes before accepting the matching state reference. Unaccepted uploads, stdout delivery and diagnostic telemetry are not accepted recovery state. Capture must account for concurrent tools and background writers. A-78 through A-80 and BD-01/BD-02/BD-04 remain explicit qualification gates, not a claim that native continuation solves the transaction boundary.

### INV-6 Observability and service levels

Collect Worker/Client SDK metrics and, when Cloud is selected, the complementary Cloud metrics. Keep separate dashboards for their distinct observation points, with redacted logs and traces. [EV-16](https://docs.temporal.io/references/sdk-metrics) and [EV-17](https://docs.temporal.io/cloud/metrics/openmetrics) ground those sources. Native CLI telemetry remains inside the content policy and is never recovery authority.

| Correctness objective | Measurement | Alert or stop |
|---|---|---|
| Zero confidential canary leaks | Count exposures across outside payloads, failures, logs, traces and observers | Any exposure stops the profile |
| One owned runtime and native input consumer per admitted generation | Resource/consumer count by controlled test identity | Count above one blocks continuation and replacement |
| Every supported stale or cross job operation denied | Negative case pass count divided by submitted cases | Any unexpected acceptance blocks activation |
| Every accepted recovery fixture restores matching state | Accepted fixture success count divided by attempted cases | Any accepted state mismatch or loss blocks recovery activation |
| Zero repeated controlled uncertain mutations | Destination effect counters and retained original identity | Any repeat stops affected continuation |

These are measurable acceptance objectives, not measured availability or latency SLOs. Assumption: A-88 requires the workload envelope, timeout values, fleet capacity, production latency/availability targets and alerts to be selected under BD-07/BD-09 before M4 production activation. A local baseline cannot establish them by implication.

### INV-7 Security and privacy

Seal confidential content before it leaves the approved runtime or authorized input producer. Outside Workers handle ciphertext and approved metadata, with no content decryption key. A Payload Codec protects service storage but plaintext exists in executing Clients/Workers; failure attributes require explicit coverage, and Search Attributes remain readable. [EV-14](https://docs.temporal.io/production-deployment/data-encryption) and [EV-15](https://docs.temporal.io/search-attribute) ground those product constraints.

Bind operations to principal, job, generation and original operation identity. Validate input authentication and approved output release inside the content boundary where required. Neither permission callbacks nor an encrypted VM alone isolates generated commands from supervisor keys and control sockets. A-81 through A-83, BD-05 and BD-06 must qualify the selected arrangement.

Neither party may decrypt protected combined material alone. Approved image/key release, restricted administration, operator secrecy, cloud hypervisor protection and inference provider access are separate requirements and decisions. Plaintext provider snapshots are not an implicit confidential recovery mechanism. BD-09 carries forward the approved synthetic retention policy. Real client storage, key and Namespace retention require the client's policy; the synthetic values do not become production defaults. No malicious host rollback protection is silently adopted.

## Interfaces

The [runtime protocol](runtime-protocol.md) at EV-24 defines proposed operation identities, finite synthetic deadlines, receiver reconciliation, stopped capture, budget admission and handoff. The [native recovery protocol](native-recovery-protocol.md) at EV-25 defines proposed original-call deferral, independent dispatch, typed result projection and prelaunch restoration. These are new application contracts requiring independent review and implementation qualification. They are not upstream SDK APIs. Active child recovery remains an explicit native capability gap; a main-agent adapter does not fulfill it.

The inherited first trusted execution candidate is AWS EC2 NitroTPM with a mutually approved isolated Attestable AMI and KMS recipient encryption (EV-26). The initial scope trusts the cloud provider and protects against unauthorized operator and counterparty access. Google Confidential Space remains an alternative, not a selected replacement. Exact image, key release, runtime confinement and useful report policy still require qualification. See the [deployment baseline](evidence/upstream-alignment.md#trusted-execution-deployment-baseline).

The service operation names and schemas remain BD-07 design work. The minimum contract must distinguish sealed job input, approved status, runtime attach/reconnect, explicit stop, accepted state publication and selected restoration. Every mutating operation binds original identity and generation and has an honest acknowledgment meaning. Status observation does not grant execution or replacement authority.

The outside API must not expose arbitrary guest exec, arbitrary Workflow mutation or plaintext native protocol messages. Public keys, opaque resource references and permitted status are not confidential payload substitutes. Questions and reports use BD-06's recipient specific contract.

The retained plugin interfaces and tests remain compatible. New confidential operation types must not alias plaintext `SegmentInput`, `DeferredCall`, `ToolOutcome` or `AgentState` without an explicit trust/profile boundary. An ordinary remote SDK adapter, if later useful, attaches to existing lifecycle ownership and remains a separately qualified profile.

Native plugin loading and package delivery are separate responsibilities. The runtime supplies its verified local plugin path to the native SDK. The admitted provisioning path supplies the package, either in the approved image or through an authorized delivery mechanism. Do not infer transfer between hosts from `plugins` options or CLI internal caching. The [upstream skill evidence](evidence/upstream-alignment.md#skill-package-loading-and-file-placement) confirms a local skill loading test; remote package transfer and executable helper qualification remain unproved.

## Acceptance evidence

All acceptance is pending implementation. Preserve both negative controls and measured results. No acceptance row is closed by writing this specification.

| ID | Observable proof |
|---|---|
| AC-01 | One representative native skill loads through the pinned SDK/CLI and produces the expected bounded artifact. Record exact versions and admitted tools/features. On a clean runtime filesystem, verify the admitted package identity, native instruction loading and required supporting files without an undeclared shared mount or preinstalled copy. Test any admitted executable helper and its dependencies. Missing or mismatched packages must fail before job execution. Qualify the selected image or delivery path; do not require an additional transfer service when the approved image already contains the package. |
| AC-02 | Synthetic confidential canaries are absent from outside Worker arguments/results, history content, logs, failures, telemetry and observers. Process/configuration inspection shows no Worker or Namespace credential inside the runtime. |
| AC-03 | Existing provider defaults remain available; unsupported requested mode/policy causes zero allocations; one autonomous runtime starts and stops with the declared idle policy. |
| AC-04 | Concurrent create/launch, lost replies, reconnect, cancellation and stale generation attempts converge on one owned runtime and one input consumer; unauthorized and cross job operations are denied. |
| AC-05 | Destroy the original runtime and disable original host/disk access. Restore only declared durable state and compare native session identity, accepted conversation, files, sidecars and controlled effect counters with the accepted boundary. |
| AC-06 | Corrupt, remove, mismatch or substitute accepted recovery bytes and attempt cleanup during unresolved publication. Each case refuses unsafe restore or deletion and preserves a classified failure. |
| AC-07 | Interrupt a controlled mutation before execution, after execution and before outcome acceptance. Prove definitive classifications, preserve original identity and stop on uncertainty without another mutation or model continuation that bypasses it. |
| AC-08 | Attempts by generated commands to read keys, alter policy, use control sockets, escape allowed files or egress, or continue after failed policy enforcement are denied. Removing an essential guard makes a paired negative control fail. |
| AC-09 | Question/output forgery, replay, cross job access, unapproved telemetry content, oversized output and history pressure obey the selected contract without exposing protected content or losing accepted state. |
| AC-10 | On the selected final deployment, wrong image, wrong job, stale identity and unauthorized key release fail. Approved execution restores encrypted state and releases only permitted artifacts. Ordinary local containers cannot close this row. |
| AC-11 | Supported rollover, reset, stop, cleanup, retention and SDK/image upgrade cases preserve ownership, accepted identities and required bytes. Unsupported transitions refuse explicitly; replay fixtures remain version bound. |
| AC-12 | Each paid run has exact prior authorization, finite allowance and complete records. If strict preventive limits remain required, prove admission before every chargeable request and cumulative accounting rather than inferring it from post request monitoring. |

## Alternatives considered

| Alternative | Decision and reason |
|---|---|
| Native local SDK/CLI inside an approved runtime | Selected architecture direction; the supervisor and coherent recovery still require proof |
| Outside Workflow SDK using the current pluggable TransportActivities seam | Optional interoperability for a trusted Worker profile; its Worker subprocess default and custom CLI placement do not satisfy this content boundary by themselves |
| Rebuild the Claude loop or mandate Mods replay | Not the default route; retain useful old failure evidence without requiring a replacement engine |
| Use SessionStore or stdout offsets as full recovery authority | Insufficient alone for coherent files, acknowledged progress and external effects |
| Create a second compute controller beside the harness | Reject; one lifecycle owner is required |
| Move all old source/fixtures during this extension | Reject for this scope; preserve the legacy mode and archived evidence paths |
| Adopt an entire moving draft branch | Reject as an implicit dependency; use exact reviewed revisions and focused compatibility work |

## Open issues

Concrete remedies now exist at EV-24 and EV-25 for the previously unspecified operation, capture, budget admission and main-agent recovery protocols. They remain proposed until independent review; writing them does not close runtime acceptance. The unresolved active-child native resume mechanism and exact per-tool projection admission remain explicit. Do not replace those requirements with unsupported-case refusal and call the broader outcome complete.

Owner decisions below gate only their named behavior. A generic external placement/capability contribution can proceed under its bounded maintainer/profile agreement without resolving every confidential deployment detail. A narrow prototype does not close the final recovery or confidentiality requirements.

The static map's unresolved or partial relations remain disclosed at EV-1 and A-76. The first code scope must identify affected registrations and consumers without treating manual spot checks as complete topology. New research is limited to a concrete unresolved decision or failed acceptance condition.

## Decisions project owners must make

The detailed rationale and approval carryover remain in [decisions.md](decisions.md). This table is the formal blocking summary. Open means that a named engineering design, qualification or genuine owner subdecision remains; it does not reopen every carried forward approval. Source inspection cannot approve a change in product risk.

| ID | Decision | Why the design cannot assume it | Blocks | Status |
|---|---|---|---|---|
| BD-01 | How does native execution preserve exact original pending call and definitive result recovery? | The requirement is carried forward; native integration design and qualification remain pending. | M3 governed mutation recovery | Open |
| BD-02 | How does native execution enforce the selected protected independent dispatch authority? | The selected authority is carried forward; replacement needs a new decision. | M3 nonrepeatable effects | Open |
| BD-03 | How is strict preventive spending enforced, and what paid run authorization is granted separately? | Final prevention is carried forward; paid execution is a separate authorization. | M4 budget activation and every paid run | Open |
| BD-04 | How is coherent native session/workspace/sidecar capture implemented? | Storage/publication rules are carried forward; native capture design remains pending. | M3 capture and restoration | Open |
| BD-05 | Which exact image, KMS and administration bindings qualify the inherited AWS trusted execution profile? | Local configuration and AWS NitroTPM direction are retained; actual attested deployment remains unqualified. | M2 local security checks; M4 trusted activation | Open |
| BD-06 | How does the runtime enforce each job's approved recipient and release policy? | Authentication/read boundaries carry forward; business report schemas are job inputs rather than a new runtime product decision. | M2 release boundary; M4 admission of real job policies | Open |
| BD-07 | What compatible native service and attachment bindings implement the approved local profile? | The M1 additive proposal is specified in the plan; upstream acceptance and later native bindings remain separately gated. | M1 upstream acceptance; M2 supervisor; M3 takeover | Open |
| BD-08 | How are retained broader native features and second harness qualified after the finite prototype? | Requirements and phasing carry forward; broader claims await their proof. | M4 broader feature and second harness activation | Open |
| BD-09 | How is safe handoff implemented, and which uncertain Bash action is authorized? | Synthetic retention/reset safety carries forward; action and final production policy remain open. | M3 retained recovery window; M4 rollover and cleanup | Open |

## Assumptions and risks if wrong

A-01 through A-74 remain reserved by the historical source family at EV-8. This specification uses new identifiers rather than reusing them.

| ID | Assumption | Status | Risk if wrong | Severity | Reversible | Retire by | Owner |
|---|---|---|---|---|---|---|---|
| A-75 | The selected SDK and CLI can support the inside runtime supervisor without an outside plaintext SDK bridge. | untested | The confidential profile cannot execute the native skill as specified. | High | Partly | M2 native skill and sealed path proof; BD-07 | runtime owner |
| A-76 | The static map and supplemental traces cover the existing entry points relevant to the selected change. | untested | An unrecognized caller or registration can bypass the new mode or break compatibility. | High | Yes | M1 source impact and registration tests; map residual disposition | implementation owner |
| A-77 | The harness can add external placement and narrow capability preflight while preserving existing defaults. | proposed fix | Existing users receive different placement or unsupported requests allocate resources. | Medium | Yes | M1 compatibility and zero allocation tests; BD-07 | lifecycle owner |
| A-78 | Stable operation identity and reconciliation converge concurrent or uncertain launch requests on one input consumer. | proposed fix | Two runtimes or CLIs can mutate the same session or consume the same input. | High | Partly | M1 and M2 concurrency and lost reply cases; BD-07 | lifecycle owner |
| A-79 | The selected capture boundary can bind all required native and workspace state before accepted reference publication. | proposed fix | An acknowledged session restores mismatched or incomplete files or results. | High | No | M3 accepted state fault cases; BD-04 | recovery owner |
| A-80 | The selected native recovery and effect authority can meet the retained exact outcome and uncertainty obligations. | proposed fix | A completed external mutation repeats or a lost definitive result is invented. | High | No | M3 controlled mutation fault cases; BD-01 and BD-02 | project and runtime owners |
| A-81 | The supervisor, generated commands and service gateway can enforce the selected content and control boundary. | untested | Outside operators or generated commands access protected content, credentials or policy. | High | Partly | M2 confinement and canary cases; BD-05 and BD-06 | security owner |
| A-82 | The selected approved image and mutual key release paths can establish the final declared confidentiality profile. | untested | An unauthorized party or image receives keys or protected plaintext. | High | No | M4 wrong image/job/key and restoration cases; BD-05 | security and deployment owners |
| A-83 | The question, answer, output and telemetry contract can release only content permitted to the recipient. | open decision | A valid interaction leaks the other party's protected inputs. | High | No | M2 schema/authentication cases and M4 release proof; BD-06 | content policy owner |
| A-84 | Rollover, reset and retention can preserve accepted identities, unresolved outcomes, required bytes and keys. | open decision | A reset repeats an effect or cleanup makes an accepted session unrecoverable. | High | No | M3 retention and M4 reset/rollover/upgrade cases; BD-09 | recovery and lifecycle owners |
| A-85 | The inside gateway can enforce the retained request/token/currency authority using an admitted model and supplier charge contract. The first candidate reserves pessimistic bounds from EV-27/EV-28 rather than estimated token counts. | proposed fix | An unclassified feature, supplier contract violation or bypass exceeds admitted authority; model-only accounting is misrepresented as a whole-account bill cap. | High | No | M4 provider envelope compatibility, tariff and admission/accounting proof; BD-03 | budget owner |
| A-86 | The retained wider native features and second harness can meet the same selected trust and recovery contract. | open decision | A broader product claim is unsupported or a new tool path bypasses policy. | High | Partly | M4 selected positive feature and second harness cases; BD-08 | runtime and policy owners |
| A-87 | An explicitly selected dependency transition from the retained lock can preserve both legacy behavior and the new runtime contract. | untested | An API or protocol change breaks registered Workflows or native restoration. | High | Partly | M1 dependency qualification and M4 version transition cases; BD-07 and BD-09 | release owner |
| A-88 | The selected deployment workload, deadlines, fleet capacity and service targets can be monitored without content leakage. | open decision | The service stalls or exceeds capacity without a safe alert or support boundary. | Medium | Partly | M2 local baseline and M4 approved workload/SLO/alert/retention review; BD-07 and BD-09 | service owner |

## Authoritative location

`docs/confidential-agent-runtime/spec.md` is the active specification. The plan owns implementation sequence, the decision register owns owner approvals, the obligation map owns historical dispositions, and evidence files own observations. There is one active project package. Formal evidence consistency and independent design review do not qualify a runtime or close an AC row.

## Evidence

Full machine readable manifest: `evidence.json`, schema `evidence-manifest/v1`. Live documentation is mutable product corroboration; local source and map records bind the inspected baseline. Supplemental reads do not replace the map's coverage limits. No model, provider, attestation or recovery test ran during authoring.

| ID | Tool | Operation | Query | Result | Used for | Status |
|---|---|---|---|---|---|---|
| EV-1 | map-temporal-application | read finalized analyzer outcome and portable receipt | docs/confidential-agent-runtime/evidence/topology-receipt.json | docs/confidential-agent-runtime/evidence/topology-receipt.json | INV-2 INV-3 source pin and static topology residual | used |
| EV-2 | user-source | read retained source | python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_models.py:54-90 | python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_models.py:54 | INV-3 INV-7 existing plaintext segment models | used |
| EV-3 | user-source | read retained source | python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_session_control.py:86-119 | python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_session_control.py:86 | INV-1 local SDK lifecycle reference | used |
| EV-4 | user-source | read retained source | python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_plugin.py:29-43 | python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_plugin.py:29 | INV-2 generated segment Activity registration | used |
| EV-5 | user-source | read retained lock and package metadata | python/claude_agent_sdk/uv.lock and pyproject.toml | python/claude_agent_sdk/uv.lock | INV-2 dependency baseline; SDK 0.2.154 and Temporal 1.33.0 | used |
| EV-6 | user-source | read retained source | python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_workflow.py:447-490,577-597,766-776 | python/claude_agent_sdk/src/temporalio/claude_agent_sdk/_workflow.py:447 | INV-2 INV-3 INV-4 current helper, segment and tool scheduling | used |
| EV-7 | user-source | read owner decision register | docs/confidential-agent-runtime/decisions.md | docs/confidential-agent-runtime/decisions.md | INV-1 INV-5 INV-7 open owner decisions and bounded authority | used |
| EV-8 | user-source | read complete obligation map | docs/confidential-agent-runtime/obligation-map.json | docs/confidential-agent-runtime/obligation-map.json | INV-5 inherited obligations and historical acceptance limits | used |
| EV-9 | user-source | read consolidated research | docs/confidential-agent-runtime/evidence/research.md | docs/confidential-agent-runtime/evidence/research.md | INV-1 INV-5 INV-7 pinned native recovery and trust boundary research | used |
| EV-10 | temporal-docs | search_temporal_knowledge_sources | What do official Temporal Python documentation require for Activity timeouts, retries, heartbeats and cancellation, and why must external process termination be verified separately? | https://docs.temporal.io/develop/python/activities/timeouts | INV-1 Activity timeout, retry and heartbeat semantics | used |
| EV-11 | temporal-docs | search_temporal_knowledge_sources | What do official Temporal documentation require for deterministic Workflow code, explicit state transfer and unfinished handlers at Continue-As-New, and Activity idempotency? | https://docs.temporal.io/workflow-definition#deterministic-constraints | INV-3 deterministic Workflow behavior | used |
| EV-12 | temporal-docs | search_temporal_knowledge_sources | What do official Temporal documentation require for deterministic Workflow code, explicit state transfer and unfinished handlers at Continue-As-New, and Activity idempotency? | https://docs.temporal.io/activity-definition#idempotency | INV-1 INV-5 repeated execution after lost completion | used |
| EV-13 | temporal-docs | search_temporal_knowledge_sources | What do official Temporal documentation require for deterministic Workflow code, explicit state transfer and unfinished handlers at Continue-As-New, and Activity idempotency? | https://docs.temporal.io/workflow-execution/continue-as-new | INV-4 explicit application state transfer and handler completion | used |
| EV-14 | temporal-docs | search_temporal_knowledge_sources | What do official Temporal documentation say about payload codec placement, failure encoding and Search Attribute confidentiality, Worker Versioning, and SDK metrics versus Cloud metrics? | https://docs.temporal.io/production-deployment/data-encryption | INV-7 codec placement and failure attributes | used |
| EV-15 | temporal-docs | search_temporal_knowledge_sources | What do official Temporal documentation say about payload codec placement, failure encoding and Search Attribute confidentiality, Worker Versioning, and SDK metrics versus Cloud metrics? | https://docs.temporal.io/search-attribute | INV-7 readable visibility fields | used |
| EV-16 | temporal-docs | search_temporal_knowledge_sources | Which official Temporal documentation describe SDK worker metrics and Temporal Cloud metrics, and how should metrics distinguish Worker execution health from application service level objectives? | https://docs.temporal.io/references/sdk-metrics | INV-6 SDK observation surface | used |
| EV-17 | temporal-docs | search_temporal_knowledge_sources | Which official Temporal documentation describe SDK worker metrics and Temporal Cloud metrics, and how should metrics distinguish Worker execution health from application service level objectives? | https://docs.temporal.io/cloud/metrics/openmetrics | INV-6 complementary Cloud metrics | used |
| EV-18 | atlas | query then bounded source read | sdk-python continue_as_new all_handlers_finished execute_activity heartbeat worker registration; read features/features/continue_as_new/updates_do_not_block_continue_as_new/feature.py lines 1:110 | atlas://code/features/features/continue_as_new/updates_do_not_block_continue_as_new/feature.py | INV-4 bounded Update and Continue-As-New conformance precedent | used |
| EV-19 | temporal-developer | read installed Python SDK reference | references/python/python.md in installed plugin version 0.4.3 | https://github.com/temporalio/codex-temporal-plugin | INV-2 INV-3 Python registration and source organization guidance | used |
| EV-20 | user-source | read transition proposal | docs/confidential-agent-runtime/rebaseline-plan.md | docs/confidential-agent-runtime/rebaseline-plan.md | Objective, scope and authorized document transition | used |
| EV-21 | user-source | read provider sample entry point | python/claude_agent_sdk/tests/refund/worker.py:37-50 | python/claude_agent_sdk/tests/refund/worker.py:37 | INV-2 example queue is configuration, not a fixed production topology | used |
| EV-22 | user-source | read fetched current upstream source without checkout | git show 32969f3ffa7688cb1cde250f1245e4ed70eb53d6:python/claude_agent_sdk/README.md | https://github.com/temporalio/ai-integrations/blob/32969f3ffa7688cb1cde250f1245e4ed70eb53d6/python/claude_agent_sdk/README.md | Current optional TransportActivities seam, Worker subprocess default and trusted outside SDK topology | used |
| EV-23 | user-source | read fetched upstream dependency metadata | git show 32969f3ffa7688cb1cde250f1245e4ed70eb53d6:python/claude_agent_sdk/pyproject.toml | https://github.com/temporalio/ai-integrations/blob/32969f3ffa7688cb1cde250f1245e4ed70eb53d6/python/claude_agent_sdk/pyproject.toml | Candidate dependency transition SDK >=0.2.163,<0.2.166 and Temporal >=1.34.0,<2 | used |
| EV-24 | user-source | read proposed application protocol | docs/confidential-agent-runtime/runtime-protocol.md | docs/confidential-agent-runtime/runtime-protocol.md | Proposed sealed operations, stopped capture, strict admission and retained trust profile; not implementation proof | used |
| EV-25 | user-source | read proposed native recovery protocol | docs/confidential-agent-runtime/native-recovery-protocol.md | docs/confidential-agent-runtime/native-recovery-protocol.md | Proposed original pending identity, typed outcome projection and prelaunch recovery; active child capability gap retained | used |
| EV-26 | user-source | read AWS primary documentation | https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/nitrotpm-attestation.html | https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/nitrotpm-attestation.html | NitroTPM measured instance and KMS recipient encryption; not deployed qualification | used |
| EV-27 | user-source | read model contract | https://platform.claude.com/docs/en/models/haiku-4-5/overview | https://platform.claude.com/docs/en/models/haiku-4-5/overview | Candidate exact model identity and context/output bounds; mutable vendor contract revalidated at admission | used |
| EV-28 | user-source | read provider tariff | https://platform.claude.com/docs/en/about-claude/pricing | https://platform.claude.com/docs/en/about-claude/pricing | Candidate conservative per-attempt pricing envelope; not spending authorization or immutable tariff | used |
| EV-29 | user-source | read native subagent continuation | https://code.claude.com/docs/en/agent-sdk/subagents#resume-subagents | https://code.claude.com/docs/en/agent-sdk/subagents#resume-subagents | Parent session follow-up continuation is distinct from exact interrupted parent-call recovery | used |
| EV-30 | user-source | read pinned harness source | gh api repos/temporal-community/sandbox-orchestration-harness/contents/sdk/compute/provider.go?ref=24f09129335f8057750f09f84a45b9c76c99d9c1 | https://github.com/temporal-community/sandbox-orchestration-harness/blob/24f09129335f8057750f09f84a45b9c76c99d9c1/sdk/compute/provider.go | Existing Worker-oriented Start and StartFromSnapshot contracts; additive external mode avoids empty queue sentinel | used |
| EV-31 | user-source | read pinned harness source | gh api repos/temporal-community/sandbox-orchestration-harness/contents/sdk/workflow/activities.go?ref=24f09129335f8057750f09f84a45b9c76c99d9c1 | https://github.com/temporal-community/sandbox-orchestration-harness/blob/24f09129335f8057750f09f84a45b9c76c99d9c1/sdk/workflow/activities.go | Existing provider lookup and StartSandbox activity route; preallocation validation and compatibility impact | used |
| EV-32 | user-source | read pinned harness source | gh api repos/temporal-community/sandbox-orchestration-harness/contents/sdk/compute/smolcloud/provider.go?ref=24f09129335f8057750f09f84a45b9c76c99d9c1 | https://github.com/temporal-community/sandbox-orchestration-harness/blob/24f09129335f8057750f09f84a45b9c76c99d9c1/sdk/compute/smolcloud/provider.go | Existing stable creation/adoption path and TEMPORAL_TASK_QUEUE injection; first external provider extension | used |
| EV-33 | user-source | read supplemental sandbox primary sources and record phase implications | MXC policy validation; native sandbox-runtime; OpenShell supervisor; nono draft NEP-0007; SmolVM checkpoint and trust contracts | docs/confidential-agent-runtime/evidence/sandbox-landscape-review.md | Later stage component reuse decisions, confinement proof cases and optional portable capture evaluation; no M1 contract or dependency change | used |
