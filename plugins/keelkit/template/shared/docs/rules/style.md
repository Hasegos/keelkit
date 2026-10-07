# 주석 규칙

주석은 클래스와 함수(메서드) 단위로만 쓴다. 그 안쪽 코드에는 쓰지 않는다.

## 1. 문서 주석 (기본)

각 언어의 표준 문서 주석 형식으로 간략하게 쓴다.

| 언어 | 형식 |
|---|---|
| Java, Kotlin | Javadoc / KDoc: `/** */`, `@param`, `@return` |
| Python | docstring `""" """`, Google 스타일 `Args:`, `Returns:` |
| TypeScript, JavaScript (React 포함) | JSDoc: `/** */`, `@param 이름 설명`, `@returns 설명` (타입은 시그니처에 있으므로 쓰지 않는다) |
| C# | XML 문서: `/// <summary>`, `<param>`, `<returns>` |
| Go | 이름으로 시작하는 `//` 한 문장 |
| Rust | `///` |
| Swift | `///`, `- Parameter`, `- Returns` |
| PHP, Ruby | PHPDoc, YARD |

- 이 표는 기본값이다. 프로젝트에서 바꾸라고 하면 고치고, 프로젝트에서 쓰는 언어의 줄만 남긴다.
- 요약은 한두 줄, "~한다." 체. 무엇을 하는지와 알아야 할 동작(트랜잭션, 부작용)만 적는다.
- 파라미터와 반환은 한 줄씩. 없으면 그 줄은 쓰지 않는다. 던지는 예외가 있으면 한 줄.

```java
/**
 * 메모를 저장한다. 제목/본문의 앞뒤 공백은 제거한다.
 * 저장 트랜잭션이 커밋되면 로컬 LLM 요약이 비동기로 시작된다.
 *
 * @param userId  작성자 회원 ID
 * @param request 메모 작성 요청
 * @return 저장된 메모
 */
public Memo save(long userId, MemoRequest request) {
```

```python
def save(user_id: int, request: MemoRequest) -> Memo:
    """메모를 저장한다. 제목/본문의 앞뒤 공백은 제거한다.

    Args:
        user_id: 작성자 회원 ID
        request: 메모 작성 요청
    Returns:
        저장된 메모
    """
```

## 2. 번호 박스 헤더 (선택)

어느 언어의 표준 규약도 아니므로 기본값은 쓰지 않는다. 프로젝트가 켜면 클래스와 함수(메서드) 위에 하나씩 두고, 문서 주석은 그 바로 아래에 둔다.

켠 언어: 없음

- 선 길이는 제목에 맞춘다. 주석 기호는 언어에 맞춘다 (`#`, `//`).
- 클래스는 `1.`, `2.` 순서로 번호를 붙이고, 그 안의 메서드는 `1-1.`, `1-2.`로 붙인다.
- 제목은 무엇을 하는지만 짧게 쓴다.

```
# ─────────────────────
# 2. 삭제 확인 규칙
# ─────────────────────
```

## 3. 프론트엔드 (TypeScript, JavaScript, React)

- React 컴포넌트와 훅도 함수이므로 같은 방식으로 함수 단위에만 JSDoc을 쓴다. 클래스가 있으면 클래스 단위에도 쓴다.
- props와 반환 타입은 시그니처가 말해주므로 요약 한 줄만 쓰고, `@param`은 의미가 타입으로 드러나지 않을 때만 쓴다.
- JSX 안의 주석(`{/* */}`)은 쓰지 않는다. 타입, 인터페이스, 상수에도 쓰지 않는다.

```tsx
/**
 * 메모 목록을 보여준다. 항목을 누르면 상세 화면으로 이동한다.
 *
 * @param props.onSelect 항목 선택 시 호출, 선택한 메모 ID를 받는다
 */
export function MemoList({ memos, onSelect }: MemoListProps) {
```

## 4. 쓰지 않는 것

- 필드, 상수, 지역 변수, 함수 안 코드에 다는 주석
- 한 줄 주석(`# 설명`, `// 설명`), 줄 끝 주석, TODO 주석
- 예외는 도구 지시어(`# noqa`, `// eslint-disable`, `@SuppressWarnings` 등)와, 2번에서 켠 언어의 박스 헤더뿐이다.

이유와 설계는 코드가 아니라 `docs/`에 적는다.