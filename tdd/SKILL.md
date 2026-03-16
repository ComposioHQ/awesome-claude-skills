---
name: tdd
description: Guide test-driven development (TDD) workflows — write failing tests first, then implement code to make them pass. Use this skill when the user wants to practice TDD, write tests before code, or build features using the red-green-refactor cycle.
---

# Test-Driven Development (TDD)

Guide development using the TDD cycle: Red → Green → Refactor.

## TDD Cycle

```
Red    → Write a failing test that defines desired behavior
Green  → Write the minimal code to make the test pass
Refactor → Clean up code while keeping tests green
```

Each cycle should be small — a few minutes per iteration. Never skip the Red phase.

## Step 1: Red — Write a Failing Test

Before writing any implementation code:

1. **Define the behavior** — what should this unit do?
2. **Write a test** that asserts that behavior
3. **Run the test** — confirm it fails (not errors — fails)
4. If the test passes without implementation, the test is wrong or already covered

A good test:
- Tests one behavior (single assertion or related assertions)
- Has a descriptive name: `test_returns_error_when_input_is_empty`
- Is fast and isolated — no external dependencies (use mocks/stubs)
- Is deterministic — same result every run

**Test naming pattern:** `test_[unit]_[scenario]_[expected_result]`

## Step 2: Green — Write Minimal Implementation

Write the **simplest possible code** to make the test pass:
- Don't over-engineer
- Don't add features not covered by a test
- It's okay to write ugly code here — refactor comes next
- Return hardcoded values if that makes the test pass initially (triangulation)

Run the test — confirm it passes. If other tests break, fix them.

## Step 3: Refactor — Clean Without Breaking

Now improve the code:
- Remove duplication
- Improve naming
- Simplify logic
- Apply patterns and abstractions
- Run tests after every change — if they break, undo and try again

## When to Write Tests

TDD applies to:
- New features (write test first, always)
- Bug fixes (write a failing test that reproduces the bug, then fix it)
- Refactoring (tests provide safety net)

## Test Structure: Arrange-Act-Assert (AAA)

```python
def test_add_two_numbers():
    # Arrange
    calculator = Calculator()

    # Act
    result = calculator.add(2, 3)

    # Assert
    assert result == 5
```

## Mocking and Isolation

Tests should be isolated from external dependencies:

**JavaScript (Jest):**
```js
jest.mock('./api', () => ({
  fetchUser: jest.fn().mockResolvedValue({ id: 1, name: 'Alice' })
}));
```

**Python (unittest.mock):**
```python
from unittest.mock import patch, MagicMock

@patch('module.requests.get')
def test_fetch_user(mock_get):
    mock_get.return_value.json.return_value = {'id': 1}
    result = fetch_user(1)
    assert result['id'] == 1
```

## TDD Workflow with Claude

When building a feature with TDD:

1. **Describe the feature** — Claude will help identify testable units
2. **Write the first test** — Claude generates a failing test
3. **Run the test** — confirm it fails
4. **Write minimal implementation** — Claude writes just enough code
5. **Run tests** — confirm passing
6. **Refactor** — Claude suggests improvements
7. **Repeat** for the next behavior

## Test Organization

```
src/
  feature/
    feature.js
    feature.test.js    # co-located with source
tests/
  unit/               # or organized by type
  integration/
  e2e/
```

## Common TDD Pitfalls

- **Writing tests after code** — this is not TDD, just testing
- **Tests that never fail** — always verify the red phase
- **Testing implementation details** — test behavior, not internals
- **Slow tests** — slow tests kill the TDD rhythm; mock I/O
- **Giant test methods** — one test per behavior
- **Skipping refactor phase** — green without refactor accumulates debt

## Notes for Claude

- Always start with the test file, never the implementation
- Generate tests that are specific about inputs and outputs
- After green, actively look for duplication and suggest refactors
- If the user writes tests after code, gently redirect to the TDD approach for future work
