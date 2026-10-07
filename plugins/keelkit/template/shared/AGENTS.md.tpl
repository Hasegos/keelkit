# {{name}}

{{one_line}}

- 스택: {{stack}}
- 저장소: {{repo}} (기준 브랜치 `dev`)
- 상태: 초기 설정 ({{today}}). `미정` 항목이 있으면 0번을 먼저 한다

## 0. 미정 항목 채우기

이 문서나 `docs/`에 `미정`이 남아 있으면 작업을 시작하기 전에 `harness` skill 1번 절차로 채운다. 알 수 있는 것은 코드에서 읽고, 못 읽는 것만 사용자에게 한 번에 묻는다. 채운 뒤 이 절을 지운다.

## 자주 쓰는 명령

```bash
{{run_cmds}}
```

## 규칙과 절차

| 위치 | 내용 | 읽는 때 |
|---|---|---|
| `docs/rules/workflow.md` | 진행 방식(묻지 않고 진행, 삭제는 확인, master / main 제외), 압축(compact) 규칙 | 항상 |
| `docs/rules/code.md` | 구조, 같이 고칠 문서 | 코드 파일을 만질 때 |
| `docs/rules/style.md` | 주석(언어별 표준 문서 주석, 번호 박스 헤더는 선택) | 코드 파일을 만질 때 |
| `docs/rules/docs.md` | 원본 문서 표, 문서 쓰는 방식 | 문서를 만질 때 |
{{delegation_row}}
| skill `harness` | 설정 채우기, 규칙 · 절차 · 금지 사항 추가 · 변경 | `미정`이 있을 때, 설정 변경을 요청할 때 |
| skill `verify` | 검증과 체크리스트 절차 | 구현을 마쳤을 때 |
| skill `commit-pr` | `dev` 기준 브랜치, 커밋, PR(`gh`), squash 병합, 브랜치 삭제 | 커밋할 때 |

{{skills_note}}

## 문서

| 문서 | 내용 |
|---|---|
| `docs/ROADMAP.md` | 목적, 핵심 흐름, 진행 상황, 결정 기록 |
| `docs/ARCHITECTURE.md` | 구조, 데이터, 설계 결정과 근거 |
| `docs/SETUP.md` | 준비물, 실행 방법, `.env` 키 이름과 설명 |

## 진행 상황

세부 원본은 `docs/ROADMAP.md` 2번.

- [ ] {{first_step|미정}}

## 다음 할 일

1. 미정
