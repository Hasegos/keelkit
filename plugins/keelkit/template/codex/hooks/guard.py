import importlib.util
import json
import re
import sys
from pathlib import Path

PATCH_FILE = re.compile(r"^\*\*\* (?:Add File|Update File|Move to): (.+?)\s*$", re.M)


def load_guard(root: Path):
    """프로젝트의 .claude/hooks/guard.py 를 모듈로 불러온다. 검사 규칙은 그 파일 한 곳에만 둔다.

    Args:
        root: 프로젝트 루트
    Returns:
        guard 모듈. 파일이 없으면 None
    """
    path = root / ".claude" / "hooks" / "guard.py"
    if not path.is_file():
        return None
    spec   = importlib.util.spec_from_file_location("keelkit_guard", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def find_reason(guard, event: dict) -> str | None:
    """Codex 도구 호출을 guard.py 의 검사에 넣어 차단 이유를 얻는다.

    Args:
        guard: guard 모듈
        event: Codex hook 이벤트
    Returns:
        차단 이유. 해당하지 않으면 None
    """
    tool       = event.get("tool_name")
    tool_input = event.get("tool_input") or {}
    if tool == "Bash":
        return guard.check_block(tool_input.get("command", ""), event.get("cwd"))
    if tool == "apply_patch":
        for path in PATCH_FILE.findall(tool_input.get("command", "")):
            reason = guard.check_file(path)
            if reason:
                return reason
    return None


def main() -> None:
    """Codex PreToolUse 이벤트를 읽어 차단할 호출이면 JSON deny 를 출력한다. 이 Codex 는 exit 2 로는 막지 못한다. 삭제 확인(ask)은 지원하지 않아 하지 않는다."""
    sys.stdout.reconfigure(encoding="utf-8")
    event = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    guard = load_guard(Path(__file__).resolve().parents[2])
    if guard is None:
        return
    reason = find_reason(guard, event)
    if reason:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName"           : "PreToolUse",
            "permissionDecision"      : "deny",
            "permissionDecisionReason": reason,
        }}, ensure_ascii=False))


if __name__ == "__main__":
    main()
