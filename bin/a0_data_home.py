"""Resolve the task store published with Agent Base's live slot."""
import atexit
import fcntl
import json
import os
import re
import subprocess
from pathlib import Path


_locks = {}
atexit.register(lambda: [handle.close() for handle in _locks.values()])

def resolve_data_home():
    lock = Path.home() / ".local/state/a0/cutover.lock"
    lock.parent.mkdir(parents=True, exist_ok=True)
    if lock not in _locks:
        _locks[lock] = lock.open("a")
        fcntl.flock(_locks[lock], fcntl.LOCK_SH)
    explicit = os.environ.get("A0_DATA_HOME")
    if explicit:
        return Path(explicit).expanduser()
    home = Path.home()
    target = home / "SISO_Workspace/_data/worktrees/siso/main/agents/zero"
    receipt = home / ".local/state/agent-base/live/active.json"
    if receipt.is_file():
        active = json.loads(receipt.read_text())
        if active.get("a0DataHome") != str(target):
            return home / "SISO_Workspace/SISO_Agents/agent-zero/siso-agent-zero"
    return target


def resolve_agent_home(data=None, seat="agent-zero"):
    """Personal state is repo-scoped; the task store keeps its existing authority."""
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}", seat):
        raise ValueError("invalid agent name")
    selected = os.environ.get("SISO_AGENT_STATE_ROOT")
    if selected and not Path(selected).is_absolute():
        raise ValueError("agent state root must be absolute")
    root = Path(selected) if selected else Path(data) if data is not None else resolve_data_home()
    try:
        root = Path(subprocess.check_output(["git", "-C", str(root), "rev-parse", "--show-toplevel"],
                    stderr=subprocess.DEVNULL, text=True, timeout=3).strip())
    except (subprocess.SubprocessError, OSError):
        pass
    if root.name == "live" and root.parent.name == "siso":
        raise ValueError("live checkout requires SISO_AGENT_STATE_ROOT")
    target = root / ".agents/agents" / seat
    for path in (root / ".agents", root / ".agents/agents", target):
        if path.is_symlink():
            raise ValueError("symlinked state path")
    return target
