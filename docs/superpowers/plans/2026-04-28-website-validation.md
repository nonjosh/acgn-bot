# Website Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Validate checker sites against GitHub Actions, identify hosted-only failures versus real site/parser breakage, and land precise test skips or checker fixes.

**Architecture:** Use a dedicated validation branch to trigger the existing `push`-based Python unit test workflow without changing CI semantics up front. For any failing checker tests, compare GitHub results with local reproduction and either add explicit skips for invalid/blocked sites or patch the affected checker when site structure has changed.

**Tech Stack:** Python 3.13, `uv`, `unittest`, GitHub Actions, GitHub CLI

---

### Task 1: Trigger hosted validation run

**Files:**
- Create: `docs/superpowers/specs/2026-04-28-website-validation-design.md`
- Create: `docs/superpowers/plans/2026-04-28-website-validation.md`
- Modify: none
- Test: `.github/workflows/python-test.yml`

- [ ] **Step 1: Commit the validation docs on the isolated branch**

```bash
git add docs/superpowers/specs/2026-04-28-website-validation-design.md docs/superpowers/plans/2026-04-28-website-validation.md
git commit -m "docs: add website validation plan"
```

- [ ] **Step 2: Push the isolated branch**

```bash
git push -u origin ci-website-validation
```

- [ ] **Step 3: Inspect the hosted Python test workflow**

```bash
gh run list --workflow python-test.yml --branch ci-website-validation --limit 5
gh run view <run-id> --log-failed
```

Expected: either the workflow passes, or failing checker tests are identified from the hosted run logs.

### Task 2: Classify hosted failures

**Files:**
- Modify: `tests/test_checkers.py`
- Modify: checker modules only if a live schema change is confirmed
- Test: `tests/test_checkers.py`

- [ ] **Step 1: Reproduce each hosted failure locally**

```bash
uv run python -m unittest tests.test_checkers.TestCheckers.<failing_test_name>
```

Expected: determine whether the failure reproduces locally.

- [ ] **Step 2: Decide the remediation path**

```text
GitHub fails + local passes => hosted-IP / hosted-network restriction => skip test with explicit reason
GitHub fails + local fails because site unavailable/protected => skip test with explicit reason
GitHub fails + local fails because parser broke on changed markup/schema => patch checker and keep test enabled
```

- [ ] **Step 3: Capture only directly supported reasons**

```python
@unittest.skip("GitHub Actions IP appears blocked by <site>; local requests still succeed")
def test_example_checker(self) -> None:
    ...
```

Expected: skip reasons are concrete and evidence-based.

### Task 3: Implement minimal fixes

**Files:**
- Modify: `tests/test_checkers.py`
- Modify: `helpers/checkers/*.py` only for confirmed schema changes
- Test: `tests/test_checkers.py`
- Test: any checker-specific regression tests needed by touched checker

- [ ] **Step 1: Write or update the failing regression coverage first when a checker schema changed**

```python
def test_example_checker_schema_change(self) -> None:
    checker = checkers.ExampleChecker("https://example.com/series")
    chapter_list = checker.get_latest_chapter_list()
    self.assertGreater(len(chapter_list), 0)
```

- [ ] **Step 2: Apply the smallest code change that matches the observed site response**

```python
# Update selector / parsing path only where the live response proves the old schema changed.
```

- [ ] **Step 3: Re-run the affected local tests**

```bash
uv run python -m unittest tests.test_checkers
```

Expected: affected tests pass locally, with only intentional skips remaining.

### Task 4: Land the validation outcome

**Files:**
- Modify: whatever changed in Tasks 2-3
- Test: full suite

- [ ] **Step 1: Run the full test suite**

```bash
uv run python -m unittest
```

Expected: suite passes with explicit intentional skips only.

- [ ] **Step 2: Push the fixes**

```bash
git push
```

- [ ] **Step 3: Open a PR for the resulting branch**

```bash
gh pr create --base develop --head ci-website-validation --title "<fill from actual outcome>" --body "<summarize hosted failures, local reproduction, and fixes/skips>"
```

Expected: PR is open with a clear explanation of what was skipped or fixed.
