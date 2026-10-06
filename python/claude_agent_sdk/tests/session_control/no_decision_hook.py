"""Suppress interception while retaining the production execution observer."""

import json
import os
import runpy
import sys

event = json.load(sys.stdin)
with open(os.environ["BACKSTOP_HOOK_LOG"], "a") as log:
    log.write(json.dumps(event) + "\n")
output = {}
if event.get("hook_event_name") != "PreToolUse":
    output = runpy.run_path(sys.argv[1])["decide"](event)
print(json.dumps({"hookSpecificOutput": output}))
