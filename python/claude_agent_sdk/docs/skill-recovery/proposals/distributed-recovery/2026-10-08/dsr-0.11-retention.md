# DSR-0.11 retention and session-store decision record

Status: Confirmed decision reconciliation (2026-10-14). This record maps existing approvals to DSR-0.11. It selects no production policy and claims no runtime conformance.

## Approved owners and finite policy

The [approved admission decisions](dsr-0.6-configuration.md#approved-admission-decisions-2026-10-12) and [approved local configuration](dsr-0.6-configuration.md#approved-local-configuration-2026-10-14) own the actual values and reader/key matrix. The operator remains accountable. The project maintainer holds retention/storage, session-adapter integration, deployment, gateway/key administration and Security responsibilities. No new holder question is required.

The synthetic case has a 24-hour recovery/reset window and a seven-day retention minimum, extended for every live, parked, reset or replay reference. Apply that policy to native records, exact raw outcomes, required accepted projections/workspace objects, keys and independent authority. Indexes remain disposable. Namespace history expiration does not authorize removal of referenced objects or authority. Unknown horizon/reference state denies deletion; the janitor keeps claims and required state. Finite test values are approved decisions, not proof that retention is enforced.

The production session-store requirement is owned by the same maintainer: every admitted Worker must materialize the exact shared accepted native state, encryption protects stored data, and UUID deduplication rejects conflicting bytes rather than silently overwriting them. The selected protected checkpoint service supplies the local substrate; the native SessionStore adapter and its conformance remain unimplemented. Shared access means compatible authorized access to accepted state, not a shared writable execution directory.

## Reader, key and data-loss obligations

Use the selected scoped reader broker and approved certificate/encryption/key policy at the configuration owner. Authorize the exact namespace/job/session/object version and action before retrieval and decryption. Preserve decryptability and verification keys through all referenced horizons. Viewer, CLI, UI, harness VFS and report entrances must enforce that same policy; the SDK does not automatically propagate reader identity. Cross-session retrieval and unknown retention refuse. Context Mode indexes cannot authorize readers or recover native state.

The [canonical storage contract](../../../spec.md#selected-component-boundaries-2026-10-12) classifies lost acknowledged accepted bytes as durability FAIL. Missing required outcome/postimage/projection parks. Refusal preserves safety but does not turn data loss into a durability pass. Retry cannot fabricate accepted data. DSR-4.2 implements reference-safe deletion; DSR-5.4 and Q-2/Q-6 prove exact recovery, retained keys/authority, cache rebuilding and unauthorized reader refusal. Those tickets remain OPEN.

## Production policy remains separate

No client-approved production duration, compliance basis or production backup policy is selected. Before admitting real client data, the maintainer must obtain the client's policy and bind its recovery horizons, retention/deletion/legal constraints, reader rights and key lifecycle to the offered service. This is an admission condition for that future use, not an unanswered owner question for the approved synthetic profile. Until then, admit no real client data.

## Acceptance mapping

| DSR-0.11 criterion | Decision evidence and disposition |
|---|---|
| Retention holder and value | Approved configuration names the maintainer and synthetic minimum/reference extensions; production is explicitly excluded pending client policy. Satisfied for the approved synthetic decision scope. |
| Session-store holder and three requirements | Maintainer owns shared authorized materialization, encrypted storage and UUID deduplication above. Satisfied as requirements, not implementation. |
| Unknown retention keeps claims | Approved janitor denial above and configuration reader matrix. Satisfied as policy. |
| Accepted-data loss FAIL; missing required outcome/projection parks | Canonical storage contract and this mapping. Satisfied as a decision obligation. |
| Object/key/authority retention and reader refusal | Existing approved finite policy and Q-2/Q-6/DSR-5.4 conformance requirements above. Satisfied as required policy and proof scope; execution remains pending. |

Closing this decision record does not close the janitor, session-store adapter, enforcement, local execution or portable qualification gates. It also does not answer candidate BD rows in fixed inventories or change retained evidence records.
