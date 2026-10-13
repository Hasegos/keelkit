# keelkit

> 어떤 프로젝트든 같은 뼈대로 시작한다. 폴더를 열고 `/keelkit:init` 한 줄이면 `CLAUDE.md`, `AGENTS.md`, `.claude/`, `.agents/`, `docs/`가 깔리고 AI 도구가 프로젝트를 읽어서 채운다.

Claude Code와 Codex에서 같이 쓰는 플러그인. 어느 쪽에서 `init`을 돌려도 결과가 같고, 특정 언어나 프레임워크에 묶이지 않는다.

## 설치

```bash
/plugin marketplace add Hasegos/keelkit
/plugin install keelkit@keelkit
```

프로젝트 폴더를 새 세션으로 열고 실행한다.

```bash
/keelkit:init
```

hook과 권한은 새 세션부터 적용된다.

### Codex에서 설치

같은 저장소가 Codex 플러그인도 겸한다 (`.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`). `init` skill은 Claude와 같은 파일을 쓴다.

```bash
codex plugin marketplace add Hasegos/keelkit
```

Codex에서 keelkit 플러그인을 설치하고 프로젝트 폴더를 연 뒤 "이 폴더에 keelkit init 해줘"라고 말한다. `$init`으로 직접 부를 수도 있다. `.codex/hooks`가 master 보호, `.env`, `--no-verify` 등을 막지만, Codex에서 프로젝트와 hook을 신뢰(`/hooks`)해야 켜진다. 신뢰 전에는 경고 없이 꺼져 있다. 삭제 확인은 문장으로만 지켜진다.

## Claude와 Codex 둘 다

도구를 고르는 질문은 없다. 항상 둘 다 설치하고, 어느 쪽에서 실행해도 같다.

- 규칙 원본은 `docs/rules/`, 공통 지침 원본은 `AGENTS.md` 한 곳이다. `CLAUDE.md`는 `@AGENTS.md`로 그것을 가져온다. 도구를 바꿔도 내용이 같다.
- skill은 `.claude/skills/`와 `.agents/skills/`에 같은 내용으로 복사된다. 한쪽을 고치면 다른 쪽도 같이 고친다.
- hook(`guard.py`)은 Claude 전용이다. Codex는 같은 규칙을 문장으로만 지킨다.
- Claude에서 Codex 플러그인(`/codex:rescue`)으로 작업을 그때그때 맡길 수 있다. keelkit은 이 위임을 설치하거나 규칙으로 정하지 않는다.

## 무엇이 깔리나

```
my-project/
├─ AGENTS.md                 공통 지침: 소개, 명령, 규칙 표 (Claude와 Codex가 읽음)
├─ CLAUDE.md                 @AGENTS.md + Claude 전용 설정 지도
├─ docs/
│  ├─ rules/                 진행 방식, 코드, 주석, 문서 규칙
│  ├─ ROADMAP.md             목적, 진행 상황, 결정 기록
│  ├─ ARCHITECTURE.md        구조와 설계 근거
│  └─ SETUP.md               실행법, .env 키 이름
├─ .agents/skills/           Codex용 skill (.claude/skills/와 같은 내용)
├─ .codex/                   Codex hook: hooks.json + guard.py (.claude/hooks/guard.py의 규칙을 사용)
└─ .claude/
   ├─ settings.json          권한 + hook 연결
   ├─ skills/                harness(설정 채우기 · 변경), verify, commit-pr
   ├─ agents/                runner(긴 출력 요약), reviewer(큰 PR 검토)
   └─ hooks/                 guard.py, strip_eof.py
```

설치 뒤 Claude가 코드와 기존 문서를 읽고 목적, 스택, 실행 명령을 채운다. 읽어서 알 수 없는 것만 한 번에 묻는다.

## 기존 프로젝트에 붙일 때

기존 파일은 지우거나 덮어쓰지 않는다. 파일 이름이 아니라 **기능** 단위로 겹침을 먼저 확인하고, 설치 전에 한 번만 묻는다.

1. Claude가 기존 `CLAUDE.md`, `.claude/`, hook, `.husky` 등을 읽고 keelkit의 기능 16개와 대조한다.
2. 기능마다 번호를 붙인 표로 보여준다: 겹침 · 내용 다름, 겹침 · 내용 같음, 없음.
3. 기본값은 **기존 유지**다. 바꿀 번호만 말하면 된다 (예: "1번, 3번 keelkit으로". 없으면 "그대로").
4. 겹치지 않는 기능만 설치한다. 기존을 지우는 선택은 한 번 더 확인하고 백업을 남긴다.

| 상황 | 처리 |
|---|---|
| 같은 기능이 없음 | keelkit을 설치한다 |
| 같은 기능이 있음 | 기존을 유지하고 keelkit 쪽은 설치하지 않는다 |
| `.claude/settings.json` | 기존 권한과 hook은 유지하고 keelkit 것만 추가한다 |
| `guard.py`의 검사 중 일부가 겹침 | 그 검사만 끈다. 기존 hook 코드는 건드리지 않는다 |

- `.gitignore`에는 `.env`, `.keel-backup/`과 keelkit이 설치하는 경로를 추가한다: `docs/`, `CLAUDE.md`, `.claude/`, `AGENTS.md`, `.agents/`, `.codex/`. `git init` 전이라 `.gitignore`가 없어도 만든다.
- 이미 git이 추적 중인 경로는 넣지 않고 알린다. 설정 파일을 저장소에 올리고 싶으면 `.gitignore`에서 그 줄을 지운다.
- 합친 결과를 확인한 뒤 `.keel-backup/`은 직접 지운다.

## guard hook이 막는 것

부탁이 아니라 동작으로 막는다. Claude 전용이다.

| 상황 | 동작 |
|---|---|
| `master` / `main`에 merge, push, PR 병합 | 차단. 원격에 브랜치가 하나도 없을 때의 첫 push(`master` 만들기)만 통과 |
| 커밋 메시지에 `Co-Authored-By` | 차단 |
| `.env` 커밋, `.env.*` 파일 생성 | 차단 |
| `--no-verify`, `git commit -n`, `core.hooksPath` 변경, `HUSKY=0` | 차단 |
| 파일, 폴더, 브랜치, 태그, 컨테이너 삭제, 강제 push | 사용자에게 확인 요청 |
| `feature/` 브랜치 삭제 | 자동 허용 |
| `master` / `main` / `dev` 브랜치 삭제 | 차단 |

## 기본 진행 규칙

- 파일을 고치기 전에 파일마다 한 줄 계획(무엇을, 근거)을 말하고 사용자 답을 받은 뒤 진행한다. 승인 뒤의 실행, 브랜치, 커밋, push, PR은 묻지 않는다. 변경 뒤에는 모두 검수하고 파일마다 한 줄로 보고한다 (큰 변경은 `reviewer` agent).
- 기준 브랜치는 `dev`, 작업 브랜치는 `feature/<기능>`. 원격이 비어 있으면 빈 커밋으로 `master`를 먼저 만들고 `dev`, `feature/<기능>` 순서로 간다.
- 커밋은 `ADD` / `FIX` / `DELETE <대상> 추가/수정/삭제`.
- PR은 `gh`로 만들고 squash 병합한다. `master` / `main` 병합은 사용자가 직접 한다.
- `.env`는 한 개만 쓴다. 키 이름만 `docs/SETUP.md`에 적고 값은 적지 않는다.
- 주석은 클래스 · 함수 단위에만, 언어 표준 문서 주석(Javadoc, docstring, JSDoc 등)으로 쓴다.

기본값을 바꾸려면 Claude에게 "이 규칙 바꿔줘"라고 말한다. `harness` skill이 알맞은 파일을 찾아서 고친다.

## 요구 사항

- Claude Code
- Python 3 (`python` 또는 `python3`)
- git
- 선택: `gh` (PR 생성 · 병합). 없으면 설치와 `gh auth login`을 안내하고 PR 단계는 보류한다.

## 자주 묻는 것

| 질문 | 답 |
|---|---|
| 일부만 쓸 수 있나? | 설치 뒤 필요 없는 파일을 지우면 된다. |
| 플러그인을 업데이트하면? | `/keelkit:init`을 다시 실행한다. 이미 채운 파일은 덮어쓰지 않고 "직접 합쳐야 함"으로만 보고하며 백업이 남는다. |
| hook이 동작하지 않는다 | 새 세션에서 열었는지, `python`이 PATH에 있는지 확인한다. |

## 라이선스

MIT
