# M1 external runtime delivery

### CNR-1 Deliver external runtime orchestration

Status: OPEN

- Type: Epic
- Priority: High
- Estimate: none
- Labels: none
- Parent: none
- Blocked by: CNR-6
- Blocks: CNR-10
- Related: none
- Owner role: Harness contribution owner
- Requirements: CR-03, CR-06, CR-15; applicable AC-03 and AC-04

#### Context

The [M1 plan](../plan.md#m1-explicit-external-runtime-support) uses the existing Go harness. The earlier mode/interface design review passed; the revised configuration based mechanism requires scoped review and implementation verification.

#### Problem

The maintainer confirmed that the existing provider interface supports compute without an inside Temporal Worker. Native process launch should use provider configuration and the existing lifecycle owner.

#### Scope

Deliver CNR-2 through CNR-6 as additive harness changes, one existing provider extension and a reproducible generic example.

#### Out of scope

Native Claude integration, recovery snapshots, suspend/resume, attestation, paid inference and live cloud qualification belong to later work or separately authorized checks.

#### Acceptance criteria

- [ ] CNR-2 through CNR-6 meet their criteria with resolvable evidence at the exact reviewed revision.
- [ ] The M1 review package contains the runnable example, legacy replay result, fake provider conformance results and independent implementation verdict.
- [ ] The proposed upstream contribution states the admitted fresh start profile and the remaining provider and security limits. Maintainer acceptance remains a separate merge gate.

#### Dependencies and blockers

CNR-6 owns M1 acceptance. No later confidential policy decision blocks this generic contribution.

#### Source evidence

[M1 contract and evidence mapping](../ticket-evidence.md#m1-evidence-and-acceptance-map); [M1 design review](../verification-report.md).

#### Open questions

Maintainers may request different additive API names. Record any material semantic change before implementation proceeds under a changed contract.

### CNR-2 Launch an explicit external runtime without changing legacy execution

Status: DONE (2026-10-27)

- Type: Feature
- Priority: High
- Estimate: 4 points (confidence 80 percent)
- Labels: Type: Feature, Topic: External runtime
- Parent: CNR-1
- Blocked by: none
- Blocks: CNR-3, CNR-4
- Related: none
- Owner role: Harness contribution owner
- Requirements: CR-03, CR-06, CR-15; applicable AC-03 and AC-04

#### Context

The harness uses `Provider.Start(ctx, taskQueueName)`. The maintainer clarified through the operator on 2026-10-27 that the Worker bootstrap comment is historical and provider configuration is the preferred way to select a host without a Worker. This replaces the earlier separate mode/start interface selection.

#### Problem

A configured native process must not receive unintended Worker bootstrap or change existing configurations. Retries must retain resource identity and configuration; old histories must retain their command selection.

#### Scope

Revise the launch contribution to use provider configuration and the existing start Activity and controller. Remove the separate mode/start interface requirement. Prove stable input, resource identity and legacy compatibility with recording fake providers and fresh histories. Provider admission belongs to CNR-3; initial and later lifecycle policy belongs to CNR-4. Keep earlier verification evidence as historical and run a fresh full verification pass for this revised scope.

#### Out of scope

Actual SmolCloud native configuration, allocation/adoption admission and configuration specific restore refusal are CNR-3. Initial idle/snapshot admission, later operations and attached references are CNR-4. This compatibility contribution does not claim those policies are enforced or the complete native process feature is ready. No new controller, Python harness SDK or Nexus service is required.

#### Acceptance criteria

- [x] Recording provider tests prove unchanged configurations use existing `Start` with the original queue, defaults and command selection. Retained legacy parent and controller histories replay without a nondeterminism error. Source: M1 plan and H1/H2/T2.
- [x] A native process configuration uses the same `Start` interface without requiring an inside Worker. A retry test proves identical stable start identity and configuration on both attempts; no second launch identity is required unless existing identity is insufficient. Source: M1 plan and T1.
- [x] Unknown providers and invalid configuration rejected by the configured provider constructor produce zero start/allocation calls through existing SDK/controller and direct receiving Activity routes. Valid unchanged configurations require no new optional interface or capability lookup. Do not add global rejection of unknown configuration keys. Source: M1 plan and H1/H2.
- [x] Tests show existing default and explicit `NoIdleTimeout` options and initial snapshot selection retain their original interpretation and routing. Fake native execution explicitly selects `NoIdleTimeout`. Native configuration specific idle/snapshot/restore admission remains required under CNR-3/CNR-4 and is not claimed by these compatibility tests. Source: M1 plan and H1/H2/T2.
- [x] Existing serialized inputs and registrations remain compatible. Fresh history and retained state show the selected provider configuration and stable resource identity through the existing start path. No parallel external Activity family is added merely for placement. Any historical command change requires a separate activation/versioning plan. Source: M1 plan and T2/G1.

#### Dependencies and blockers

Start against harness revision H0. Inspect the changed registration and caller paths before editing. Record the selected source revision and any relevant upstream delta in the contribution.

#### Source evidence

[M1 plan](../plan.md#m1-explicit-external-runtime-support); [H0, H1, H2, T1, T2 and G1](../ticket-evidence.md#inspected-sources).

**Current combined acceptance:** CNR-2 was verified again with CNR-3 and automatic local test CI at `28e521cc7b067c2902e38442386fd131ec6667a0`, against `24f09129335f8057750f09f84a45b9c76c99d9c1`, in [the same draft PR #7](https://github.com/temporal-community/sandbox-orchestration-harness/pull/7). The compatibility tests and retained fixtures remain; exact wire coverage includes four existing snapshot input/output records. The CNR-3 acceptance evidence below owns the combined result and limits.

**Prior compatibility-only implementation acceptance evidence:**

Verified and published revision: `9addcda9e6cf7dd03bb194dbec37c138e2a7ab82`, base `24f09129335f8057750f09f84a45b9c76c99d9c1`, [PR #7](https://github.com/temporal-community/sandbox-orchestration-harness/pull/7). The operator requested one combined commit. It replaces the two draft commits and has the identical tree `a8794c1d81313c2f89b8c4f32d247f6c6ddbb7b8` as independently verified source revision `028bd08d69ea592972d352908b06881215479c2c`. Canonical per commit verification passed again on the replacement. Upstream still matched the reviewed baseline before publication. The executable provider/SDK/controller paths match that baseline; only the provider contract comment changes in production source. The revised contribution removes the earlier separate mode/interfaces and Activity family. The committed tree matches source snapshot SHA256 `81974bdad209e2bc8707c66a1f278e37bfa656d222620ef4cac17b57c5863cab`, computed over the compact sorted path-to-SHA256 map of all 72 tracked files.

- Existing start and retry proof: `TestExistingStartRetriesPreserveProviderConfiguration` and `TestLocalNativeProcessHistory` run a bounded local process through a fake provider, retain queue/configuration across actual Activity attempts and observe one fake resource. No inside Worker polls the resource queue. [Conformance tests](https://github.com/temporal-community/sandbox-orchestration-harness/blob/9addcda9e6cf7dd03bb194dbec37c138e2a7ab82/sdk/provider_start_test.go) and [fresh history tests](https://github.com/temporal-community/sandbox-orchestration-harness/blob/9addcda9e6cf7dd03bb194dbec37c138e2a7ab82/sdk/provider_start_history_test.go).
- Refusal and compatibility proof: direct Activity and public SDK invalid provider/configuration matrices produce zero start/allocation calls; opaque provider fields remain valid. `TestExistingSandboxWireShapes`, `TestExistingSandboxRegistrationContract`, option forwarding and snapshot routing tests pass. Both retained legacy histories and four fresh parent/controller histories replay.
- Fresh independent contract, mutation and structural invariant reviews pass. The final matrix detects 42 distinct relevant faults, with no unresolved survivor. A default timer mutation exposed a test gap; corrected assertions now reject both the six minute timer and any timer under `NoIdleTimeout`. Unrelated controls preserve all 695 materialized wire bytes. Six focused compiler probes reject broken interface/record contracts with intended diagnostics.
- Lead rerun and canonical per commit verification pass on the exact revision: 33 top level tests and 53 passing results including subtests, two expected skips for live cloud execution and fixture regeneration, vet, all 12 Makefile binary targets and the database example build. Focused race verification passes eight top level tests and 26 results including subtests, with no skips. Builds use the documented temporary replacement for the baseline's unavailable SDK pseudo version; tracked dependency files remain unchanged.

Local CNR-2 acceptance is complete. GitHub CodeQL and its Go analysis passed on source revision `028bd08d69ea592972d352908b06881215479c2c`, completed at 2026-10-28T00:00:35Z. Fresh CodeQL is running on the published combined commit; the earlier CI result does not qualify that revision. Maintainer acceptance remains separate. CNR-3/CNR-4 still own concrete provider admission and initial/later lifecycle policy. Full native process acceptance still needs both plus the demo. No cloud allocation, paid inference, recovery, attestation or confidential deployment was performed.

**Earlier implementation evidence, superseded mechanism:**

The maintainer's clarification and the operator's direction on 2026-10-27 replaced the mode/interface mechanism with provider configuration through existing `Start`. The ticket was reopened for that revision. The following evidence remains valid for the earlier implementation only; the completed revised acceptance is recorded above and does not transfer the earlier verdict.

The operator subsequently approved the minimal division on 2026-10-27: CNR-2 proves existing start and compatibility; CNR-3 owns concrete provider admission; CNR-4 owns initial and later lifecycle policy. Existing `Start` receives no controller idle option, so its direct calls validate the provider information they actually receive. CNR-4 must inspect actual idle/snapshot choices at controller initialization. Complete native process acceptance still requires CNR-3/CNR-4 and the CNR-5 demo; no guarantee is removed by this reassignment.

Implementation: `temporal-community/sandbox-orchestration-harness`, branch `external-runtime-launch`, commit `b9b5675810895efdaa030d4db7d67a4491bf0339`, base `24f09129335f8057750f09f84a45b9c76c99d9c1`. Upstream matched H0 before editing and before the PR attempt. The committed source matches reviewed snapshot SHA256 `90cd3e948bcf9a5ea9a622302856c7d5fc885c11fb4bd6088b8d2e50206be86c`, computed over the sorted path-to-SHA256 map for the 16 changed files using compact JSON.

Draft PR: https://github.com/temporal-community/sandbox-orchestration-harness/pull/7, published under the operator's later PR request after SAML SSO reauthorization. The published revision is the earlier implementation commit. Per commit verification passed, including the SDK suite, retained and fresh histories, vet and all example builds. At publication, GitHub CodeQL was running; this note does not assert its current result. Maintainer feedback now requires the configuration based revision. This documentation update does not change the PR or its code.

The five superseded criteria are retained here as the exact acceptance basis for that proof:

- Recording provider tests prove omitted and zero mode use legacy `Start` with the original queue and command selection. A retained legacy history replays without a nondeterminism error. Source: M1 plan and H1/H2/T2.
- An explicit external request reaches only the optional external start interface with nonempty, retained `SandboxID` and `LaunchIdentity`. A retry test shows identical identity and configuration on both attempts. Source: M1 plan and T1.
- Unsupported or unknown modes, absent optional interfaces, failed capability lookup and unsupported requested capabilities produce zero allocation calls. Tests cover both SDK/controller entry and direct receiving Activity input. Source: M1 plan and H1/H2.
- The first external profile requires explicit `NoIdleTimeout` and refuses snapshot, restore, suspend/resume and unsupported idle policies before dispatch. Tests prove external failure never falls back to legacy `Start`. Source: M1 plan and H1/H2.
- New external Activity names and explicit inputs preserve the old serialized input interpretation and registrations. Tests inspect retained controller mode/profile/configuration and fresh external history. Any historical command change requires a separate activation/versioning plan. Source: M1 plan and T2/G1.

- Legacy proof: `TestSDKPlacementSelection`, `TestLegacyStartKeepsQueueWithoutCapabilities`, `TestLegacyInputSerializationUnchanged` and `TestRetainedLegacyReplay` pass. The retained parent and controller histories were captured from unchanged H0 production source. Their fixture SHA256 values are `04af535e512909d0dc1ef31558d6461f05bba13615383f20145ea6333fc9a2a4` and `7cef88826f8dcfba7950d6d5bcaf9e74f59c41620fa94922d40c18acdab33d3e`.
- External proof: `TestFreshExternalHistory`, `TestControllerRetainsExternalAdmissionAndRetry` and the controller/direct Activity refusal matrices pass. Tests cover retained configuration, retry identity after a lost reply, each disabled initial policy, missing interfaces, failed capability lookup, no fallback and conflicting initialization. `TestAcceptedExternalHandlerInterleaving` also checks handlers without a second validator call.
- Independent `verify-change --mutation-sensitive` with structural invariants: PASS. Three isolated initial contexts reviewed the contract, mutation sensitivity and structural invariants. The final mutation matrix has 55 killed faults, two equivalent validator checks confirmed by a second reader and one passing unrelated provider control. No relevant survivor remains.
- Lead rerun: `GOWORK=off HARNESS_LOCAL_TEST=1 go test -json -count=1 ./...` passes 45 top level tests and 94 results including subtests, with two expected skips for live cloud testing and fixture regeneration. Vet, all 12 existing Makefile binary targets and the database example build pass. The existing example modules reference an unavailable SDK pseudo version; builds use a temporary workspace replacement to the local SDK, with tracked module files unchanged. The placement unit test retains an enabled ten second detector allowance for SDK binary checksum setup; production defaults and all acceptance assertions are unchanged.

Scope remains CNR-2. Actual provider provisioning/adoption is CNR-3. Later operation and attachment enforcement is CNR-4. The generic demo and complete M1 acceptance remain open. No live allocation, paid inference, recovery, attestation or confidential deployment was performed.

#### Open questions

Prove the existing contract and identify only demonstrated missing checks in scope. Concrete provider and lifecycle policy mechanisms remain owned by CNR-3/CNR-4 rather than added to this compatibility contribution.

### CNR-3 Provision an external SmolCloud runtime with stable ownership

Status: DONE (2026-10-27)

- Type: Feature
- Priority: High
- Estimate: 3 points (confidence 80 percent)
- Labels: Type: Feature, Topic: External runtime
- Parent: CNR-1
- Blocked by: CNR-2
- Blocks: CNR-5
- Related: none
- Owner role: Harness provider contribution owner
- Requirements: CR-03, CR-06, CR-15; applicable AC-03 and AC-04

#### Context

The existing SmolCloud provider uses queue derived names, Worker bootstrap environment and create/adopt helpers. Its recovered start can resume a paused machine.

#### Problem

External execution must not inherit Worker credentials or adopt a conflicting legacy, changed or restoration dependent resource.

#### Scope

Use the existing provider `Start` with the selected native process configuration. Reuse creation, adoption and cleanup where ownership, stable identity, configuration and network checks remain enforced. Add only the provider configuration changes required for that behavior. Keep unchanged configuration requests compatible.

#### Out of scope

Other provider implementations, a new reconciliation framework, snapshot recovery and live cloud qualification are excluded.

#### Acceptance criteria

- [x] Fake HTTP request tests show native process configuration uses existing `Start` and omits `TEMPORAL_TASK_QUEUE` and Worker/Namespace credential bootstrap. Missing, unknown or unsupported selected configuration and forbidden restoration refuse before allocation, including direct provider calls. Provider credentials remain on the outside Activity Worker. Unchanged configuration requests retain existing behavior. Source: M1 plan and H3.
- [x] Creation/adoption binds harness ownership, stable identity and selected nonsecret image/configuration. Tests inspect exact requests across retries and reject incompatible resources. Reuse existing naming and metadata where sufficient; a separate domain or identity field requires demonstrated need. Source: M1 plan and H3/T1.
- [x] A simulated lost create reply followed by a retry returns the original matching external resource. Same name legacy resources, changed image/configuration, wrong network policy and multiple matches are refused without modifying or deleting conflicting resources. Source: M1 plan and H3/T1.
- [x] An unexpectedly paused external resource refuses rather than using the legacy resume helper. Tests also prove owned creation failure cleanup and retained legacy adoption behavior. Source: M1 plan and H3.
- [x] All acceptance tests use a fake provider endpoint. The contribution labels the live example path as unqualified until a separately authorized live check runs. Source: M1 plan.

#### Dependencies and blockers

CNR-2 proves the existing start contract and stable retry inputs. This ticket supplies concrete configuration and provider admission; it cannot verify controller idle options absent from provider input. CNR-4 owns actual initialization/lifecycle options. Native feature acceptance waits for both and the demo.

#### Source evidence

[M1 provider contract](../plan.md#first-actual-provider-and-example); [H3 and T1](../ticket-evidence.md#inspected-sources).

**Current implementation acceptance (2026-10-28):** [Combined commit `28e521cc7b067c2902e38442386fd131ec6667a0`](https://github.com/temporal-community/sandbox-orchestration-harness/commit/28e521cc7b067c2902e38442386fd131ec6667a0), base `24f09129335f8057750f09f84a45b9c76c99d9c1`, retains one commit in [draft PR #7](https://github.com/temporal-community/sandbox-orchestration-harness/pull/7). Fresh full contract, mutation and activated structural invariant reviews pass. Mutation review found two disk validation test gaps; three new zero/negative/overflow assertions now detect both weakened guards. Final disposition: 147 of 152 Go/provider/public faults killed, three equivalent, one unreachable and one invalid mutation; eight additional CI guard faults killed, with no relevant survivor. Eleven compiler negative probes and exact baseline wire comparisons pass. The lead exact-commit rerun passes 111 results, with only live cloud and fixture capture skipped, plus vet and all example builds. Both retained histories and four fresh histories replay. [Hosted PR SDK tests](https://github.com/temporal-community/sandbox-orchestration-harness/actions/runs/40733050664), [push SDK tests](https://github.com/temporal-community/sandbox-orchestration-harness/actions/runs/40733041473), [CodeQL Go analysis](https://github.com/temporal-community/sandbox-orchestration-harness/actions/runs/40733043794/job/122974175082) and the CodeQL check pass on this revision. The GitHub hosted runner uses a local headless Temporal CLI server, fake HTTP and local subprocesses; no AWS resources or Docker are needed. Maintainer acceptance remains separate. CNR-4, the generic demo and full M1 acceptance remain open.

**Earlier implementation acceptance:** [Combined commit `2a6c1db1bdc2d16ae34da428ca8a8cfaed6b21a7`](https://github.com/temporal-community/sandbox-orchestration-harness/commit/2a6c1db1bdc2d16ae34da428ca8a8cfaed6b21a7), base `24f09129335f8057750f09f84a45b9c76c99d9c1`, in [existing draft PR #7](https://github.com/temporal-community/sandbox-orchestration-harness/pull/7). This includes CNR-2 compatibility and CNR-3 provider behavior in one commit. Maintainer acceptance remains separate.

- Configuration and request proof: `TestNativeProcessConfigurationAdmission`, `TestSmolCloudNativeDirectActivityAdmission` and `TestSmolCloudNativeExistingActivityRetry` exercise `workload=native-process` through existing interfaces. Native CPU/memory values must fit the API int32 wire domain; legacy and disk parsing retain their existing host integer domain. Requests contain no Worker/Namespace bootstrap or provider credential in guest data. Native restoration refuses before HTTP.
- Binding and retry proof: `TestNativeProcessRequestAndLostCreateReply` and `TestNativeProcessAdoptionRefusals` cover byte-identical retries, original resource adoption, exact name/ownership/configuration/network checks and untouched conflicts. The existing name and ownership label remain; one digest label binds the full queue and admitted nonsecret configuration. Exact digest assertions cover image/resources/allowlists and order-only equivalence.
- Failure proof: `TestNativeProcessOwnedCreateCleanup`, `TestNativeProcessCreateRequiresIdentity` and `TestNativeProcessPausedDuringReadiness` cover partial decode with a known ID, missing-ID refusal, owned failure cleanup and paused refusal at both adoption observations. Legacy adoption/resume tests pass. Cleanup observations prove the tested DELETE requests, not universal process death.
- Combined verification: fresh independent contract, mutation and activated structural invariant reviews pass. The final matrix detects 132 faults, with three independently confirmed equivalent guards and no unresolved relevant survivor. Eleven compiler probes reject invalid interface/record contracts. All eleven materialized public wire records exactly match compiled upstream output and fixed literals.
- Lead exact-commit checks pass: `GOWORK=off HARNESS_LOCAL_TEST=1 SMOL_CLOUD_LIVE=0 go test -json -count=1 ./...` executes 41 top level tests and 108 passing results including subtests, with only live cloud execution and fixture regeneration skipped. Both retained histories and four fresh histories replay. Vet, all twelve Makefile binary targets and the database build pass with the documented temporary local SDK replacement. Focused race detection passes 17 top level tests and 84 results, with no skips or race reports.

Local CNR-2/CNR-3 acceptance is complete. [CodeQL Go analysis](https://github.com/temporal-community/sandbox-orchestration-harness/actions/runs/40616745937/job/122580906082) and the CodeQL check pass for exact pushed revision `2a6c1db1bdc2d16ae34da428ca8a8cfaed6b21a7`, completed on 2026-10-28 UTC. CNR-4 actual initial idle/snapshot choices, later operations and attachments, the generic demo and full M1 acceptance remain OPEN. Live SmolCloud execution, account capacity, recovery, attestation and confidential deployment remain unqualified. No cloud allocation or paid inference occurred.

#### Open questions

If the actual provider API cannot enforce the selected ownership/configuration binding, record the limit and return to scoped design review. Do not weaken adoption checks to complete the example.

### CNR-4 Preserve external policy across commands and attached references

Status: OPEN

- Type: Feature
- Priority: High
- Estimate: 3 points (confidence 80 percent)
- Labels: Type: Feature, Topic: External runtime
- Parent: CNR-1
- Blocked by: CNR-2
- Blocks: CNR-5
- Related: none
- Owner role: Harness lifecycle contribution owner
- Requirements: CR-06, CR-15; applicable AC-03 and AC-04

#### Context

The existing SDK distinguishes owned and attached sandbox references. M1 uses provider configuration and existing lifecycle boundaries to preserve the selected native process policy.

#### Problem

Creation checks alone do not prevent later commands, attachments or direct Activity calls from bypassing the admitted profile.

#### Scope

Enforce actual initial idle/snapshot policy, selected configuration, allowed operations and resource binding at existing SDK/controller, receiving Activity and provider boundaries. Add checks only where existing enforcement is insufficient. Preserve one resource owner and unchanged configuration behavior; do not add a parallel external operation family merely for placement.

#### Out of scope

New snapshot, suspend/resume or restore support, replacement recovery and runtime idle detection are excluded.

#### Acceptance criteria

- [ ] Tests prove an attached reference routes to the same resource without resetting its configuration or acquiring ownership. Closing an attachment does not delete compute. Source: M1 plan and H2.
- [ ] SDK/controller initialization rejects omitted/default or unsupported idle policy and initial snapshot/restore for the selected fresh native configuration before allocation. Require actual `NoIdleTimeout`; a declaration in provider config alone does not prove the controller selected it. Direct receiving calls validate the configuration and identity information available there, without claiming to inspect absent controller fields. Source: M1 plan and H1/H2.
- [ ] Unsupported execute, snapshot, restore, suspend/resume and idle requests produce zero forbidden provider calls after startup and through attachments. Source: M1 plan and H1/H2.
- [ ] Direct receiving Activity/provider tests reject missing or conflicting required configuration/resource binding independently of the SDK route. Retries retain the selected context. Existing input signatures remain compatible. Source: M1 plan and H2/T1.
- [ ] Owner completion/cancellation tests exercise the existing stop/cleanup path; attached callers cannot become a second cleanup owner. Report provider teardown observations accurately rather than claiming proof of all process death. Source: M1 plan and H2/G1.
- [ ] Legacy command and attachment tests retain their original routing without a new capability prerequisite. Source: M1 plan and H2/T2.

#### Dependencies and blockers

CNR-2 supplies the revised configuration and identity contract through existing inputs. This work can proceed beside CNR-3 after that revision is reviewed and verified.

#### Source evidence

[M1 contract](../plan.md#source-contract-and-extension-surface); [H1, H2, T1, T2 and G1](../ticket-evidence.md#inspected-sources).

#### Open questions

Record any existing attachment or cancellation path that cannot preserve the selected profile before changing it. Such a source impact requires a bounded correction, not a second lifecycle controller.

**Implementation source impact, 2026-10-28:** The existing attachment addresses only its owner Workflow and already preserves controller configuration and resource identity. Its `RequestStop` also signals owner shutdown. The bounded correction issues version 2 references for fresh native configurations and refuses attachment shutdown through those references; version 1 legacy references retain their behavior. Native status adds an optional typed resource binding, omitted for legacy status. Direct native stop checks this binding and current machine metadata before deletion. The controller retains all ownership and operation routing. No new Activity family or lifecycle controller is introduced. References and labels remain reconciliation data in a trusted environment, not authentication against forged inputs or direct signals.

Activation is limited to fresh native executions. Pre-policy experimental native histories are not a compatible deployment baseline and require a separate activation/versioning decision before migration. The retained legacy command sequence and fixtures must continue to replay unchanged. This does not authorize such a migration or a live provider run. Implementation and fresh combined verification remain in progress; acceptance is not yet recorded.

### CNR-5 Demonstrate a controller owned external process

Status: OPEN

- Type: Task
- Priority: High
- Estimate: 2 points (confidence 85 percent)
- Labels: Type: Task, Topic: External runtime
- Parent: CNR-1
- Blocked by: CNR-3, CNR-4
- Blocks: CNR-6
- Related: none
- Owner role: Harness example contribution owner
- Requirements: CR-03, CR-06, CR-15; applicable AC-03 and AC-04

#### Context

The first useful demonstration is a generic native process managed by the existing harness. It does not require the Claude integration.

#### Problem

Reviewers need a reproducible example of external placement, capability refusal and compute ownership before evaluating the later native agent composition.

#### Scope

Add one harmless bounded process example through provider configuration and existing `Start`, a fake provider conformance test and instructions for an optional real SmolCloud run. Use explicit `NoIdleTimeout`; no separate execution mode is required.

#### Out of scope

No LLM call, model credential, new cloud allocation, live run, skill execution, host recovery or confidentiality claim is part of this ticket's default proof.

#### Acceptance criteria

- [ ] A documented local fake provider command runs the example and proves one resource owner, process completion and explicit cleanup. A second run exercises cancellation and cleanup. Source: M1 plan and H2/G1.
- [ ] Captured launch configuration contains no in-resource Temporal Worker bootstrap or Namespace credential. The real example's image entrypoint runs only the bounded native process. Source: M1 plan and H1/H3.
- [ ] A deliberately unsupported profile fails before allocation and produces an actionable error. The example does not treat command completion as autonomous runtime idleness. Source: M1 plan.
- [ ] A reviewer can find exact prerequisites, commands, expected results and limits without private records. Optional real execution is labeled separately and not reported as tested by fake conformance. Source: M1 plan.
- [ ] The example and collaboration handoff identify the next early M2 skill demo without making that later integration an M1 acceptance dependency. Source: M1/M2 plan.

#### Dependencies and blockers

CNR-3 and CNR-4 supply actual provider behavior and lifecycle enforcement. Fake conformance is the default acceptance route; no live provider credential is required for it.

#### Source evidence

[M1 example and acceptance contract](../plan.md#focused-acceptance-and-compatibility); [collaboration handoff](../collaboration-handoff.md); [H1, H2, H3 and G1](../ticket-evidence.md#inspected-sources).

#### Open questions

Choose the smallest bounded process and image that match the provider example convention. It must not require paid model access.

### CNR-6 Verify M1 and prepare the upstream review handoff

Status: OPEN

- Type: Task
- Priority: High
- Estimate: 2 points (confidence 85 percent)
- Labels: Type: Task, Topic: External runtime
- Parent: CNR-1
- Blocked by: CNR-5
- Blocks: CNR-1
- Related: none
- Owner role: Contribution owner with independent implementation reviewers
- Requirements: CR-03, CR-06, CR-15; applicable AC-03 and AC-04

#### Context

The revised M1 mechanism requires scoped design review before implementation. Implementation acceptance then needs evidence from the actual changed harness revision; earlier mode/interface verification does not satisfy this gate.

#### Problem

A design PASS, source links or fake example alone cannot prove complete compatibility, admission enforcement and ownership behavior.

#### Scope

Run scoped `verify-change` after implementation, including the target repository's required checks. Prepare a concise draft contribution description, example instructions and collaboration handoff. Keep fixes with the behavior they repair.

#### Out of scope

Publishing a PR or message, paid execution, live provider qualification and upstream merge are separate actions. No M2 through M4 guarantee is accepted here.

#### Acceptance criteria

- [ ] Independent implementation verification maps every CNR-2 through CNR-5 criterion to exact revision evidence and reports no unresolved material defect for the selected M1 scope. Source: M1 verification contract.
- [ ] A lead rerun confirms applicable target CI commands, legacy history replay, fresh external histories, fake provider retry/adoption cases, direct Activity refusal, attachment isolation and completion/cancellation cleanup. Source: M1 plan, T1/T2 and G1.
- [ ] A clean example run and negative configuration run reproduce CNR-5 results. Retain actionable evidence without requiring private raw diagnostics to review the contribution. Source: M1 plan.
- [ ] The draft upstream description states the problem, additive behavior, compatibility, proof and limits. The collaboration handoff separates harness ownership from the native SDK/Transport work and lists unresolved joint seam questions. Source: M1 plan.
- [ ] The M1 exit record distinguishes implementation acceptance, pending maintainer acceptance and unexecuted live checks. It identifies the bounded early M2 design/ticket handoff instead of expanding all later work. Source: M1/M2 plan.

#### Dependencies and blockers

CNR-5 transitively requires every other M1 work ticket. Maintainer review gates upstream merge, not preparation of this local review package.

#### Source evidence

[M1 acceptance and compatibility](../plan.md#focused-acceptance-and-compatibility); [M1 design review](../verification-report.md); [T1, T2 and G1](../ticket-evidence.md#inspected-sources).

#### Open questions

Select the actual review revision after implementation. Do not reuse a prior design verdict as implementation proof.
