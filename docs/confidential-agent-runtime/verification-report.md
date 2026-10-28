# Stage appropriate design verification

Current applicability, 2026-10-27: this report preserves the review of the earlier mode/interface design. The maintainer subsequently clarified that provider configuration and existing `Start` are preferred; the operator selected that revision in the [M1 plan](plan.md#m1-explicit-external-runtime-support). This historical PASS does not approve the revised mechanism. The [CNR-2 ticket](tickets/m1-external-runtime.md#cnr-2-launch-an-explicit-external-runtime-without-changing-legacy-execution) and [CNR-3 ticket](tickets/m1-external-runtime.md#cnr-3-provision-an-external-smolcloud-runtime-with-stable-ownership) own fresh combined acceptance of compatibility and concrete provider admission. CNR-4 lifecycle policy, the generic demo and complete M1 verification remain pending. The original review results below are retained without reinterpretation.

Date: 2026-10-26. Verdict: **PASS for M1 design**. Both independent reviewers found zero material core findings and zero material remedy findings in the selected Sandbox Orchestration Harness contribution. This approves the design for implementation and testing. It is not an implementation PASS, upstream merge approval or a PASS for the complete future runtime.

## Selected scope

Subsequent supplemental research at EV-33 adds candidate reuse decisions and more concrete proof cases for later stages. It was not part of this independent M1 review. The M1 contract and tickets remain unchanged; later component selection and recovery mechanisms still require their own scoped review. Current evidence gate counts may therefore exceed the historical counts recorded below without representing another independent pass.

The project owner explicitly requested staged sandbox work. The immediate scope is the full M1 contract in [the plan](plan.md#m1-explicit-external-runtime-support): explicit external runtime placement, narrow capability admission, one existing provider extension, an ordinary example and compatibility checks. Future recovery and confidential environment requirements remain in the specification and their later milestones. They are not prerequisites for M1 and are not waived.

The earlier full roadmap review returned CONDITIONAL. Its blanket reopening of nine approvals was corrected against the retained local configuration and retention records. A subsequent full outcome investigation identified the unresolved active-child recovery mechanism. This report does not relabel that broader outcome PASS. It records the later, explicitly selected phase scope.

## Source identities and actual evidence

| Source | Identity and use |
|---|---|
| Harness | `24f09129335f8057750f09f84a45b9c76c99d9c1`; current main independently checked unchanged |
| Current harness paths | `sdk/compute/provider.go`, `sdk/compute/smolcloud/provider.go`, `sdk/sandbox.go`, `sdk/workflow/activities.go` and `sdk/workflow/workflow.go`, read directly from pinned GitHub source |
| Retained local application | `cad28f3e6024ccd992df44cba4306a74ff50140a` plus existing uncommitted documents; application source, tests and lock unchanged |
| Maintained application map | Content fingerprint `sha256:e157cfb4e532a0ef95f09ccba860da608ec42fb7237dd43f11c5aabf6606636f`; failed aggregate and three unresolved dynamic targets remain disclosed in the [receipt](evidence/topology-receipt.json) |
| Later Claude integration | PR #169 `32969f3ffa7688cb1cde250f1245e4ed70eb53d6`; SDK 0.2.163 source commit `1ef6d8c71bb0e44a6b33fe61497864f21e17fdb7`; not adopted by M1 |

The harness was inspected through immutable remote source reads; no local harness checkout or complete runtime topology is claimed. The map remains a source derived lower bound for the retained application. Atlas did not supply the harness source; direct GitHub reads supplied it. Temporal Docs and installed domain/developer guidance grounded retry, ownership and replay reasoning.

## Claim ledger

| ID | Claim and provenance | Result |
|---|---|---|
| S1-C1 | Current behavior: the existing provider Start contract requests an in-resource Worker, and SmolCloud injects its queue environment | Confirmed from pinned source; explicit external placement addresses a real contract gap |
| S1-C2 | Proposed design: optional external interfaces preserve the legacy Provider contract and refuse unsupported combinations before allocation | Coherent and implementable; implementation must prove zero allocation and no legacy fallback |
| S1-C3 | Proposed design: the existing Child Workflow remains the compute owner; external adoption retains original identity and validates mode/configuration | Coherent and implementable; duplicate, conflict, attachment and cleanup tests remain required |
| S1-C4 | Proposed design: omitted/zero mode preserves existing command selection; new external Activities carry explicit mode/profile state | Coherent and implementable; retained-history replay is required before shipping |

Partial precedent for a new composition is not a claim that an upstream official recipe already implements it. The source contracts and explicit failure responses support the design; its implementation acceptance checks remain open.

## Repository impact and compatibility

Primary change classification is `feature`, with `improvement`, `test_change` and `documentation_change` as secondary classifications. M1 lands in the harness repository; it does not require adopting or modifying the Claude integration draft.

| Surface | Required change |
|---|---|
| Provider interface/registration | Add optional external start and mode-specific capabilities; keep legacy Provider unchanged |
| SDK options and controller state | Retain explicit mode/profile/identity and validate requests; old zero mode preserves defaults |
| Activity inputs and routing | New external operations validate mode/profile independently; legacy histories retain old command behavior |
| SmolCloud creation/adoption | Add stable external naming and labels, omit Worker bootstrap, check matching external ownership/configuration/network; refuse unexpected paused recovery |
| Command/lifecycle/attachment paths | Apply admitted capabilities after startup and through attached references; attachment grants no new ownership or capability |
| Example and tests | Harmless external process, fake-provider conformance, request inspection, cancellation/cleanup and legacy replay |

Provider credentials remain on the outside Activity Worker. The first external profile requires `NoIdleTimeout` and refuses restore, snapshot and suspend/resume. This is ordinary external placement, not a confidential execution claim. The example does not require model credentials or invoke an LLM. An optional live provider run requires separate authorization.

## Corrections incorporated

The source review exposed two SmolCloud reuse hazards: existing adoption checks do not establish the new external mode/configuration binding, and recovered paused resources can invoke legacy Resume. The plan now requires mode-specific external checks and refuses that unsupported recovery case while preserving legacy behavior.

The plan also retains the admitted profile across later operations and attached references. Capability refusal is not limited to creation. New receiving Activities must enforce the same profile against direct/retried inputs. These are implementation acceptance obligations, not a new controller or a broad lifecycle rewrite.

Separate later-stage corrections distinguish native writer shutdown from compute termination, retain the AWS NitroTPM/KMS direction and trusted cloud provider, specify a candidate paid request envelope, and place output release policy in registered job configuration. Those improvements do not expand M1.

## Independent review and validation

`protocol_contract_validation` and `protocol_adversarial_validation` began as isolated read only reviewers and did not author the design. Both reviewed the phase-specific contract and actual pinned source, then returned M1 PASS with zero remaining material findings. The lead independently inspected the source paths and incorporated the bounded clarifications above.

Specification and plan evidence gates pass with 32 matching rows, seven constitution sections, 14 matched assumptions, 14 reopened local/Atlas references, 18 structurally validated URL references and no unresolved reference. The document checker preserves all 201 historical obligations and all 70 ticket blocks. These are document checks, not runtime proof.

Implementation must run the named fake-provider, request-shape, direct Activity rejection, attachment, cleanup and retained-history replay checks. No application implementation, live provider/model run, attestation test, dependency adoption, commit, push or external publication occurred.

## Later stage gates and next work

- M2: local native SDK/CLI composition, verified skill placement and the sealed content boundary. Use synthetic input and the approved local profile.
- M3: native outcome/authority and accepted session/workspace restoration. Active-child recovery still needs an identified native mechanism; safe parking does not fulfill positive recovery.
- M4: qualify the AWS Attestable AMI, independent KMS release, command isolation, real job policies, budget admission and operational transitions.

Business report field design is not an M1 task. Real jobs must supply approved authenticated release policy before private input and key admission. Do not make a concrete assessment schema a prerequisite for the generic harness extension.

The next handoff is `write-tickets` for M1 only, then scoped implementation and `verify-change`. Maintainer review gates upstream acceptance. Any larger or breaking contribution needs discussion before that expansion. Keep the archived DSR backlog historical and preserve later requirements without implementing them all in the first contribution.

## Domain review disclosures

The Temporal design review was installed and applied (discovered as `temporal-design`, invoked by protocol_contract_validation) and returned findings cited at S1-C1, S1-C2, S1-C3, S1-C4.

Temporal product and SDK behavior claims were grounded through Temporal Docs (5 successful connector calls across protocol_contract_validation, protocol_adversarial_validation).

Composed Temporal mechanisms were classified against precedent by protocol_contract_validation: Existing sandbox Child Workflow remains the sole compute lifecycle owner is partial precedent (source Direct pinned source https://github.com/temporal-community/sandbox-orchestration-harness/blob/24f09129335f8057750f09f84a45b9c76c99d9c1/sdk/workflow/workflow.go and sdk/sandbox.go); Mode-specific external start and capability checks reuse provider Activity boundaries and stable identity is partial precedent (source Direct pinned source https://github.com/temporal-community/sandbox-orchestration-harness/blob/24f09129335f8057750f09f84a45b9c76c99d9c1/sdk/workflow/activities.go and sdk/compute/smolcloud/provider.go; additive external branch is proposed); Preserve legacy replay by retaining old command selection and adding an explicit external branch is partial precedent (source https://docs.temporal.io/develop/go/workflows/versioning#patching-with-getversion and pinned harness source; exact implementation replay remains acceptance evidence).

The Temporal developer skill was installed and applied (discovered as `temporal:temporal-developer`, invoked by protocol_adversarial_validation) and returned findings cited at S1-C1, S1-C3, S1-C4.

The target is a spec-driven-temporal package (spec.md and plan.md), and its evidence gate passed.

## Proof checker limits

The legacy proof checker cannot verify the available Codex reviewer transcripts and does not check direct GitHub sources. Its not-proven declarations concern machine attestation of tool/skill delivery; they do not change the scoped engineering verdict. The manifest declaration is the only enforcement for those loads/call counts in this run. No runtime proof or implementation result is inferred.

```text
warning: temporal-design-review is unproven (no transcript supplied for role protocol_contract_validation; pass --role-transcript protocol_contract_validation=<path>); the manifest declaration is the only enforcement for it
warning: temporal-docs-grounding is unproven (0 of 5 declared calls observed; protocol_contract_validation: no transcript supplied for role protocol_contract_validation; pass --role-transcript protocol_contract_validation=<path>; protocol_adversarial_validation: no transcript supplied for role protocol_adversarial_validation; pass --role-transcript protocol_adversarial_validation=<path>); the manifest declaration is the only enforcement for it
warning: pattern-precedent is unproven (no atlas:// source to resolve; Temporal Docs and external sources are not checked); the manifest declaration is the only enforcement for it
warning: temporal-developer is unproven (no transcript supplied for role protocol_adversarial_validation; pass --role-transcript protocol_adversarial_validation=<path>); the manifest declaration is the only enforcement for it
```
