# Portable target preparation review

Verdict: CONDITIONAL (2026-10-09). The confirmed objective is recovery on another host with the original disk unavailable. The revised [DSR-0.6 preparation](dsr-0.6-preparation.md) supports preparation of the existing distributed route without claiming adoption, completed acceptance criteria or demonstrated distributed recovery. Cold immutable restoration is the preferred proposal; independently durable shared storage remains a valid alternative when it survives the execution-host fault domain and preserves protected authority.

## Scope and identities

This full pass reviews the preparation document and its canonical planning/ticket references against published baseline `4553c340ed4ba8477de09af4888bd00008db8e41`. Preparation SHA256: `1a5ef407f5150474da47d4bb19de4b7f17463d3236b830e7036d48df9dca7f1a`. The [manifest](portable-target-review-manifest.json) records the domain review. The four candidate package artifacts remain unchanged. This is not a new full qualification of that package, a runtime test, a platform matrix or implementation authorization. Historical preparation and integration reviews retain their original scope.

The implementation boundary remains the canonical mandatory SDK entrypoint, accepted segment before effects, exact original pending call/result recovery, ambiguous Bash parking, authoritative cleanup before replacement and denial of unsupported child recovery. Only design preparation, evidence navigation and owning ticket notes change. No executor or SDK code changes.

## Claim ledger and independent reconciliation

| Claim | Evidence and disposition |
|---|---|
| PT1: Accepted conversation and workspace must survive loss of the original disk | Confirmed objective. Existing storage synthesis and candidate M2/P4 provide the proposed qualification path. Host-local storage alone cannot meet it. An independently durable shared filesystem can meet the data prerequisite and is retained as an alternative. Neither route has passed this qualification. |
| PT2: Restoration must not restore permission to repeat an effect | Required by canonical original-call recovery and conservative effect admission. Existing storage/fencing synthesis proposes authority outside restored files and outer resets. Entity scheduling or protected transactional unique records remain alternatives. Workflow code accepts bounded observations; filesystem publication and physical process inspection remain outside it. Unknown Bash parks before model delivery or further dispatch. |
| PT3: Portable takeover requires lifecycle proof and explicit adoption | Canonical cleanup and candidate M2/P3 require exact old-incarnation termination, descendants and restart prevention. Reachable storage, timeout, cancellation, lease expiry and force deletion do not establish physical death. BD-1/BD-2/BD-3/BD-6 choices remain open where applicable. The goal confirmation does not adopt the distributed protocol or authorize DSR-2.1. |

`integration_contract_review` and `integration_adversarial_review` independently reviewed the complete preparation and relevant governing sources. Both returned CONDITIONAL with no material core or remedy defect. They agreed on the cold restore preference, durable shared storage alternative, unresolved adoption and termination prerequisites, and preservation of ambiguity parking. They received the same target but reviewed separately; their findings were reconciled by the lead. Three nonmaterial stale phrases about the shared target, volume choice and qualification approval were corrected and directly checked by the lead. Those wording corrections do not select a backend or change the qualified scope.

The current implementation and completed Phase 1 dispositions remain bounded evidence. Upstream native records and conversation recovery remain reuse candidates at the integration source pins recorded in the preparation and coverage map. No new upstream compatibility or recovery behavior is demonstrated here.

## Conditions and smallest next qualification

The prepared recommendation is owned by DSR-0.6. Select the portable preservation route, accepted acknowledgement/metadata contract, independent authority and lifecycle, trusted exact-incarnation termination source, and responsible storage/deployment, Security and integration roles. BD-6 adoption must reconcile the canonical specification and affected ticket dependencies before implementation. The preparation owns the detailed alternatives, risks and owner-decision split; this report does not duplicate them.

The smallest portable qualification reuses candidate M2/P4 with one accepted conversation/workspace pair restored on H2 after removing H1 disk access. Add M2/P3 with the old execution alive during control partition and effect egress retained: replacement must remain denied until independent whole-execution termination is established. Existing P1 rollback and P2 publication/acceptance-gap cases must also preserve original identity and prevent repeat dispatch. Exact definitive results must match required postimages; uncertainty parks. Lost accepted bytes are a durability failure even if refusal preserves safety. Surviving-host container replacement is only a preliminary control.

Mods, response escrow, positive child recovery, multiple pending calls and confidential execution remain deferred under their recorded qualification limits. No new experiment or model call ran. The single next action is the portable storage/authority adoption decision and canonical rebaseline preparation, not DSR-2.1 implementation.

## Grounding and verification limits

Existing proposal research and reviews were reused. The lead made one successful fresh Temporal Docs connector call about External Storage and accepted filesystem restoration, and one successful Atlas wrapper query about host loss and dispatch authority. The current independent reviewers made zero fresh Docs calls. External Storage documents payload references and durable backing storage; it does not supply this complete filesystem checkpoint and physical termination protocol. Previously grounded cancellation and Entity Workflow evidence was reused. No universal absence claim follows from the limited precedent search.

The manifest gate returned `status: complete`. Its disclosures are:

The Temporal design review was installed and applied (discovered as `temporal-workflow-design-critic`, invoked by integration_contract_review) and returned findings cited at PT1, PT2, PT3.

Temporal product and SDK behavior claims were grounded through Temporal Docs (1 successful connector calls across lead).

Composed Temporal mechanisms were classified against precedent by integration_contract_review: Accepted head and immutable exact conversation/workspace receipts is partial precedent (source https://docs.temporal.io/external-storage); Independent Entity Workflow effect admission is partial precedent (source https://docs.temporal.io/design-patterns/entity-workflow#implementation); Complete original pending recovery with physical host termination is no precedent found (source https://docs.temporal.io/activity-execution#cancellation).

The Temporal developer skill was installed and applied (discovered as `temporal:temporal-developer`, invoked by lead) and returned findings cited at PT2.

The proof checker returned `not-proven` for all four applied rows. It cannot validate this Codex skill-read evidence or resolve the role transcript; the manifest declaration is the only enforcement for those rows in this run. It does not validate Temporal Docs URLs as Atlas sources. This is a proof limitation, not runtime evidence or an assertion that a native skill invocation was mechanically proven.

warning: temporal-design-review is unproven (no transcript supplied for role integration_contract_review; pass --role-transcript integration_contract_review=<path>); the manifest declaration is the only enforcement for it

warning: temporal-docs-grounding is unproven (0 of 1 declared calls observed; lead: harness codex but the session transcript could not be resolved (unavailable); pass --transcript); the manifest declaration is the only enforcement for it

warning: pattern-precedent is unproven (no atlas:// source to resolve; Temporal Docs and external sources are not checked); the manifest declaration is the only enforcement for it

warning: temporal-developer is unproven (harness codex but the session transcript could not be resolved (unavailable); pass --transcript); the manifest declaration is the only enforcement for it
