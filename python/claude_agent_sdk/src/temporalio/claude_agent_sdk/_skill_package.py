"""Validate the finite project skill surface without interpreting skill instructions."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path


def package_inventory(directory: str) -> dict[str, str]:
    """Return file hashes after refusing links and alternate project configuration."""
    root = Path(directory)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Skill package requires a real .claude directory")
    if {path.name for path in root.iterdir()} != {"skills"}:
        raise ValueError("Skill package permits only the skills directory")
    inventory = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or not (path.is_dir() or path.is_file()):
            raise ValueError("Skill package rejects symlinks and special files")
        if path.is_file():
            inventory[path.relative_to(root).as_posix()] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    return inventory


def skill_metadata(text: str) -> dict[str, str]:
    """Accept only plain single line name and description frontmatter."""
    if "!`" in text:
        raise ValueError("Skill shell injection is unsupported")
    lines = text.splitlines()
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        raise ValueError("Skill requires bounded frontmatter")
    end = lines.index("---", 1)
    fields = {}
    for line in lines[1:end]:
        key, separator, value = line.partition(":")
        if key in {"hooks", "context", "allowed-tools"}:
            raise ValueError(f"Unsupported skill feature: {key}")
        if key not in {"name", "description"} or not separator or key in fields:
            raise ValueError(f"Unsupported skill frontmatter: {key}")
        value = value.strip()
        if not value or value[0] in "'\"[{|>&*!" or " #" in value:
            raise ValueError("Skill frontmatter requires plain single line scalars")
        fields[key] = value
    if set(fields) != {"name", "description"}:
        raise ValueError("Skill requires name and description")
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", fields["name"]):
        raise ValueError("Unsupported skill name")
    return fields


@dataclass(frozen=True)
class ValidatedSkillPackage:
    """A project package snapshot; every segment must verify the same bytes.

    Attributes:
        directory: Absolute .claude directory directly beneath the engine cwd.
        names: Exact model invocation names in the validated package.
        files: Relative file names and SHA256 hashes retained at validation.
    """

    directory: str
    names: tuple[str, ...]
    files: tuple[tuple[str, str], ...]

    @classmethod
    def validate(cls, cwd: str) -> ValidatedSkillPackage:
        """Validate a project skills tree and reject ancestor loading ambiguity."""
        workspace = Path(cwd).resolve(strict=True)
        for parent in workspace.parents:
            if (parent / ".claude").exists():
                raise ValueError("Ancestor project skill sources are unsupported")
            if (parent / ".git").exists():
                break
        directory = workspace / ".claude"
        files = package_inventory(str(directory))
        names = []
        for path in sorted((directory / "skills").iterdir()):
            if not path.is_dir() or not (path / "SKILL.md").is_file():
                raise ValueError("Each skill requires its own SKILL.md directory")
            fields = skill_metadata((path / "SKILL.md").read_text(encoding="utf-8"))
            if fields["name"] != path.name:
                raise ValueError("Skill name must match its directory")
            names.append(path.name)
        if not names:
            raise ValueError("Skill package is empty")
        return cls(str(directory), tuple(names), tuple(sorted(files.items())))

    def verify(self, cwd: str) -> None:
        """Refuse a changed package, loading root or forged validation snapshot."""
        current = type(self).validate(cwd)
        if current != self:
            raise ValueError("Validated skill package changed")

    def document(self) -> dict[str, object]:
        """Return the immutable package binding for the command hook."""
        return {
            "directory": self.directory,
            "names": list(self.names),
            "files": dict(self.files),
        }
