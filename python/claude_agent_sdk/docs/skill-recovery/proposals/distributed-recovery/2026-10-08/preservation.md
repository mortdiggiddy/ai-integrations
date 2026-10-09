# Planning evidence preservation

Status: Local preparation, not committed or published. Preservation approves no design choice, completes no runtime acceptance criterion and authorizes no deletion.

The [supporting evidence](supporting-evidence/README.md) closes digest-only source gaps needed to inspect maintained ticket dispositions and proposal planning. Its [manifest](preservation-manifest.json) binds original and sanitized projection hashes separately. Current documentation checks are supplied by the repository's [planning checker](../../../check_planning.py); they require no originating private directory or private assumption index. Historical migration/publication manifests remain unchanged and describe their original snapshots, rather than newly edited documents.

The same manifest separately binds two historical shutdown verification logs discovered as ignored dependencies during isolated checking. Their published copies preserve the original suite and false readiness failure results; exporting them performs no new experiment.

The maintained planning owners remain the [canonical documents](../../../canonical-documents.md), [tickets](../../../tickets/README.md), [conditional proposal](README.md) and [DSR-0.6 preparation](dsr-0.6-preparation.md). Historical captured statements inside evidence projections do not override current dispositions. The [preservation review](preservation-review.md) owns the observed checks and their limits.

## Cutover conditions

1. Verify every original file in a separate archive against its source digest, retaining historical failures, raw artifacts, publication manifests, reservation records and configuration bytes. Configuration is excluded from inspectable exports and is not decoded during preservation. A second local copy shares the host failure domain; preservation on another host or durable backup is a separate operator responsibility.
2. Verify current planning from an isolated repository export with no access to the originating private tree. Check source projections, ticket/assumption/milestone coherence, local links and evidence bindings. This is documentation preservation proof, not runtime qualification or a full platform matrix.
3. Obtain explicit authorization to commit and publish the prepared changes, run the required publication checks and verify the exact remote revision. An uncommitted working tree is not GitHub parity. Preservation documentation does not approve DSR-0.6 or adopt the distributed proposal.
4. Confirm the separate archive is retained before an explicitly authorized removal. This package does not delete the originating private tree or the repository checkout.

Historical migration checking depends on archived original sources and remains an archive operation. Continuing repository checks use maintained owners and the current preservation manifest. Future evidence exports must follow the same original/projection distinction rather than overwrite historical receipts or reinterpret sanitized output as original runtime bytes.
