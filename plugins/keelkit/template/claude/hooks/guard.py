import json
import re
import subprocess
import sys
from pathlib import Path

# 기존 프로젝트에 같은 검사가 이미 있어서 끌 검사 (coauthor, env, protected, delete, noverify). keelkit:init 이 정한다.
DISABLED       = set()
QUOTED         = re.compile(r"\"[^\"]*\"|'[^']*'")
NO_VERIFY      = (
    re.compile(r"\bgit\b[^;&|]*\b(?:commit|push|merge)\b[^;&|]*--no-verify\b"),
    re.compile(r"\bgit\b[^;&|]*\bcommit\b[^;&|]*\s-[a-zA-Z]*n[a-zA-Z]*(?=\s|$)"),
    re.compile(r"\bgit\b[^;&|]*core\.hooksPath(?:=|\s+)(?!\.?/?\.githooks\b)"),
    re.compile(r"\bHUSKY=0\b"),
)
PROTECTED      = ("master", "main")
PROT           = r"(?:(?<![\w./-])|refs/heads/)(?:" + "|".join(PROTECTED) + r")(?![\w./-])"
ENV_FILE       = re.compile(r"(?:^|/)\.env(?:\.[^/]+)?$")
ENV_EXTRA      = re.compile(r"(?:^|[/\\])(?:\.env\.[^/\\]+|env\.(?:example|sample|template))$", re.I)
FEATURE_DELETE = (
    re.compile(r"^\s*git\s+branch\s+(?:-[dD]|--delete)\s+(?:feature/\S+\s*)+$"),
    re.compile(r"^\s*git\s+push\s+\S+\s+(?:--delete\s+)?(?::?feature/\S+\s*)+$"),
)
CMD_START      = r"(?:^|[;&|(`\s])"
DELETE_RULES   = [
    (CMD_START + r"(?:rm|rmdir|rd|unlink|del|erase|ri|shred|truncate|Remove-Item)(?=\s|$)", "파일 / 폴더 삭제"),
    (r"\bfind\b.*\s-delete\b", "파일 삭제 (find -delete)"),
    (r"\b(?:os\.remove|os\.unlink|shutil\.rmtree|\.unlink\(|fs\.rmSync|fs\.unlinkSync|rimraf)\b", "코드로 파일 삭제"),
    (r"\bgit\s+clean\b", "추적 안 되는 파일 삭제 (git clean)"),
    (r"\bgit\s+reset\s+--hard\b", "변경 되돌리기 (git reset --hard)"),
    (r"\bgit\s+stash\s+(?:drop|clear)\b", "stash 삭제"),
    (r"\bgit\s+(?:checkout\s+(?:--\s|\.(?:\s|$))|restore\b(?![^;&|]*--staged))", "작업 중 변경 되돌리기"),
    (r"\bgit\s+branch\b[^;&|]*\s(?:-[a-zA-Z]*[dD][a-zA-Z]*|--delete)\b", "브랜치 삭제"),
    (r"\bgit\s+tag\b[^;&|]*\s(?:-d|--delete)\b", "태그 삭제"),
    (r"\bgit\s+push\b[^;&|]*(?:--delete|\s-d\b|\s:\S)", "원격 브랜치 삭제"),
    (r"\bgit\s+push\b[^;&|]*(?:--force|\s-f\b)", "강제 push (원격 기록 덮어쓰기)"),
    (r"\bdocker\b[^;&|]*\b(?:rm|rmi|prune)\b", "컨테이너 / 이미지 / 볼륨 삭제"),
    (r"\bdocker[\s-]+compose\b[^;&|]*\bdown\b[^;&|]*(?:\s-v\b|--volumes)", "볼륨 삭제 (docker compose down -v)"),
    (r"\b(?:drop\s+(?:table|database|schema|index)|truncate\s+table|delete\s+from)\b", "DB 데이터 삭제"),
]


def git_out(args: list[str], cwd: str | None) -> str:
    """명령을 실행하고 표준 출력을 반환한다. 실패하면 빈 문자열을 반환한다.

    Args:
        args: 실행할 명령과 인자
        cwd: 실행 위치
    Returns:
        앞뒤 공백을 지운 표준 출력
    """
    try:
        return subprocess.run(args, cwd=cwd or None, capture_output=True, text=True, timeout=15).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def commit_message_texts(command: str) -> list[str]:
    """git commit 명령 문자열과 -F / --file 로 넘긴 메시지 파일 내용을 모은다.

    Args:
        command: 실행하려는 명령
    Returns:
        검사할 텍스트 목록
    """
    texts = [command]
    for path in re.findall(r"(?:-F|--file)[= ]\s*(?!-(?:\s|$))(\S+)", command):
        try:
            texts.append(Path(path.strip("'\"")).read_text("utf-8"))
        except OSError:
            pass
    return texts


def check_env(command: str, cwd: str | None) -> str | None:
    """.env 계열 파일을 add 하거나 커밋하려는 명령이면 이유를 반환한다.

    Args:
        command: 실행하려는 명령
        cwd: 실행 위치
    Returns:
        차단 이유. 해당하지 않으면 None
    """
    if "env" in DISABLED:
        return None
    reason = ".env 계열 파일은 커밋하지 않는다 (사용자 규칙). .gitignore 에 넣고 add 에서 뺀다."
    if re.search(r"\bgit\s+add\b[^;&|]*\.env\b", command):
        return reason
    if not re.search(r"\bgit\s+commit\b", command):
        return None
    names = git_out(["git", "diff", "--cached", "--name-only"], cwd).splitlines()
    if re.search(r"\bgit\s+commit\b[^;&|]*\s(?:-[a-zA-Z]*a[a-zA-Z]*|--all)\b", command):
        names += git_out(["git", "diff", "--name-only"], cwd).splitlines()
    return reason if any(ENV_FILE.search(n) for n in names) else None


def check_noverify(command: str) -> str | None:
    """git hook 을 건너뛰는 명령이면 이유를 반환한다. 따옴표 안의 글자는 보지 않는다.

    Args:
        command: 실행하려는 명령
    Returns:
        차단 이유. 해당하지 않으면 None
    """
    if "noverify" in DISABLED:
        return None
    bare = QUOTED.sub('""', command)
    if any(p.search(bare) for p in NO_VERIFY):
        return "git hook 을 건너뛰는 옵션(--no-verify, -n, core.hooksPath 변경, HUSKY=0)은 쓰지 않는다 (사용자 규칙). hook 이 막은 이유를 고친 뒤 다시 실행하세요."
    return None


def check_block(command: str, cwd: str | None) -> str | None:
    """차단할 명령이면 이유를 반환한다.

    Args:
        command: 실행하려는 명령
        cwd: 실행 위치
    Returns:
        차단 이유. 해당하지 않으면 None
    """
    if "coauthor" not in DISABLED and re.search(r"\bgit\b.*\bcommit\b", command) and any(re.search(r"co-authored-by", t, re.I) for t in commit_message_texts(command)):
        return "커밋 메시지에 Co-Authored-By 를 넣지 않는다 (사용자 규칙). 그 줄을 빼고 다시 커밋하세요."

    reason = check_noverify(command) or check_env(command, cwd)
    if reason:
        return reason

    if "protected" in DISABLED:
        return None

    if re.search(r"\bgit\b[^;&|]*\b(?:merge|push)\b", command):
        pushes_protected = re.search(r"\bgit\b[^;&|]*\bpush\b[^;&|]*" + PROT, command)
        switches_to      = re.search(r"\bgit\s+(?:checkout|switch)\s+(?:-\S+\s+)*" + PROT, command)
        switches_away    = re.search(r"\bgit\s+(?:checkout|switch)\b", command) and not switches_to
        on_protected     = not switches_away and git_out(["git", "branch", "--show-current"], cwd) in PROTECTED
        if pushes_protected or switches_to or on_protected:
            return "master / main 으로의 merge 와 push 는 하지 않는다 (사용자 규칙). 다른 브랜치에서 작업하고, 이 브랜치는 사용자가 직접 병합한다."

    if re.search(r"\bgh\s+pr\s+merge\b", command):
        number = re.search(r"\bgh\s+pr\s+merge\b.*?\s(\d+|https://\S+)", command)
        base   = git_out(["gh", "pr", "view", *([number.group(1)] if number else []), "--json", "baseRefName", "-q", ".baseRefName"], cwd)
        if base in PROTECTED or not base:
            return "이 PR 의 병합 대상이 master / main 이거나 확인할 수 없다. 병합은 하지 않는다 (사용자 규칙)."
    return None


def check_file(path: str) -> str | None:
    """.env 하나만 쓰므로 .env.example, .env.local 같은 파일을 만들려는 것이면 이유를 반환한다.

    Args:
        path: 쓰려는 파일 경로
    Returns:
        차단 이유. 해당하지 않으면 None
    """
    if "env" not in DISABLED and ENV_EXTRA.search(path):
        return ".env 하나만 쓴다 (사용자 규칙). .env.example, .env.local 같은 파일은 만들지 않는다. 키 설명은 docs 에 적는다."
    return None


def check_delete(command: str) -> str | None:
    """삭제 명령이면 확인을 요청할 사유를 반환한다. 병합 뒤 feature/ 브랜치 삭제는 제외한다.

    Args:
        command: 실행하려는 명령
    Returns:
        삭제 사유. 해당하지 않으면 None
    """
    if "delete" in DISABLED:
        return None
    for segment in re.split(r"[;&|\n]+", command):
        if any(p.search(segment) for p in FEATURE_DELETE):
            continue
        for pattern, label in DELETE_RULES:
            if re.search(pattern, segment, re.I):
                return label
    return None


def main() -> None:
    """hook 이벤트를 읽어 차단(exit 2)하거나 삭제 확인(ask)을 출력한다."""
    sys.stderr.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    event      = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    tool       = event.get("tool_name")
    tool_input = event.get("tool_input") or {}

    if tool in ("Write", "Edit", "MultiEdit"):
        reason = check_file(tool_input.get("file_path", ""))
        if reason:
            print(reason, file=sys.stderr)
            sys.exit(2)
        return

    command = tool_input.get("command", "")
    if tool not in ("Bash", "PowerShell") or not command:
        return

    reason = check_block(command, event.get("cwd"))
    if reason:
        print(reason, file=sys.stderr)
        sys.exit(2)

    label = check_delete(command)
    if label:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName"           : "PreToolUse",
            "permissionDecision"      : "ask",
            "permissionDecisionReason": f"삭제 확인: {label}",
        }}, ensure_ascii=False))


if __name__ == "__main__":
    main()
