# DSR-0.6 concrete configuration design review

Verdict: CONDITIONAL (2026-10-11). The [configuration](dsr-0.6-configuration.md) is a coherent proposed qualification target with no unresolved material design defect after reconciliation. Product selection, exact configuration/owners, protocol adoption, upstream agreement and runtime evidence remain blockers. Architecture direction approval is retained; it is not expanded into product or implementation approval.

## Contract and identity

Full pass on the single configuration document against `design-base` baseline `4553c340ed4ba8477de09af4888bd00008db8e41` plus preserved pending planning edits. Configuration SHA256: `50f1cc273eb3ac182a8526c379529679437bc7260369ec0f926f01234d70b2f4`. The [manifest](dsr-0.6-configuration-review-manifest.json) records domain outcomes. Candidate spec/plan/evidence files, implementation and completed Phase 1 remain unchanged. This is not a full candidate package, runtime, topology or platform matrix verification.

Governing sources are canonical accepted-segment/original-pending recovery, conservative Bash uncertainty and cleanup requirements; DSR-0.6 approval limits; maintained storage synthesis/fencing/substrate research and conditional candidate milestones. Upstream compatibility remains governed by the pinned source comparison and interface agreement in earlier integration preparation. Repository impact is design/ticket navigation now; later canonical workspace/admission/lifecycle and existing integration/qualification tickets are mapped by the configuration. No second executor is introduced.

## Independent findings and reconciliation

The contract and adversarial reviewers (`integration_contract_review` and `integration_adversarial_review`) reviewed the complete authored target separately and reread the final corrected target. Existing roles were reused, with independent reasoning and no shared reviewer report during evaluation. Both returned CONDITIONAL with zero unresolved material defects. This is independent role review, not a claim that entirely new agent sessions were created.

| Claim | Finding and disposition |
|---|---|
| CK1 storage | S3 objects have exact version identities/application digests and complete acknowledged components before acceptance. Versioning alone is not immutability; policy, keys, lifecycle, metadata and materializer remain qualification conditions. Routine cleanup cannot destroy sole required bytes; urgent destruction retains uncertainty/data-loss classification. |
| CK2 authority | Independent Entity owns scheduling, duplicates return status/results, application dedup survives admitted continuation and authority loss refuses. Protected namespace or equivalent administration gateway is a proposed operational prerequisite, with actual denial tests. No Workflow-ID-specific ACL is presumed. Complete composition has partial precedent, not arbitrary Bash exactly once. |
| CK3 termination | Dedicated EC2 incarnation, external controller, terminal state readback and exclusion of independent relaunch paths are a proposed independent cleanup route. Request acknowledgement, disappearing API object, timeout or lease is insufficient. Whole guest confinement and independent canary tests remain required. Remote requests already issued remain separately unresolved. |
| CK4 adoption and migration | Cold direction is approved; products, exact configuration and complete candidate protocol remain proposed. Canonical and ticket impacts preserve IDs, dependencies, historical records and Phase 1 closure. Old shared-volume and new cold authority modes cannot silently mix; applicable rebaseline precedes implementation. |

Lead independently checked the AWS terminal/version/conditional-write contracts and canonical assumptions. Review-driven requirements for administrative authority protection, application deduplication, publication-before-destruction, metadata credential isolation and DSR-3.5 reset impact were added as explicit proposed obligations and checked by both reviewers. An optional suggestion that DSR-0.8 did not own reset was rejected after reading its actual heading, "Decide how a Workflow reset is detected and handled"; the original reset-impact pointer is correct. No reviewer remedy was promoted to qualified runtime behavior.

## Remaining gates and acceptance evidence

The smallest next operator choice is selection or replacement of AWS S3, protected Entity scheduling and dedicated externally terminated Linux EC2 instances as the first qualification stack. The configuration owns alternatives, all six decision dispositions, risk consequences and smallest tests. Before dependent execution: named storage/deployment, Security and integration roles; exact region/account/policies/keys/retention and authority namespace/admin control; runtime/service/client pins; finite test/workspace/payload/time limits; upstream interface ownership/revision; and applicable canonical protocol adoption/rebaseline.

Qualification sequence remains model-free protocol/authority negatives, separately authorized real provider/storage rig and later native differential proof on the existing SDK path. Require original disk unavailability, lost publication/admission replies, old workspace/outer reset, protected authority reset/recreation denial, actual metadata/credential/descendant negatives and a partitioned old execution still reaching effect egress. A replacement cannot start without exact termination proof. Missing accepted bytes FAIL durability; an uncertain original effect parks without another model request or spawn. Completed experiments do not repeat.

Production sizing/SLO, confidential hardware, Mods, response escrow, positive child recovery and multiple pending calls retain recorded qualification limits. No new infrastructure operation, code, installed dependency, model call or runtime result is demonstrated.

## Sources and domain disclosure

This pass used three successful fresh Temporal Docs calls, one each by lead and the two reviewers. The lead and adversarial reviewer each made one successful Atlas wrapper query. Existing research/source captures were reused. Fresh AWS primary reads checked conditional writes, object versions, EC2 termination and stop/start; they establish service primitives only. Domain critic and developer guidance were applied. The full assembled original-pending/workspace/provider-termination protocol has no complete precedent found in this bounded search; that is not a universal absence claim.

Manifest gate: `status: complete`. Disclosures:

The Temporal design review was installed and applied (discovered as `temporal-workflow-design-critic`, invoked by integration_contract_review) and returned findings cited at CK1, CK2, CK3, CK4.

Temporal product and SDK behavior claims were grounded through Temporal Docs (3 successful connector calls across lead, integration_contract_review, integration_adversarial_review).

Composed Temporal mechanisms were classified against precedent by integration_contract_review: Protected Entity owns scheduling and retained application dedup is partial precedent (source https://docs.temporal.io/design-patterns/entity-workflow#implementation); Exact native conversation/workspace receipt plus independently terminated EC2 recovery is no precedent found (source https://docs.temporal.io/activity-execution#cancellation).

The Temporal developer skill was installed and applied (discovered as `temporal:temporal-developer`, invoked by lead) and returned findings cited at CK2.

Proof checker: all four applied rows are `not-proven`. Codex skill reads and unresolved role transcripts are not mechanically validated by the legacy Claude transcript checker; external URLs are not checked as Atlas paths. The manifest declaration is the only enforcement for those rows in this run. This limit does not prove a native Skill invocation or platform behavior.

warning: temporal-design-review is unproven (no transcript supplied for role integration_contract_review; pass --role-transcript integration_contract_review=<path>); the manifest declaration is the only enforcement for it

warning: temporal-docs-grounding is unproven (0 of 3 declared calls observed; lead: harness codex but the session transcript could not be resolved (unavailable); pass --transcript; integration_contract_review: no transcript supplied for role integration_contract_review; pass --role-transcript integration_contract_review=<path>; integration_adversarial_review: no transcript supplied for role integration_adversarial_review; pass --role-transcript integration_adversarial_review=<path>); the manifest declaration is the only enforcement for it

warning: pattern-precedent is unproven (no atlas:// source to resolve; Temporal Docs and external sources are not checked); the manifest declaration is the only enforcement for it

warning: temporal-developer is unproven (harness codex but the session transcript could not be resolved (unavailable); pass --transcript); the manifest declaration is the only enforcement for it
