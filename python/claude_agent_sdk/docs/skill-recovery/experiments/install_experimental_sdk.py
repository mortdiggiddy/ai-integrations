"""Build the approved experimental SDK in a copied dependency environment."""

import argparse
import hashlib
import json
import os
import subprocess
import tarfile
import urllib.request
import zipfile
from pathlib import Path

SOURCE_REVISION = "3ac4b25733d1302c89d0dadd13cab268e64d1213"
SOURCE_HASH = "364ec9f343f793dd5ce9c8aa4bc685101286c732b47a19d90171b15e1db6a022"
CLI_HASH = "15e2d05148f801b5774032faad87e624ecd172e9903288bda448b892eb58fa07"
ARTIFACTS = [
    {
        "name": "hatchling-1.27.0-py3-none-any.whl",
        "url": "https://files.pythonhosted.org/packages/08/e7/ae38d7a6dfba0533684e0b2136817d667588ae3ec984c1a4e5df5eb88482/hatchling-1.27.0-py3-none-any.whl",
        "sha256": "d3a2f3567c4f926ea39849cdf924c7e99e6686c9c8e288ae1037c8fa2a5d937b",
    },
    {
        "name": "trove_classifiers-2026.6.1.19-py3-none-any.whl",
        "url": "https://files.pythonhosted.org/packages/7c/a4/81502f486f01db95bc8320646a8a12511f5e556cb63d5e224d91816605c4/trove_classifiers-2026.6.1.19-py3-none-any.whl",
        "sha256": "ab4c4ec93cc4a4e7815fa759906e05e6bb3f2fbd92ea0f897288c6a43efd15b3",
    },
    {
        "name": "sdk-source.tar.gz",
        "url": "https://codeload.github.com/brianstrauch/claude-agent-sdk-python/tar.gz/"
        + SOURCE_REVISION,
        "sha256": SOURCE_HASH,
    },
]
SNAPSHOT = r"""
import hashlib,importlib.metadata,json,pathlib,sys
out={"prefix":sys.prefix,"python":sys.version,"distributions":{}}
for d in importlib.metadata.distributions():
 name=d.metadata["Name"].lower().replace("_","-")
 out["distributions"][name]={"version":d.version,"metadata_sha256":hashlib.sha256(d.read_text("METADATA").encode()).hexdigest(),"path":str(d._path)}
print(json.dumps(out,sort_keys=True))
"""
PROVENANCE = r"""
import hashlib,importlib.metadata,importlib.util,json,pathlib,sys
import claude_agent_sdk
from claude_agent_sdk import ClaudeAgentOptions
fields=ClaudeAgentOptions.__dataclass_fields__
print(json.dumps({"prefix":sys.prefix,"sdk_file":claude_agent_sdk.__file__,"sdk_version":importlib.metadata.version("claude-agent-sdk"),"temporal_version":importlib.metadata.version("temporalio"),"recover_pending_tool":"recover_pending_tool" in fields,"parallel_tool_recovery":"parallel_tool_recovery" in fields,"recovery_module":importlib.util.find_spec("claude_agent_sdk._internal.main_agent_recovery").origin},sort_keys=True))
"""


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--uv", type=Path, required=True)
    args = parser.parse_args()
    baseline = args.baseline.resolve()
    root = args.root.resolve()
    if root.exists():
        raise RuntimeError("A fresh disposable root is required")
    if root == baseline or baseline in root.parents:
        raise RuntimeError("Disposable root cannot be inside the baseline environment")
    root.mkdir(parents=True)
    report = {
        "source_revision": SOURCE_REVISION,
        "commands": [],
        "downloads": [],
        "status": "started",
    }
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith(("ANTHROPIC_", "CLAUDE_", "OPENAI_"))
    }
    env.update(
        {
            "UV_CACHE_DIR": str(root / "uv-cache"),
            "UV_OFFLINE": "1",
            "UV_NO_EDITABLE": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
        }
    )
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)

    def save():
        (root / "install-record.json").write_text(json.dumps(report, indent=2))

    def run(cmd, cwd=None):
        done = subprocess.run(
            [str(x) for x in cmd], cwd=cwd, env=env, text=True, capture_output=True
        )
        report["commands"].append(
            {
                "argv": [str(x) for x in cmd],
                "cwd": str(cwd) if cwd else None,
                "returncode": done.returncode,
                "stdout": done.stdout,
                "stderr": done.stderr,
            }
        )
        save()
        if done.returncode:
            raise RuntimeError("Command failed: " + str(cmd[0]))
        return done.stdout

    try:
        original_python = baseline / "bin/python"
        before = json.loads(run([original_python, "-c", SNAPSHOT]))
        report["baseline_before"] = before
        site = baseline / "lib/python3.13/site-packages"
        cli = site / "claude_agent_sdk/_bundled/claude"
        if digest(cli) != CLI_HASH:
            raise RuntimeError("Original CLI hash differs from approved identity")
        report["cli"] = {
            "path": str(cli),
            "sha256": digest(cli),
            "version": run([cli, "--version"]).strip(),
        }
        if report["cli"]["version"] != "2.1.274 (Claude Code)":
            raise RuntimeError("Original CLI version differs from approved lane")
        artifacts = root / "artifacts"
        artifacts.mkdir()
        for artifact in ARTIFACTS:
            data = urllib.request.urlopen(artifact["url"], timeout=60).read()
            actual = hashlib.sha256(data).hexdigest()
            if actual != artifact["sha256"]:
                raise RuntimeError("Artifact hash mismatch: " + artifact["name"])
            target = artifacts / artifact["name"]
            target.write_bytes(data)
            report["downloads"].append(
                {**artifact, "actual_sha256": actual, "bytes": len(data)}
            )
            save()
        isolated = root / "venv"
        run(["cp", "-a", baseline, isolated])
        python = isolated / "bin/python"
        copied = json.loads(run([python, "-c", SNAPSHOT]))
        report["copied_before"] = copied
        if Path(copied["prefix"]).resolve() != isolated:
            raise RuntimeError("Copied interpreter did not select disposable prefix")

        def versions(snap):
            return {
                k: (v["version"], v["metadata_sha256"])
                for k, v in snap["distributions"].items()
            }

        if versions(copied) != versions(before):
            raise RuntimeError("Copied dependencies differ from baseline")
        for dist in copied["distributions"].values():
            if isolated not in Path(dist["path"]).resolve().parents:
                raise RuntimeError("Copied distribution escapes disposable prefix")
        requirements = root / "build-requirements.txt"
        requirements.write_text(
            "hatchling==1.27.0 --hash=sha256:"
            + ARTIFACTS[0]["sha256"]
            + "\ntrove-classifiers==2026.6.1.19 --hash=sha256:"
            + ARTIFACTS[1]["sha256"]
            + "\n"
        )
        run(
            [
                args.uv,
                "pip",
                "install",
                "--python",
                python,
                "--no-index",
                "--find-links",
                artifacts,
                "--no-deps",
                "--require-hashes",
                "-r",
                requirements,
            ]
        )
        source_parent = root / "source"
        source_parent.mkdir()
        with tarfile.open(artifacts / "sdk-source.tar.gz") as archive:
            archive.extractall(source_parent, filter="data")
        source = source_parent / ("claude-agent-sdk-python-" + SOURCE_REVISION)
        if not source.is_dir():
            raise RuntimeError("Source archive has an unexpected root")
        report["source"] = str(source)
        bundled = source / "src/claude_agent_sdk/_bundled"
        if any(p.name in {"claude", "claude.exe"} for p in bundled.iterdir()):
            raise RuntimeError("Source unexpectedly contains a CLI binary")
        output = root / "built-wheel"
        output.mkdir()
        run(
            [
                python,
                "-c",
                "from hatchling.build import build_wheel; print(build_wheel("
                + repr(str(output))
                + "))",
            ],
            cwd=source,
        )
        wheels = list(output.glob("*.whl"))
        if len(wheels) != 1:
            raise RuntimeError("Expected exactly one generated wheel")
        wheel = wheels[0]
        with zipfile.ZipFile(wheel) as archive:
            if any(
                n.endswith(("/_bundled/claude", "/_bundled/claude.exe"))
                for n in archive.namelist()
            ):
                raise RuntimeError("Generated wheel unexpectedly bundles a CLI")
            metadata = archive.read(
                next(n for n in archive.namelist() if n.endswith(".dist-info/METADATA"))
            ).decode()
        report["wheel"] = {
            "path": str(wheel),
            "sha256": digest(wheel),
            "metadata": metadata,
        }
        run(
            [
                args.uv,
                "pip",
                "install",
                "--python",
                python,
                "--no-index",
                "--no-deps",
                wheel,
            ]
        )
        after = json.loads(run([python, "-c", SNAPSHOT]))
        report["copied_after"] = after
        changes = {
            name: {
                "before": before["distributions"].get(name),
                "after": after["distributions"].get(name),
            }
            for name in before["distributions"].keys() | after["distributions"].keys()
            if before["distributions"].get(name, {}).get("version")
            != after["distributions"].get(name, {}).get("version")
        }
        report["version_changes"] = changes
        if set(changes) != {"claude-agent-sdk", "hatchling", "trove-classifiers"}:
            raise RuntimeError("Dependency changes exceed approved packages")
        expected = {
            "claude-agent-sdk": "0.2.162",
            "hatchling": "1.27.0",
            "trove-classifiers": "2026.6.1.19",
        }
        for name, version in expected.items():
            if after["distributions"][name]["version"] != version:
                raise RuntimeError("Unexpected approved dependency version")
        for name, data in before["distributions"].items():
            if (
                name != "claude-agent-sdk"
                and data["metadata_sha256"]
                != after["distributions"][name]["metadata_sha256"]
            ):
                raise RuntimeError("Retained dependency metadata changed")
        report["provenance"] = json.loads(run([python, "-c", PROVENANCE]))
        prov = report["provenance"]
        if isolated not in Path(prov["sdk_file"]).resolve().parents or not all(
            prov[k]
            for k in (
                "recover_pending_tool",
                "parallel_tool_recovery",
                "recovery_module",
            )
        ):
            raise RuntimeError("Experimental SDK provenance or API check failed")
        report["baseline_after"] = json.loads(run([original_python, "-c", SNAPSHOT]))
        if report["baseline_after"] != before or digest(cli) != CLI_HASH:
            raise RuntimeError(
                "Original environment changed during isolated installation"
            )
        report["isolated_python"] = str(python)
        report["status"] = "passed"
    except Exception as exc:
        report["status"] = "failed"
        report["error"] = type(exc).__name__ + ": " + str(exc)
        raise
    finally:
        save()
    print(
        json.dumps(
            {
                "status": report["status"],
                "isolated_python": report["isolated_python"],
                "source": report["source"],
                "cli": report["cli"],
                "wheel_sha256": report["wheel"]["sha256"],
                "record": str(root / "install-record.json"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
