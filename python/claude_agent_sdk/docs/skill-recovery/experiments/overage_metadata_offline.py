"""Check extracted CLI metadata functions and the SDK parser without transport."""

import hashlib
import json
import subprocess
from pathlib import Path

import subscription_sdk_control as control
import subscription_sdk_run as previous


def main():
    """Print pure source checks; run only in the pinned offline container."""
    from claude_agent_sdk._internal.message_parser import parse_message

    binary = Path("/opt/claude").read_bytes()
    assert hashlib.sha256(binary).hexdigest() == previous.CLI_HASH
    records = previous.verify_sdk()
    functions = []
    anchors = {}
    for name, following in (
        ("Tot", "uzo"),
        ("uzo", "yPn"),
        ("xot", "dzo"),
        ("ia", "Xwr"),
    ):
        lower_bound = 202572000 if name == "ia" else 197484000
        start = binary.index(f"function {name}(".encode(), lower_bound)
        end = binary.index(f"function {following}(".encode(), start)
        assert end - start < 3000
        functions.append(binary[start:end].decode())
        anchors[name] = {
            "byte_offset": start,
            "sha256": hashlib.sha256(binary[start:end]).hexdigest(),
        }
    # Helpers replace unrelated offers and utilization readings, never transport.
    setup = """
const Pse = 'anthropic-ratelimit-unified-overage-in-use';
let warning = null;
function kPn() { return undefined; }
function gPn() { return {}; }
function szo() { return {}; }
function hPn() { return warning; }
"""
    cases = """
function run(status, overage, inUse, claim, derived = null, include = true) {
  warning = derived;
  const h = new Map();
  if (status !== null) h.set('anthropic-ratelimit-unified-status', status);
  if (overage !== null) h.set('anthropic-ratelimit-unified-overage-status', overage);
  if (inUse !== null) h.set(Pse, inUse);
  if (claim !== null) h.set('anthropic-ratelimit-unified-representative-claim', claim);
  return ia(Tot({get: k => h.get(k) ?? null}, false).own,
            {includeOverageInUse: include});
}
const tests = [
 ['observed-shape', run('allowed','allowed','true','overage'), false, true],
 ['fallback', run('rejected','allowed','true','five_hour'), true, true],
 ['fallback-warning', run('rejected','allowed_warning','true','five_hour'), true, true],
 ['eligibility-only', run('allowed','allowed',null,'five_hour'), false, undefined],
 ['false-header-omitted', run('allowed','allowed','false','five_hour'), false, undefined],
 ['nonliteral-header-omitted', run('allowed','allowed','TRUE','five_hour'), false, undefined],
 ['default-status', run(null,'allowed','true','overage'), false, true],
 ['derived-warning-preserves-use', run('allowed','allowed','true','overage',
   {status:'allowed_warning',isUsingOverage:false,rateLimitType:'five_hour'}), false, true],
 ['emitter-suppresses-use', run('allowed','allowed','true','overage',null,false), false, undefined],
];
for (const [name,value,using,inUse] of tests) {
  if (value.isUsingOverage !== using || value.overageInUse !== inUse)
    throw new Error(name);
}
console.log(JSON.stringify(tests.map(([name, value]) => ({name, value}))));
"""
    result = subprocess.run(
        ["node", "-e", setup + "\n".join(functions) + cases],
        check=True,
        capture_output=True,
        text=True,
        timeout=15,
    )
    vectors = json.loads(result.stdout)
    checked = []
    for vector in vectors:
        raw = vector["value"]
        parsed = parse_message(
            {
                "type": "rate_limit_event",
                "rate_limit_info": raw,
                "uuid": "offline-fixture",
                "session_id": "offline-fixture",
            }
        )
        assert parsed.rate_limit_info.raw == raw
        assert parsed.rate_limit_info.rate_limit_type == raw.get("rateLimitType")
        assert parsed.rate_limit_info.overage_status == raw.get("overageStatus")
        monitor = control.Monitor()
        reason = monitor.inspect(
            {"kind": "RateLimitEvent", "message": previous.encode(parsed)}
        )
        assert reason == "ambiguous_active_or_unverifiable_overage"
        assert monitor.overage_clear_seen is False
        checked.append({**vector, "unchanged_monitor_stop": reason})
    clear = {
        "status": "allowed",
        "isUsingOverage": False,
        "overageInUse": False,
        "rateLimitType": "five_hour",
    }
    monitor = control.Monitor()
    assert (
        monitor.inspect(
            {
                "kind": "RateLimitEvent",
                "message": {"rate_limit_info": {"status": "allowed", "raw": clear}},
            }
        )
        is None
    )
    assert monitor.overage_clear_seen is True
    print(
        json.dumps(
            {
                "status": "passed",
                "cli_sha256": previous.CLI_HASH,
                "sdk_record_files": records,
                "extracted_functions": anchors,
                "source_vectors": checked,
                "explicit_false_monitor_control": "accepted",
                "model_cli_spawns": 0,
                "transport_starts": 0,
                "limits": [
                    "Pure extracted functions, not a full CLI execution",
                    "Utilization warning injected; window tracking not replayed",
                    "No observed response headers or provider billing verified",
                    "Monitor unchanged; missing overageInUse still stops",
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
