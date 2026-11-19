# M1 external runtime implementation acceptance

Status: ACCEPTED (2026-11-18, local implementation). Fresh whole-contribution verification accepts the corrected initialization ownership and all 21 active implementation criteria. The five CNR-6 package criteria have current proof. Hosted SDK CI passes on the published revision. Maintainer acceptance and live provider qualification remain separate.

## Reviewed source

Repository: [Sandbox Orchestration Harness](https://github.com/temporal-community/sandbox-orchestration-harness). Branch `external-runtime-demo`, revision `549bd175eeba39f33fe606c49a91cd5f67c55f74`, builds on open [PR #13](https://github.com/temporal-community/sandbox-orchestration-harness/pull/13), verified head `133786bb5e805495532db85ef08bc2075e2bf005`. The new contribution targets its parent's branch while that PR is open. Retarget it to main after its parent lands.

The combined source inventory contains 101 repository files. Its SHA256 is `3808089139e9dc1cd7de6f0ec8265306467b8870a044cfebf4ccef7c56f1320d`, computed over compact sorted JSON from repository relative paths to file SHA256 values. The image entrypoint, example test and instructions are identified in [CNR-5](../tickets/m1-external-runtime.md#cnr-5-demonstrate-a-controller-owned-external-process). A branch name alone does not identify reviewed bytes. Later source changes require the affected verification.

[PR #14](https://github.com/temporal-community/sandbox-orchestration-harness/pull/14) publishes the correction and example together, stacked on PR #13. [Pull request SDK CI](https://github.com/temporal-community/sandbox-orchestration-harness/actions/runs/44370319316/job/135035044347) and [push SDK CI](https://github.com/temporal-community/sandbox-orchestration-harness/actions/runs/44370261128/job/135034830441) both pass for exact head `549bd175eeba39f33fe606c49a91cd5f67c55f74`, completed 2026-11-18 UTC. The new PR has no assigned reviewers, and no account reviewer policy requires assignment. Maintainer approval remains pending. No CodeQL check is present for this stacked head; do not copy a parent's analysis result.

## Acceptance scope

The [M1 plan](../plan.md#m1-explicit-external-runtime-support) and active [CNR-2 through CNR-6 criteria](../tickets/m1-external-runtime.md) govern this review. Historical superseded interface criteria and earlier verdicts retain their original scope. The current interface uses provider configuration, existing `Start` and one sandbox lifecycle controller.

| Contract | Required current proof |
| --- | --- |
| Existing Start and compatibility | Legacy queue/default/registration/wire behavior, stable retry input, retained parent/controller replay and fresh histories. |
| Concrete provider admission | Empty guest bootstrap environment, outside provider credential, configuration/identity/network binding, matching lost-reply adoption, refusal of conflicts and paused resources, owned failure cleanup. |
| Policy through commands and references | Actual `NoIdleTimeout`, initial and later unsupported operation refusal, independent receiving Activity/provider checks, retained configuration/resource context and one owner for cleanup. |
| Local external process | Documented completion, cancellation, explicit cleanup, bounded entrypoint, credential exclusion, refusal before allocation and separate real execution limits. |
| Review package and exit | Fresh combined criterion mapping, lead rerun, clean documented commands, concise public PR description, joint ownership handoff and qualified local acceptance statement. |

## Reproduction

Use the harness's public `examples/external-process/README.md` for exact local server and example commands. The default proof uses local Temporal on port 17293, loopback fake provider HTTP and bounded native processes. It requires no cloud allocation, paid inference, provider credential or Claude execution.

Run the SDK CI command from `sdk`:

```sh
GOWORK=off HARNESS_LOCAL_TEST=1 SMOL_CLOUD_LIVE=0 HARNESS_HISTORY_CAPTURE= go test -json -count=1 -timeout=5m ./...
GOWORK=off go vet ./...
```

Check the exact required-test event set in `.github/workflows/tests.yml`. Run `make bins` and build `examples/database-fork` with the repository's local SDK workspace. Keep any isolated build workspace and generated checksums outside the source inventory. Run all three documented example commands independently and require executed cases rather than skips.

## Verification result

Fresh independent contract, adversarial containment and structural invariant reports map all 21 active implementation criteria and five CNR-6 criteria to the current source, with no unresolved material implementation finding. The final lead SDK suite passes 301 test/subtest results with three expected live/capture skips. The exact CI required-name gate, vet, all 12 Makefile example targets and the database build pass. The three documented example commands pass independently. No implementation source or fixture changes during this verification. Focused race checks pass, including 44 adversarial results. Five negative compiler probes reject invalid records/interfaces.

Current report SHA256 values: contract `abe709b35562a3700a879d5968031e0b71b3b967a43e0ab2f88718710af159b4`; adversarial `3a638d14e08b198b8820d18db193606e006187332a0e84ded20a27b75b470025`; structural `ca5126e9073c9bbf8af9766f5854febee138ba15107c574da659d444dbc75a36`. The final lead rerun and package reconciliation complete the caller duties in those reports. Original failed reports remain dated evidence with their original source identities and verdicts.

## Current initialization ownership

New controllers claim initialization with the pinned SDK's native Workflow mutex before policy changes or the first Activity wait. Validator and receiving handler reject a distinct competing Update. A retry of the same Update ID retains the original result through native Update identity. `exclusive-sandbox-initialization` selects the new behavior; histories without that marker retain their previous path.

`TestLocalConcurrentInitializationOwnership/{same,changed,invalid,legacy}/{stop,cancel}` holds the actual SmolCloud fake create response while a competing Update arrives. All eight cases prove the original result, one create, original configuration/status in Stop, one DELETE and replay. Cancellation is processed before the response is released. `TestControllerInitializationClaimGuardsReceivingHandler` checks the handler boundary. An isolated validator bypass with additional invalid cases passes 15 results. Removing the receiving claim in that copy fails and reproduces the unfinished original handler.

Let older pending initialization finish before deployment, and exclude competing init requests on older controllers. Do not roll back marked active controllers without a separately verified replay transition. No dependency, serialized input, registration or retained history fixture changes.

## Historical counterexample before correction

The existing controller admits a second `sandbox-init` Update while the first Start Activity is pending. The handler does not claim initialization before it waits for the Activity. A later initialization failure sets the shared lifecycle to failed. The main Workflow can then complete with a nil result while the first accepted handler is still running. Releasing the first Start produces a late allocation with no controller left to record its result or call Stop.

Reproduction uses the public controller Workflow and two distinct init Update IDs. Hold the first fresh Start, submit another init that fails, observe controller completion, then release the first operation. The custom provider probe reports `AcceptedUpdateCompletedWorkflow`, the SDK warning `TMPRL1102` and `Stop calls=0`. The lead repeats that result. A second probe holds the actual SmolCloud create response and submits another fresh configuration with a missing image; its constructor fails with nonretryable `ProviderConfigError`. The controller again closes before the first create settles. Releasing the fake response lets the provider complete, with zero observed DELETE calls.

This is an inherited controller race, not a defect introduced by the example. Stable provider naming does not keep a completed controller alive. Ordinary SDK retry reuses an Update ID, but no documented contract excludes distinct concurrent public init Updates. The case violates CNR-4 owner lifetime/cleanup and blocks CNR-6's no-material-defect criterion. Fake allocation observations establish the controller failure; no live cloud leakage is claimed.

The current initialization claim and regression matrix close this finding for new controllers. Historical replay and the documented activation constraints preserve compatibility. The operator authorizes the controller correction, complete verification and contribution publication on 2026-11-18; maintainer acceptance remains separate.

Historical structural report SHA256: `de1b8cb07c96b8a6a09c53f1ba3c5b03f3159bc812301a229c61df40c8446db1`. Independent adjudication SHA256: `0855fbdced0025ff952046e0e32474062a23ee4c47763f6e2a597d3b4018813a`. Both bind the earlier 100 file source map `48fe0e258c6fd1c6468d39098513ed9dede12d780a6231ca12aef747345297d6`.

## Ownership and remaining limits

The [collaboration handoff](../collaboration-handoff.md) owns the joint interface questions. The harness owns provisioning, binding, attachment and compute deletion. The native integration owns the CLI process and transport on that host. Files, readiness, exact package admission and shutdown semantics require a reviewed early M2 composition. That skill demo has separate tickets and is not an M1 dependency.

Local fake conformance does not qualify real image boot, short entrypoint readiness, provider supported observation, cloud teardown, hostile code containment, replacement recovery, attestation or confidential execution. Existing fresh receiving Worker cutover and rollback prerequisites remain applicable. Prior unbound experimental runs need their own transition; no automatic migration is approved. Maintainer review and upstream merge remain pending; any later revision requires its own hosted check evidence.
