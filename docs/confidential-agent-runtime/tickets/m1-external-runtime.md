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

The [approved M1 plan](../plan.md#m1-explicit-external-runtime-support) extends the existing Go harness. The M1 design review passed; implementation is pending.

#### Problem

The current provider start contract bootstraps a Temporal Worker inside compute. Autonomous native runtimes need explicit external placement and one retained lifecycle owner.

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

Status: OPEN

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

The current harness uses `Provider.Start(ctx, taskQueueName)`. M1 selects optional external start and mode scoped capability interfaces while retaining that contract.

#### Problem

An empty queue or a provider fallback cannot distinguish external execution safely. A retry must retain the original launch identity, and old histories must retain their command selection.

#### Scope

Implement explicit opt in external placement through the SDK, existing controller and receiving start Activity. Validate requested capabilities before allocation. Retain the admitted mode, profile version, normalized provider configuration and stable sandbox/launch identity in controller state.

#### Out of scope

Actual SmolCloud external provisioning is CNR-3. Enforcement of later operations and attached references is CNR-4. No new controller, Python harness SDK or Nexus service is required.

#### Acceptance criteria

- [ ] Recording provider tests prove omitted and zero mode use legacy `Start` with the original queue and command selection. A retained legacy history replays without a nondeterminism error. Source: M1 plan and H1/H2/T2.
- [ ] An explicit external request reaches only the optional external start interface with nonempty, retained `SandboxID` and `LaunchIdentity`. A retry test shows identical identity and configuration on both attempts. Source: M1 plan and T1.
- [ ] Unsupported or unknown modes, absent optional interfaces, failed capability lookup and unsupported requested capabilities produce zero allocation calls. Tests cover both SDK/controller entry and direct receiving Activity input. Source: M1 plan and H1/H2.
- [ ] The first external profile requires explicit `NoIdleTimeout` and refuses snapshot, restore, suspend/resume and unsupported idle policies before dispatch. Tests prove external failure never falls back to legacy `Start`. Source: M1 plan and H1/H2.
- [ ] New external Activity names and explicit inputs preserve the old serialized input interpretation and registrations. Tests inspect retained controller mode/profile/configuration and fresh external history. Any historical command change requires a separate activation/versioning plan. Source: M1 plan and T2/G1.

#### Dependencies and blockers

Start against harness revision H0. Inspect the changed registration and caller paths before editing. Record the selected source revision and any relevant upstream delta in the contribution.

#### Source evidence

[M1 plan](../plan.md#m1-explicit-external-runtime-support); [H0, H1, H2, T1, T2 and G1](../ticket-evidence.md#inspected-sources).

#### Open questions

Exact additive names remain subject to maintainer review. The mode, admission and compatibility outcomes are fixed by the reviewed contract.

### CNR-3 Provision an external SmolCloud runtime with stable ownership

Status: OPEN

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

Extend the existing provider through the M1 optional interfaces. Reuse creation and cleanup only where external identity, ownership, configuration and network checks remain enforced. Keep legacy requests unchanged.

#### Out of scope

Other provider implementations, a new reconciliation framework, snapshot recovery and live cloud qualification are excluded.

#### Acceptance criteria

- [ ] Fake HTTP request tests show external creation omits `TEMPORAL_TASK_QUEUE` and Worker/Namespace credential bootstrap. Provider credentials remain on the outside Activity Worker. Legacy provisioning request tests retain existing behavior. Source: M1 plan and H3.
- [ ] External names use a separate domain from legacy queue names. Creation labels bind harness ownership, external mode, stable sandbox/launch identity and normalized nonsecret image/configuration digest. Tests inspect exact requests across retries. Source: M1 plan and H3/T1.
- [ ] A simulated lost create reply followed by a retry returns the original matching external resource. Same name legacy resources, changed image/configuration, wrong network policy and multiple matches are refused without modifying or deleting conflicting resources. Source: M1 plan and H3/T1.
- [ ] An unexpectedly paused external resource refuses rather than using the legacy resume helper. Tests also prove owned creation failure cleanup and retained legacy adoption behavior. Source: M1 plan and H3.
- [ ] All acceptance tests use a fake provider endpoint. The contribution labels the live example path as unqualified until a separately authorized live check runs. Source: M1 plan.

#### Dependencies and blockers

CNR-2 supplies the explicit start contract and retained identity. The provider implementation must reject unsupported external configurations before allocation.

#### Source evidence

[M1 provider contract](../plan.md#first-actual-provider-and-example); [H3 and T1](../ticket-evidence.md#inspected-sources).

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

The existing SDK distinguishes owned and attached sandbox references. M1 adds retained external policy to the existing lifecycle controller.

#### Problem

Creation checks alone do not prevent later commands, attachments or direct Activity calls from bypassing the admitted profile.

#### Scope

Enforce the retained mode, capability/profile version, normalized configuration and resource binding at later controller operations and receiving external Activities. Preserve one resource owner and existing legacy behavior.

#### Out of scope

New snapshot, suspend/resume or restore support, replacement recovery and runtime idle detection are excluded.

#### Acceptance criteria

- [ ] Tests prove an attached reference routes to the same external resource without resetting its mode or acquiring ownership. Closing an attachment does not delete compute. Source: M1 plan and H2.
- [ ] Unsupported execute, snapshot, restore, suspend/resume and idle requests produce zero forbidden provider calls after startup and through attachments. Source: M1 plan and H1/H2.
- [ ] Direct external Activity tests reject missing or conflicting mode/profile/configuration/resource binding independently of the SDK route. Retries retain admitted context. Source: M1 plan and H2/T1.
- [ ] Owner completion/cancellation tests exercise the existing stop/cleanup path; attached callers cannot become a second cleanup owner. Report provider teardown observations accurately rather than claiming proof of all process death. Source: M1 plan and H2/G1.
- [ ] Legacy command and attachment tests retain their original routing without a new capability prerequisite. Source: M1 plan and H2/T2.

#### Dependencies and blockers

CNR-2 supplies retained external state and receiving Activity inputs. This work can proceed beside CNR-3 after that contract exists.

#### Source evidence

[M1 contract](../plan.md#source-contract-and-extension-surface); [H1, H2, T1, T2 and G1](../ticket-evidence.md#inspected-sources).

#### Open questions

Record any existing attachment or cancellation path that cannot preserve the selected profile before changing it. Such a source impact requires a bounded correction, not a second lifecycle controller.

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

Add one harmless bounded process example, a fake provider conformance test and instructions for an optional real SmolCloud run. Use explicit external mode and `NoIdleTimeout`.

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

The M1 design is approved for implementation. Implementation acceptance needs evidence from the actual changed harness revision.

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
