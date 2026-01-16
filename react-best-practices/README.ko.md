# React Best Practices

[English](README.md) | **한국어** | [中文](README.zh.md) | [日本語](README.ja.md)

---

에이전트와 LLM에 최적화된 React 모범 사례를 생성하고 유지하기 위한 구조화된 저장소입니다.

## 구조

- `rules/` - 개별 규칙 파일 (규칙당 하나)
  - `_sections.md` - 섹션 메타데이터 (제목, 영향도, 설명)
  - `_template.md` - 새 규칙 생성을 위한 템플릿
  - `area-description.md` - 개별 규칙 파일
- `src/` - 빌드 스크립트 및 유틸리티
- `metadata.json` - 문서 메타데이터 (버전, 조직, 요약)
- __`AGENTS.md`__ - 컴파일된 출력 (생성됨)
- __`test-cases.json`__ - LLM 평가를 위한 테스트 케이스 (생성됨)

## 시작하기

1. 의존성 설치:
   ```bash
   pnpm install
   ```

2. 규칙에서 AGENTS.md 빌드:
   ```bash
   pnpm build
   ```

3. 규칙 파일 유효성 검사:
   ```bash
   pnpm validate
   ```

4. 테스트 케이스 추출:
   ```bash
   pnpm extract-tests
   ```

## 새 규칙 만들기

1. `rules/_template.md`를 `rules/area-description.md`로 복사
2. 적절한 영역 접두사 선택:
   - `async-` - 워터폴 제거 (섹션 1)
   - `bundle-` - 번들 크기 최적화 (섹션 2)
   - `server-` - 서버 사이드 성능 (섹션 3)
   - `client-` - 클라이언트 사이드 데이터 페칭 (섹션 4)
   - `rerender-` - 리렌더 최적화 (섹션 5)
   - `rendering-` - 렌더링 성능 (섹션 6)
   - `js-` - JavaScript 성능 (섹션 7)
   - `advanced-` - 고급 패턴 (섹션 8)
3. 프론트매터와 내용 작성
4. 명확한 예제와 설명 포함
5. `pnpm build`를 실행하여 AGENTS.md와 test-cases.json 재생성

## 규칙 파일 구조

각 규칙 파일은 다음 구조를 따라야 합니다:

```markdown
---
title: 규칙 제목
impact: MEDIUM
impactDescription: 선택적 설명
tags: 태그1, 태그2, 태그3
---

## 규칙 제목

규칙과 중요성에 대한 간략한 설명.

**잘못된 예 (무엇이 잘못되었는지 설명):**

```typescript
// 나쁜 코드 예제
```

**올바른 예 (무엇이 올바른지 설명):**

```typescript
// 좋은 코드 예제
```

예제 후 선택적 설명 텍스트.

참조: [링크](https://example.com)

## 파일 명명 규칙

- `_`로 시작하는 파일은 특수 파일 (빌드에서 제외)
- 규칙 파일: `area-description.md` (예: `async-parallel.md`)
- 섹션은 파일명 접두사에서 자동으로 유추됨
- 규칙은 각 섹션 내에서 제목별로 알파벳순 정렬
- ID (예: 1.1, 1.2)는 빌드 시 자동 생성

## 영향도 수준

- `CRITICAL` - 최우선 순위, 주요 성능 향상
- `HIGH` - 상당한 성능 개선
- `MEDIUM-HIGH` - 중상 수준의 향상
- `MEDIUM` - 보통 수준의 성능 개선
- `LOW-MEDIUM` - 중하 수준의 향상
- `LOW` - 점진적 개선

## 스크립트

- `pnpm build` - 규칙을 AGENTS.md로 컴파일
- `pnpm validate` - 모든 규칙 파일 유효성 검사
- `pnpm extract-tests` - LLM 평가용 테스트 케이스 추출
- `pnpm dev` - 빌드 및 유효성 검사

## 기여하기

규칙을 추가하거나 수정할 때:

1. 섹션에 맞는 올바른 파일명 접두사 사용
2. `_template.md` 구조 따르기
3. 명확한 잘못된/올바른 예제와 설명 포함
4. 적절한 태그 추가
5. `pnpm build`를 실행하여 AGENTS.md와 test-cases.json 재생성
6. 규칙은 제목별로 자동 정렬됨 - 번호 관리 불필요!

## 감사의 말

원래 [Vercel](https://vercel.com)의 [@shuding](https://x.com/shuding)이 작성했습니다.
