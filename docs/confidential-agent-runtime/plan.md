# Confidential native agent runtime plan

## Source pin

Brownfield: a separate host Git observation grounds the retained application source against the origin repository `https://github.com/mortdiggiddy/ai-integrations` at commit `cad28f3e6024ccd992df44cba4306a74ff50140a`, with uncommitted documentation and diagram changes. The packaged analyzer reported `source_snapshot.kind=non_git`, `git_revision=null`, content fingerprint `sha256:e157cfb4e532a0ef95f09ccba860da608ec42fb7237dd43f11c5aabf6606636f` and identity `sha256:e5b61eb6ed214782c768bba34fc245132634cbff3012a3381d9be534d6ae213f`; it supplied no Git or dirty tree fingerprint. The host Git commit above is separate corroboration, not a mapper Git pin. Its aggregate status was failed because inventory encountered 22 archived escaping symlink fixtures. The finalized Python result covered 25 selected maintained source/test files with 552 assertions; three computed queue/registration targets remain unresolved and fidelity is not qualified. EV-1 preserves that usable static lower bound and the 556 source region hash rechecks, not a successful full repository map or complete runtime topology.

The retained runtime source, tests, package metadata and lock were unchanged. The plan's current implementation evidence uses that same commit; candidate upstream integration and harness revisions in EV-9 are explicit external references, not the existing application baseline. Status: formal specification plan for independent review; no implementation or runtime acceptance is claimed.

## Stack

The current application is Python and retains the plugin package layout. Its lock resolves Claude Agent SDK 0.2.154 and Temporal 1.33.0 (EV-5). Current `ClaudeAgentPlugin` registers a segment Activity, and the application supplies concrete Workflows and queues. The sample Worker uses `args.task_queue` rather than a fixed production queue (EV-4, EV-21).

The proposed confidential composition uses the native SDK/CLI locally inside a supervisor, outside deterministic job orchestration and lifecycle/service Activities, and the existing Go Sandbox Orchestration Harness for compute ownership. It does not require a Python harness SDK or Nexus. BD-07 carries forward the approved local provider/ownership profile; compatible native service binding remains engineering design work.

The current PR #169 candidate at `32969f3ffa7688cb1cde250f1245e4ed70eb53d6` locks SDK 0.2.163 and Temporal 1.34.0, with the SDK manifest range >=0.2.163,<0.2.166 (EV-22, EV-23). Its `TransportActivities` seam and Worker subprocess default are separate from the retained local plugin. This candidate requires a dependency qualification decision. Do not update the existing lock, replace imported code or adopt a moving branch as a side effect of this specification. Preserve the current mode and tests while the new profile remains opt in.

## Architecture

### Existing source and change impact

| Confirmed source surface | Preserved behavior | Proposed extension impact |
|---|---|---|
| `_plugin.py` and generated `run_claude_segment` | Current Worker plugin registration and native segment execution | Add a separate application construction path; do not assume an external runtime controller already exists |
| `_workflow.py` helper and tool scheduling | Legacy segment and configurable tool Activity behavior | Outside job state must use sealed types and must not inherit content bearing old state unchanged |
| `_models.py` `SegmentInput` and outcomes | Existing plaintext fields remain valid only in their retained trusted Worker profile | Define separate sealed request/result models at the new boundary |
| `_session_control.py` | Local SDK connection, interruption and drain experience | Reuse or extract only after API and host ownership review; it is not already a sealed supervisor |
| Refund and session control tests | Retained implementation and version scoped evidence | Extend compatibility coverage without promoting old proofs to new recovery guarantees |
| Existing harness controller | Existing resource lifecycle and provider behavior | Add explicit external placement and requested capability validation without another controller |

EV-1 bounds topology coverage. Supplemental source reads at EV-2 through EV-6 and EV-21 establish these local paths; they do not complete dynamic topology or qualify the runtime. If a relevant caller is unresolved, M1 must trace it before changing its construction or payload path.

### Proposed responsibility boundaries

The outside job Workflow owns deterministic lifecycle intent, selected accepted references and approved metadata. Activities perform provider, storage and service I/O. The controller owns one compute resource and generation. The supervisor owns local native SDK lifecycle and protected content handling. The recovery adapter publishes and restores one selected state; the key adapter enforces the approved trust profile.

These component responsibilities are requirements, not claims that their proposed application modules exist. Exact file/package landing points for the new job application, sealed models, supervisor and adapters remain an implementation choice under BD-07. Keep them separate from the upstream plugin unless shared API evidence justifies a focused contribution.

No confidential content processor belongs on an outside Worker. A Codec does not change that placement rule. No observer retry, SDK disconnect or timeout is a physical teardown receipt. See [determinism](https://docs.temporal.io/workflow-definition#deterministic-constraints), [Activity idempotency](https://docs.temporal.io/activity-definition#idempotency), [Activity timeouts](https://docs.temporal.io/develop/python/activities/timeouts), and [codec placement](https://docs.temporal.io/production-deployment/data-encryption).

## Constraints

- Preserve CR-01 through CR-18, AC-01 through AC-12 and the complete obligation map. Carry forward historical approvals within their recorded scope; they do not constitute new runtime acceptance. Separate remaining owner choices from native engineering and qualification work in BD-01 through BD-09.
- Keep the existing dirty tree and archived source bytes intact. Do not switch branches, merge upstream, rewrite approvals or relocate fixtures as part of this authoring pass.
- Every new external operation needs admitted finite deadlines, retry classification, identity, authorization and an honest acknowledgment meaning. Unknown mutation outcomes stop instead of blindly retrying.
- Do not dispatch provider/network/filesystem/model work directly from Workflow code or reuse the old plaintext segment models on outside Workers.
- Keep full conversation/workspace data out of Workflow input and carried state. Qualify handler, observer and child lifetime before supported Continue-As-New. The current helper's handoff and the bounded Atlas conformance example are partial precedent, not a completed external runtime recipe.
- Do not advertise local container, watcher retry, ciphertext payload or provider capability flags as complete host recovery or mutual confidentiality.
- Paid execution needs its separately recorded authorization. No model call or allocation is authorized by this plan.
- Correctness counters and alerts are specified now. Production latency, availability, fleet, workload and retention values remain A-88 and BD-07/BD-09 gates, rather than invented defaults.
- Reuse native SDK behavior and the existing lifecycle controller. Ordinary remote SDK interoperability remains optional.

## Milestones

### M0: formal contract and dependency admission

Outcome: this specification and plan meet their evidence gates, receive independent design review, and expose every remaining issue as an owner decision or a milestone acceptance condition. This milestone does not require answering every final deployment question before the generic M1 contribution.

Prerequisites and blockers: use the concrete bounded M1 contract below under the existing endorsement of an additive external runtime contribution. Local implementation and a draft proposal do not need another blanket permission step; maintainer acceptance is required before upstream merge, and larger or breaking expansions require discussion first. Carry forward the approved later local provider/profile instead of requesting it again. BD-01 through BD-06, BD-08 and BD-09 retain downstream gates as classified in the decision register. Exact call recovery, protected Entity authority and strict budgeting remain required but do not block M1's generic placement contract.

Evidence: the source map/receipt and supplemental source reads bind the current implementation; both manifests and inline evidence tables agree; all A-75 through A-88 have a retirement check; the plan names all active BD decisions; the independent review exit test is met without a material core finding. Select any dependency transition explicitly and test both retained legacy mode and the proposed profile before adoption.

Activation: issue only the selected bounded implementation work through `write-tickets` after the applicable decisions are ready. Stop on an unresolved source impact, unapproved guarantee change or incompatible dependency assumption. No application source changes occur in M0.

### M1: explicit external runtime support

Outcome: the existing Sandbox Orchestration Harness can explicitly manage an autonomous runtime that is not a Temporal Worker. This is useful independently of Claude and confidential compute.

Prerequisites: the bounded additive contribution is already endorsed. Prepare its implementation and draft proposal in the harness repository against an explicit source revision. Maintainer acceptance is required before upstream merge; discuss larger or breaking changes first. No final confidential policy, native recovery adapter, attested image, paid inference path or live cloud test is a prerequisite for this phase.

#### Source contract and extension surface

At harness pin `24f09129335f8057750f09f84a45b9c76c99d9c1`, [compute.Provider](https://github.com/temporal-community/sandbox-orchestration-harness/blob/24f09129335f8057750f09f84a45b9c76c99d9c1/sdk/compute/provider.go) explicitly requires `Start(ctx, taskQueueName)` to bootstrap an in-resource Worker. [StartSandbox](https://github.com/temporal-community/sandbox-orchestration-harness/blob/24f09129335f8057750f09f84a45b9c76c99d9c1/sdk/workflow/activities.go) calls that method. Retain both unchanged for legacy execution. Do not use an empty task queue as a mode sentinel.

The existing [SDK ownership and options](https://github.com/temporal-community/sandbox-orchestration-harness/blob/24f09129335f8057750f09f84a45b9c76c99d9c1/sdk/sandbox.go) already distinguish owned and attached references. Its idle timeout is driven by command activity and defaults to five minutes; zero does not disable it. Reuse that lifecycle owner and explicitly request `NoIdleTimeout` for the first external profile. Add no controller.

The following names are concrete additive proposals for maintainer review, not existing upstream APIs or unresolved architecture choices:

```go
type ExecutionMode int
const (
    WorkerRuntime ExecutionMode = iota // zero value retains legacy behavior
    ExternalRuntime
)

type ExternalRuntimeStartRequest struct {
    SandboxID      string
    LaunchIdentity string
}

type ExternalRuntimeProvider interface {
    StartExternal(context.Context, ExternalRuntimeStartRequest) (*ProviderStatus, error)
}

type ProviderCapabilities struct {
    ExternalRuntime bool
    ExecuteCommand  bool
    Restore         bool
    Snapshot        bool
    SuspendResume   bool
    CommandIdle     bool
    RuntimeIdle     bool
}

type CapabilityProvider interface {
    Capabilities(context.Context, ExecutionMode) (ProviderCapabilities, error)
}
```

Keep `compute.Provider` unchanged; these optional interfaces live beside it. Add an opt in SDK option for `ExternalRuntime`. Omitted options and zero mode retain the Worker path, including existing Activity selection and legacy defaults. Unknown modes refuse. The external route requires both interfaces; it never falls back to `Start`, even if the task queue string is empty or a provider returns unsupported.

Capabilities describe the admitted provider configuration and requested mode, not an unconditional property of a provider brand. Unknown capabilities, lookup failure or requested false flags refuse before allocation. The first external profile permits fresh start, stop and the provider's declared ordinary command support; restore, snapshots and suspend/resume are disabled. Require explicit `NoIdleTimeout`; a default or command based idle timeout, runtime idle request, initial snapshot or restore request refuses in this profile even if a legacy provider supports it. Validate at SDK/controller entry and again in the receiving external Activity before calling the provider, so direct/retried inputs cannot bypass the policy. Legacy requests do not acquire a new capability prerequisite.

Persist the admitted mode, capability/profile version and normalized provider configuration in controller state. Apply that profile to every later command and lifecycle request, including attached references; attachment cannot reset the mode or gain capabilities. Disabled suspend, resume, snapshot and restore requests refuse before provider dispatch. Receiving external Activities validate the same mode/profile and resource binding independently of the SDK route. New external operation names/inputs retain this explicit context; omitted fields on historical legacy inputs retain their old interpretation. Include post-start, attachment and direct external Activity negative cases, not only creation preflight.

The controller supplies nonempty stable `SandboxID` and `LaunchIdentity` from retained lifecycle input before scheduling the external start Activity. Retries preserve both values and the provider/image/configuration binding. A receiver rejects missing identity and conflicting reuse. Do not generate a new resource identity per Activity attempt. Return the existing `ProviderStatus` resource identity and reuse the owning controller's stop/cleanup path; an attachment never becomes an owner.

#### First actual provider and example

Extend the existing [SmolCloud provider](https://github.com/temporal-community/sandbox-orchestration-harness/blob/24f09129335f8057750f09f84a45b9c76c99d9c1/sdk/compute/smolcloud/provider.go). Its current `Start` constructs a named machine, injects `TEMPORAL_TASK_QUEUE`, and uses `adopt` for create result handling. Factor shared creation without changing that legacy request. The external entry uses the stable external launch identity for the machine identity, omits queue injection and Worker/Namespace credential bootstrap, and reuses existing adoption and cleanup behavior. Keep provider credentials on the outside Activity Worker. Do not broaden this phase into a new distributed lifecycle framework or assert whole-host replacement safety from existing adoption behavior.

External naming uses its own domain/prefix and retained launch identity, distinct from legacy queue-derived names. Creation labels bind harness ownership, external mode, sandbox/launch identity and normalized nonsecret image/configuration digest. On conflict, adopt only an exact matching external resource with the expected network policy; mismatched mode/configuration or multiple matches refuse without modifying or deleting the conflicting resource. Preserve legacy naming and adoption behavior. The existing `startRecovered` automatically resumes a paused machine; the first external profile must instead refuse a paused or otherwise restoration-dependent resource, because suspend/resume is not admitted. Reuse helpers only where these mode-specific checks remain enforced. Required fake cases include a same-name legacy resource, changed image/configuration and an unexpectedly paused external resource.

This SmolCloud extension demonstrates the generic harness seam. It does not replace the approved Docker profile for M2 synthetic integration or the AWS direction for later attested execution. Other providers retain their legacy implementations and refuse external placement until explicitly extended.

Add one external example whose image entrypoint runs an ordinary harmless bounded native process. It requires no model credential, invokes no LLM and contains no Temporal Worker or Namespace credential inside the resource. An outside Worker hosts the existing sandbox Child Workflow lifecycle and stops the owned resource on the selected normal completion/cancellation path. Use `NoIdleTimeout`; do not present command completion as autonomous runtime idleness. Live SmolCloud execution is opt in and separately authorized, not a prerequisite for reviewing this contract or running fake-provider conformance.

#### Focused acceptance and compatibility

M1 covers CR-03, CR-06 and CR-15 and the applicable AC-03/AC-04 subset:

- Recording-provider tests prove omitted/zero mode calls legacy `Start` with the original queue, while explicit external mode calls `StartExternal` with the same retained identities across retries.
- A provider without the optional interfaces, an unknown/unsupported mode, and rejected snapshot/restore/suspend/idle combinations produce zero allocation calls. Exercise SDK/controller preflight and direct receiving Activity validation. External failure never calls legacy `Start` as fallback.
- SmolCloud request tests compare legacy provisioning behavior and verify external creation omits `TEMPORAL_TASK_QUEUE` and Worker/Namespace credential bootstrap. Cover stable naming, repeated identity, conflicting identity/configuration, adoption and cleanup without contacting the cloud API.
- A fake-provider example test proves one external resource owner, no Worker bootstrap in the resource, explicit stop/cleanup on normal completion and the existing cancellation path, and retained legacy examples. Record limitations of provider teardown observations rather than claiming stronger death proof.
- Preserve old serialized inputs and command histories. Use new external Activity names and additive optional fields omitted on legacy inputs; do not change commands for zero mode. Replay a retained legacy fixture and test fresh external histories. If implementation changes historical command selection, require a separate versioning/activation plan rather than accepting replay drift.

Implementation verification must inspect the changed registrations/callers, provider fake request records and legacy replay fixture. A source link or real-provider example alone cannot establish these checks. The actual provider example may later receive a separately authorized live check; do not call its unexecuted live path qualified.

Activation: external mode is explicit and limited to the admitted fresh-start profile. Stop on fallback to Worker bootstrap, unsupported allocation, identity conflict or replay incompatibility. Keep legacy mode as default and stop creating new external resources if the opt in path fails. Do not rewrite existing histories. Broader lifecycle reconciliation, restoration, native agent recovery and confidential execution remain separate phases.

### M2: native supervisor and sealed content path

Outcome: one controller owned runtime hosts the native SDK and CLI with local communication. Outside orchestration can exchange only the selected authorized operations, sealed content and approved metadata.

Prerequisites: the BD-05 local trusted profile is carried forward and the relevant BD-06/BD-07 disclosure and native interface contracts are explicit. Full attestation is not required to test the interface, but that local profile cannot claim operator confidentiality. The sealed operation schema, caller identity, job/generation binding and acknowledgment meanings must be explicit before code.

Impact: a small project runtime supervisor and one provider/service adapter. Keep application composition separate from the upstream plugin. No universal streaming framework, Nexus service, new harness SDK or ordinary remote SDK adapter is required.

Acceptance: CR-01 through CR-07 and CR-11 through CR-13 at local scope; applicable AC-01, AC-02, AC-04, AC-08 and AC-09. Use synthetic canaries and one representative native skill. Inspect outside Worker payloads, history, failures, logs, telemetry and observers. Verify the runtime has no Namespace credential. Reconnect must preserve resource identity; communication close must follow its ownership contract.

For AC-01, use a clean runtime and the selected package image or delivery path. Verify package identity, actual native skill instructions and supporting files; test admitted helpers and dependencies. Missing files and package mismatches must refuse job execution. The upstream local plugin sample is useful loading evidence, not proof of transfer into separate compute. Package provisioning must respect the confidential profile's key and access policy.

Activation: explicitly configured local integration profile, with synthetic data and no arbitrary production mutations. Stop on content exposure, cross job access, policy bypass or duplicate ownership. Disable the profile while correcting that boundary. Do not interpret a normal container as proof of restricted operator administration.

### M3: coherent replacement recovery

Outcome: a replacement runtime restores one accepted native session and workspace state without access to the original host or disk, under the selected progress and uncertainty contract.

Prerequisites: the native mechanism designs under BD-01, BD-02, BD-04 and BD-07/BD-09 are implementable for this proof, preserving approved authority, ownership and synthetic retention. Identify which exact SDK and CLI behavior is relied upon. Native SessionStore mirroring, stdout offsets and a surviving disk are not interchangeable with a proved accepted recovery boundary.

Impact: one recovery adapter, accepted state selection, workspace/session capture and restoration, generation takeover and controlled fault cases. Preserve native records and required sidecars. Choose a capture boundary that accounts for concurrent tools and background writers. Reject unsupported cases rather than relying on an arbitrary post tool copy.

Acceptance: CR-06 through CR-10 and CR-16 with AC-04 through AC-07 and the relevant AC-11 subset. Destroy the original runtime and disable original host/disk access. Compare native session identity, accepted conversation, workspace, sidecars and controlled effect counters. Inject lost replies, stale producers, corrupt or missing accepted bytes, and mutation before result acceptance. Preserve original action identity and stop on uncertainty. A watcher retry with a surviving CLI is a separate control case.

Activation: explicit recovery profile and supported workload. Stop when accepted data cannot be recovered, uncertain actions repeat, or stale generations affect current state. Retain evidence and the classified stopped state. Do not restore an empty session or rerun Bash to invent a lost definitive output. Roll back new starts to the previous supported profile while retaining keys and referenced state needed by existing runs.

### M4: confidential activation and bounded operational qualification

Outcome: one selected approved deployment meets the mutual confidentiality contract and the declared recovery guarantee.

Prerequisites: the retained BD-03 preventive budget contract is enforceable and actual final deployment, disclosure, action and production policy choices under BD-05, BD-06 and BD-09 are accepted, and M2/M3 evidence is valid for the chosen components. Carry forward the inherited cloud provider trust and AWS NitroTPM direction; qualify operator isolation rather than reopening a hardware confidentiality requirement. State the model provider plaintext boundary explicitly. The broader native feature and second harness obligations remain at BD-08 until explicitly accepted or retired.

Impact: one attestation/key release adapter, approved image policy, restricted administration, supervisor/command isolation, encrypted storage and restoration, output policy, telemetry, cleanup/retention and version transition qualification. Reuse existing product mechanisms where applicable; do not make a mode flag assert security it has not demonstrated.

Acceptance: all applicable CR and AC rows, including wrong image/job/stale identity key denial, confinement negative controls, permitted output release, protected restoration and retention across unresolved work. Retained strict preventive spending requirements need their actual admission proof. Qualify reset, Continue-As-New and SDK/image upgrades on supported boundaries rather than copying earlier results.

Activation: explicit final profile after evidence review. Stop on failed attestation or identity, unauthorized key release, content leakage, accepted state loss or unclassified effect replay. Keep the confidential profile disabled until corrected. Preserve old supported images and required key/state access for existing sessions under the selected rollback and retention contract.

### Broader service exit within M4

BD-08 still owns the retained positive child, parallel, context/artifact processing and second harness obligations. One admitted confidential profile does not prove those broader claims. Complete their selected cases before the corresponding broader service exit, or obtain explicit owner retirement. Do not silently defer a final requirement merely to call the product complete.

BD-07 and BD-09 also gate the admitted workload envelope, worker/queue capacities, finite operation values, measurable production service objectives, alerts, supported rollout/rollback behavior and retention. M2 records a local baseline; M4 must qualify the selected production profile. Keep old supported builds and required state/key access until no admitted recovery or replay path needs them.

## Assumptions retired by milestone

The specification owns the premises and risks. This table owns their proving sequence. No assumption is closed by authoring or by the presence of a source link.

| ID | Retired by milestone | Check that retires it | Gate |
|---|---|---|---|
| A-75 | M2 | Run one admitted native skill through the selected inside SDK/CLI supervisor and inspect sealed outside messages. | BD-07 |
| A-76 | M1 | Resolve the relevant map residuals and trace changed registrations, callers and bypass paths through source and compatibility tests. | BD-07 |
| A-77 | M1 | Prove retained defaults, explicit external mode and zero allocation for rejected requested combinations. | BD-07 |
| A-78 | M1 and M2 | Inject concurrent create/launch and lost replies; reconcile to one runtime and one native input consumer. | BD-07 |
| A-79 | M3 | Publish, lose, corrupt and mismatch session/workspace state around acceptance and prove the declared capture boundary. | BD-04 |
| A-80 | M3 | Inject controlled mutation before execution and after execution before outcome acceptance; prove no unclassified repeat or invented result. | BD-01 and BD-02 |
| A-81 | M2 | Use confidential canaries and command isolation negative cases against credentials, policy, files, egress and control sockets. | BD-05 and BD-06 |
| A-82 | M4 | Exercise wrong image/job/stale identity, unauthorized key release, permitted execution and protected restore on the selected deployment. | BD-05 |
| A-83 | M2 and M4 | Test forged, replayed and cross job questions/results and recipient specific output/telemetry release. | BD-06 |
| A-84 | M3 and M4 | Test supported rollover/reset/cleanup/retention/upgrade transitions while accepted and unresolved state remains required. | BD-09 |
| A-85 | M4 | Prove provider request admission and cumulative accounting under retained strict prevention; preserve separately authorized paid run records. | BD-03 |
| A-86 | M4 broader service exit | Qualify selected positive child/parallel/artifact and second harness cases; obtain explicit disposition of any scope change. | BD-08 |
| A-87 | M1 and M4 | Select exact SDK/CLI/Temporal/image versions, run legacy regression and new mode checks, then test supported upgrades. | BD-07 and BD-09 |
| A-88 | M2 baseline and M4 activation | Select the admitted workload and production targets, validate fleet/queue/deadline bounds, and prove matching content safe alerts. | BD-07 and BD-09 |

## Verification handoff

The latest explicit direction is staged delivery with a phase appropriate review of the Sandbox Orchestrator contribution first. The active next review scope is the complete M1 contract above, including its provider, compatibility and negative acceptance checks. Do not require M2/M3/M4 confidential policy, active-child resume, native result projection or final paid-provider proof to approve this generic external runtime design. Do not claim M1 PASS until fresh scoped review finds no material issue in that contract. Preserve prior full-design review ledger entries as historical.

The full roadmap and all retained CR/AC obligations remain visible. Future native capability gaps and final confidential choices are neither waived nor represented as solved by M1. Review their concrete protocols at EV-24/EV-25 when their dependent phase is selected. Document integrity alone is not a design PASS, and a scoped M1 result is not a whole-project PASS.

Hand the M1 contract and its actual harness source impact to `verify-design` for a fresh phase appropriate independent pass, then follow bounded convergence bookkeeping. Its exit test is an internally coherent additive placement contract with no material unresolved M1 mechanism or compatibility finding. Later phase choices remain explicit roadmap gates. The initial full CONDITIONAL result is not relabeled PASS. Concrete native authority/outcome and coherent capture designs remain required for their later phase.

For M1, verification inspects the actual harness provider/SDK/controller paths, optional interface compatibility, capability refusal, identity/adoption, ownership/cleanup and legacy replay. Later phase reviews additionally inspect native content models, accepted recovery, key/release policy and version compatibility. Proposed fixes are reviewed as claims rather than accepted solely because their diagnosis was correct.

| Decision | Blocks |
|---|---|
| BD-01 | M3 governed mutation recovery |
| BD-02 | M3 nonrepeatable effects |
| BD-03 | M4 budget activation and every paid run |
| BD-04 | M3 capture and restoration |
| BD-05 | M2 local security profile; M4 confidential activation |
| BD-06 | M2 interactive content path; M4 output release |
| BD-07 | M1 upstream acceptance; M2 supervisor; M3 takeover |
| BD-08 | M4 broader feature and second harness activation |
| BD-09 | M3 retained recovery window; M4 rollover and cleanup |

The convergence tool records actual passes below. The first row is the initial broader review; the second is the later phase appropriate M1 review. Their exit tests differ as stated above. Do not hand edit a passing row.

| Pass | Scope | Core findings | Remedy findings | Exit test met |
|---|---|---|---|---|
| 1 | full | 0 | 0 | yes |
| 2 | full | 0 | 0 | yes |

Tasks route to `write-tickets`, implementation to `execute-design`, and post implementation proof to `verify-change` with the required acceptance review. The existing DSR set remains archived. Create no new work item or estimate by copying the old phase graph; maintain traceability through the obligation map.

## Evidence

Full machine readable manifest: `plan-evidence.json`, schema `evidence-manifest/v1`. The specification and plan use the same inspected baseline and evidence set. Structural source integrity is not runtime acceptance, a complete topology proof, or owner approval. No application, model, provider or failure test ran in this authoring pass.

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
