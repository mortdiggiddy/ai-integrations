# Distributed recovery proposal diagrams

These views illustrate the conditional proposal. They do not establish runtime support or close ticket acceptance criteria. The candidate specification and plan own the design. Earlier diagram revisions are removed from this folder; Git history keeps them.

## Complete architecture review views

The [assessment durability walkthrough](assessment-durability/assessment-durability.html) presents the historical assessment design. Its [artifact receipt](assessment-durability/artifact-receipt.json) identifies the exact delivered bytes. Receipt paths are portable projections: local checkout, generator and browser executable prefixes are removed; timestamps, results and artifact digests are unchanged. Records under `history/` describe earlier review inputs and do not prove the current artifact. These views do not define the staged runtime specification.

The [architecture review pack](../architecture-review.md) contains Mermaid views for component/trust boundaries, payload encryption/offload, native checkpoint publication, effect outcomes, replacement barriers, harness/VFS correlation, Nexus policy, key/retention, confidential execution and positive child/parallel requirements. These are evaluation inputs, not qualified deployments.

## Skill package and engine attachment views

These views explain the [mandatory SDK execution path](../../../../spec.md#sdk-entrypoint-and-session-control), [project adapter contracts](../../../../spec.md#project-owned-adapter-record-and-operation-contracts) and [approved local configuration](../dsr-0.6-configuration.md#approved-local-configuration-2026-10-14). The canonical specification owns the contracts, the configuration owns the finite profile choices, and the [maintained tickets](../../../../tickets/README.md) own implementation and acceptance. These views add no contract or status authority.

| View | SVG | Use |
|---|---|---|
| Existing skill package, native Claude execution and Temporal coordination | [SVG](skill-execution-binding.svg) | Read first for the caller, service, package admission, runner, native engine and candidate Mods layer |
| Engine attachment to project contracts | [SVG](engine-adapter-boundaries.svg) | Read next for accepted state, dispatch, storage, execution control, readers/keys, artifact processing and transport |
| Recovery proof sequence | [SVG](recovery-proof-sequence.svg) | Compare the initial local container proof with the required later host-loss and partition proof |

An admitted skill retains its instructions, scripts and references. Native skill loading does not require Mods. The project runner binds package admission, workspace, tools and runtime policy to the SDK. TypeScript Mods are a separate candidate hook layer inside SDK-launched Claude Code; they do not own durable authority. Package compatibility, script dependencies and permissions must be admitted. These views do not promise that every existing skill runs unchanged.

The engine attachment view is a typed operation map, not a physical deployment topology. Trusted adapters mediate the operations; job code does not receive controller privileges or unrestricted key access. The views are not the complete acceptance inventory. Selected native projection, restricted Code Mode/harness integration and positive child/parallel qualification remain required at their existing ticket owners.

Independent source review on 2026-10-14 passed the three SVGs for scoped semantic fidelity. All three passed XML parsing. Candidate validation, delivery and strict checks passed, but full finalization did not pass because browser checks were skipped. No rendered visual review occurred. A Windows process launch failure from the review environment prevented the permitted browser routes; no software was installed to repair it. Browser rendering, clipping, routing and interactive behavior remain unverified.

The maintained architecture review pack now routes pending intent through the governed runner/Session/Entity boundary, separates the read-only viewer Activity from effect operations, and identifies the selected reader broker with unimplemented scope propagation and runtime qualification. These are documentation corrections; they establish no runtime admission. Frozen evidence and the dated handoff remain unchanged. The recorded browser/visual review limitation still applies to the three SVGs.
