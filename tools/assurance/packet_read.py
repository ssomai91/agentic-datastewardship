"""DC-2 packet-scoped read (stand-in): a MECHANICAL path guard.

Contract (Build Preconditions, DC-2): Read bound at tool level to the packet only; any other path fails mechanically.

WHAT THIS IS NOT. This module guards reads made through it. It does not bind the Read tool of a Claude subagent, which can still read
any file its session allows. Until the agent's tool permissions are restricted to the packet directory (for example with a Claude Code
permission rule or a PreToolUse hook, which is a settings change that needs the owner's go-ahead), a run of the Assurance Reviewer is
scoped to the packet by INSTRUCTION ONLY. Do not treat DC-2 as built.
"""
import json
from pathlib import Path


class PacketAccessError(PermissionError):
    """A read outside the packet, or of an item the manifest does not list."""


class PacketReader:
    def __init__(self, root):
        self.root = Path(root).resolve()
        manifest = json.loads((self.root / "manifest.json").read_text(encoding="utf-8"))
        self.allowed = {i["path"] for i in manifest["items"]} | {"manifest.json"}
        self.calls = []

    def read(self, relative_path):
        self.calls.append(relative_path)
        p = Path(relative_path)
        if p.is_absolute() or ".." in p.parts or relative_path.startswith(("/", "\\")):
            raise PacketAccessError(f"outside the packet: {relative_path}")
        norm = p.as_posix()
        if norm not in self.allowed:
            raise PacketAccessError(f"not listed in the manifest: {relative_path}")
        target = (self.root / norm).resolve()
        if self.root not in target.parents and target != self.root:
            raise PacketAccessError(f"resolves outside the packet: {relative_path}")  # catches symlinks
        return target.read_text(encoding="utf-8")