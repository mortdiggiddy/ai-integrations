"""Verify experimental SDK wheel, installation, source and baseline identities."""

import argparse
import base64
import csv
import hashlib
import importlib.metadata
import io
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

SNAPSHOT = r"""
import hashlib,importlib.metadata,json,sys
out={"prefix":sys.prefix,"python":sys.version,"distributions":{}}
for d in importlib.metadata.distributions():
 name=d.metadata["Name"].lower().replace("_","-")
 out["distributions"][name]={"version":d.version,"metadata_sha256":hashlib.sha256(d.read_text("METADATA").encode()).hexdigest(),"path":str(d._path)}
print(json.dumps(out,sort_keys=True))
"""


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def encoded_hash(data):
    return base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    record = json.loads((root / "install-record.json").read_text())
    require(record["status"] == "passed", "Installation did not pass")
    require(Path(sys.prefix).resolve() == root / "venv", "Wrong Python environment")
    wheel = Path(record["wheel"]["path"])
    require(root in wheel.resolve().parents, "Wheel escapes disposable root")
    require(
        hashlib.sha256(wheel.read_bytes()).hexdigest() == record["wheel"]["sha256"],
        "Wheel hash differs",
    )
    for artifact in record["downloads"]:
        actual = hashlib.sha256(
            (root / "artifacts" / artifact["name"]).read_bytes()
        ).hexdigest()
        require(
            actual == artifact["sha256"] == artifact["actual_sha256"],
            "Approved artifact changed",
        )
    cli = Path(record["cli"]["path"])
    require(
        hashlib.sha256(cli.read_bytes()).hexdigest() == record["cli"]["sha256"],
        "Original CLI changed",
    )
    dist = importlib.metadata.distribution("claude-agent-sdk")
    site = Path(dist.locate_file(""))
    require(dist.version == "0.2.162", "Wrong SDK version")
    require(
        root / "venv" in Path(dist._path).resolve().parents,
        "SDK distribution escapes environment",
    )
    wheel_verified = []
    with zipfile.ZipFile(wheel) as archive:
        name = next(n for n in archive.namelist() if n.endswith(".dist-info/RECORD"))
        for name, expected, size in csv.reader(
            io.StringIO(archive.read(name).decode())
        ):
            if not expected:
                continue
            algorithm, value = expected.split("=", 1)
            require(algorithm == "sha256", "Unexpected wheel hash algorithm")
            data = archive.read(name)
            require(
                encoded_hash(data) == value and len(data) == int(size),
                "Wheel RECORD differs",
            )
            installed = site / name
            require(
                root / "venv" in installed.resolve().parents,
                "SDK file escapes environment",
            )
            require(
                installed.read_bytes() == data,
                "Installed SDK differs from wheel: " + name,
            )
            wheel_verified.append(name)
    installed_verified = []
    for name, expected, size in csv.reader(io.StringIO(dist.read_text("RECORD"))):
        if not expected:
            continue
        algorithm, value = expected.split("=", 1)
        require(algorithm == "sha256", "Unexpected installed hash algorithm")
        target = Path(dist.locate_file(name))
        require(
            root / "venv" in target.resolve().parents,
            "Installed record escapes environment",
        )
        data = target.read_bytes()
        require(
            encoded_hash(data) == value and len(data) == int(size),
            "Installed RECORD differs: " + name,
        )
        installed_verified.append(name)
    source = Path(record["source"]) / "src"
    require(root in source.resolve().parents, "Source escapes disposable root")
    source_verified = []
    for name in wheel_verified:
        if name.startswith("claude_agent_sdk/") and (source / name).is_file():
            require(
                (source / name).read_bytes() == (site / name).read_bytes(),
                "SDK differs from source: " + name,
            )
            source_verified.append(name)
    require(
        "claude_agent_sdk/_internal/main_agent_recovery.py" in source_verified,
        "Recovery source not verified",
    )
    direct_url = json.loads(dist.read_text("direct_url.json"))
    require(
        not direct_url.get("dir_info", {}).get("editable", False), "SDK is editable"
    )
    require(direct_url["url"] == wheel.as_uri(), "SDK install URL differs")
    require(
        record["baseline_before"] == record["baseline_after"],
        "Baseline snapshot changed during install",
    )
    baseline_python = Path(record["baseline_before"]["prefix"]) / "bin/python"
    env = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "PYTHONHOME"}}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    current_baseline = json.loads(
        subprocess.check_output(
            [str(baseline_python), "-c", SNAPSHOT], text=True, env=env
        )
    )
    require(
        current_baseline == record["baseline_before"],
        "Baseline distribution identity changed",
    )
    expected = {
        "claude-agent-sdk": "0.2.162",
        "hatchling": "1.27.0",
        "trove-classifiers": "2026.6.1.19",
    }
    before = record["baseline_before"]["distributions"]
    current = {
        d.metadata["Name"].lower().replace("_", "-"): d
        for d in importlib.metadata.distributions()
    }
    require(
        set(current) == set(before) | set(expected),
        "Unexpected package additions/removals",
    )
    for name, d in current.items():
        require(
            root / "venv" in Path(d._path).resolve().parents,
            "Distribution escapes environment: " + name,
        )
        require(
            d.version == expected.get(name, before.get(name, {}).get("version")),
            "Unexpected version: " + name,
        )
        if name not in expected:
            require(
                hashlib.sha256(d.read_text("METADATA").encode()).hexdigest()
                == before[name]["metadata_sha256"],
                "Retained metadata differs: " + name,
            )
    result = {
        "status": "passed",
        "prefix": sys.prefix,
        "sdk_version": dist.version,
        "wheel_sha256": record["wheel"]["sha256"],
        "wheel_members_verified": wheel_verified,
        "installed_record_entries_verified": installed_verified,
        "source_package_files_verified": source_verified,
        "direct_url": direct_url,
        "direct_url_hash_provided": bool(
            direct_url.get("archive_info", {}).get("hashes")
        ),
        "baseline_distribution_snapshot_unchanged": True,
        "baseline_distribution_snapshot_rechecked": True,
        "approved_artifacts_rechecked": True,
        "isolated_dependency_versions_rechecked": True,
    }
    if args.output:
        require(not args.output.exists(), "Output already exists")
        args.output.write_text(json.dumps(result, indent=2))
    print(
        json.dumps(
            {k: len(v) if isinstance(v, list) else v for k, v in result.items()},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
