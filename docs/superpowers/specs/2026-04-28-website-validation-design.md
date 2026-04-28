# Website Validation and CI Triage Design

**Goal:** Re-validate all site-backed checker tests by exercising the existing GitHub Actions workflow from a dedicated branch, then distinguish between GitHub-IP-specific failures, genuinely unavailable sites, and parser/schema regressions.

## Chosen approach

Use the current `push`-triggered `python-test.yml` workflow rather than broadening CI triggers first. A dedicated validation branch will be pushed to GitHub to collect hosted test results. Any failures will then be reproduced locally in the isolated worktree:

1. **Fails in GitHub but passes locally**: treat as likely GitHub IP blocking or hosted-network-specific access restrictions and skip the affected test with a clean, explicit reason in Python test code.
2. **Fails both in GitHub and locally because the site is gone or permanently protected**: skip the affected test with a clean, explicit reason in Python test code.
3. **Fails both in GitHub and locally because site markup/schema changed but content is still accessible**: fix the checker/parser and keep the test enabled.

## Scope

- In scope: current checker tests, CI-triggering branch/PR workflow, skip reason cleanup, parser/schema fixes directly required by observed failures.
- Out of scope: unrelated refactors, broad test suite redesign, adding new websites, or changing checker behavior without evidence from current failures.

## Execution notes

- Work happens in a dedicated git worktree on branch `ci-website-validation`.
- A docs commit is acceptable as the initial change used to trigger GitHub Actions because the existing workflow runs on `push`.
- If multiple independent schema fixes are needed, they should be separated into follow-up commits/PRs after the initial validation branch identifies them.
