{{shared}}

## Claude 전용 설정 (`.claude/`)

| 위치 | 내용 | 동작하는 때 |
|---|---|---|
| `hooks/guard.py` | Co-Authored-By 커밋, `.env*` 커밋, `.env.*` 파일 생성, master / main merge · push, `--no-verify` 차단 / 삭제 명령은 확인 요청 | Bash · PowerShell 실행 전, 파일 쓰기 전 (`settings.json`) |
| `hooks/strip_eof.py` | 파일 끝 빈 줄 제거 | 파일 저장 후 (`settings.json`) |
| `agents/runner` | 출력이 긴 테스트 · 빌드 실행, 요약만 반환 | 테스트 · 빌드를 돌릴 때 |
| `agents/reviewer` | `dev` 대비 변경을 읽기 전용으로 검토, 지적 사항만 반환 | 변경이 아주 큰 PR을 만들기 전 (파일 20개 이상 또는 500줄 이상) |
| `settings.json` | 권한과 hook 연결 | 세션 시작 |

규칙(`docs/rules/*`)은 위 표의 "읽는 때"에 열어서 읽는다. 자동으로 로드되지 않는다.
