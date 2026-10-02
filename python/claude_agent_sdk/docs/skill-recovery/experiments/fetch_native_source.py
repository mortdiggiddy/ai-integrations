"""Fetch a pinned test source closure without installing or executing it."""

import argparse
import base64
import hashlib
import json
import subprocess
from pathlib import Path, PurePosixPath


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path(__file__).parent / "results/native-source-manifest.json",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    if root.exists():
        parser.error("--root must name a fresh disposable source directory")
    location = Path(__file__).resolve()
    repo = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=location.parent,
        capture_output=True,
        text=True,
        timeout=5,
    )
    repo_root = (
        Path(repo.stdout.strip())
        if repo.returncode == 0
        else location.parents[5]
        if location.parent.name == "experiments"
        else None
    )
    if repo_root is not None and root.is_relative_to(repo_root.resolve()):
        parser.error("--root must be outside the repository")
    manifest = json.loads(args.manifest.read_text())
    if manifest["repository"] != "temporalio/ai-integrations":
        parser.error("unexpected source repository")
    revision = manifest["revision"]
    if revision != "2ab873cc23a1b3224531a5634c1f6d1c8ef0ea1f":
        parser.error("unexpected source revision")
    sources = []
    for entry in manifest["files"]:
        relative = PurePosixPath(entry["relative_path"])
        source = PurePosixPath(entry["path"])
        if relative.is_absolute() or ".." in relative.parts:
            parser.error("source destination escapes scratch")
        if source != PurePosixPath("python/claude_agent_sdk") / relative:
            parser.error("source manifest path differs from relative path")
        response = subprocess.run(
            [
                "gh",
                "api",
                f"repos/{manifest['repository']}/contents/{source}?ref={revision}",
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        data = json.loads(response.stdout)
        if data.get("encoding") != "base64":
            raise RuntimeError("source response has unsupported encoding")
        content = base64.b64decode(data["content"])
        if hashlib.sha256(content).hexdigest() != entry["sha256"]:
            raise RuntimeError(f"source hash differs: {relative}")
        sources.append((relative, content))
    root.mkdir(parents=True)
    for relative, content in sources:
        target = root / str(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    print(json.dumps({"revision": revision, "verified_files": len(sources)}))


if __name__ == "__main__":
    main()
