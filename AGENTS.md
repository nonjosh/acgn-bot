# AGENTS.md

## Watch list (config/list.yaml)

The chapter watch list is gitignored. Any change to `config/list.yaml` must be
saved to BOTH the local file and the gist, then deployed: run
`sh config/update-list.sh` (details in `config/AGENTS.md`).

## Local verification (avoid running the app with the full config/list.yaml by default)

To verify checker/app changes locally, default to the shortlist
`config/list_test.yaml` (gitignored, 2-3 media spanning media types plus the
target media under verification) via the existing `CONFIG_YML_FILEPATH`
override, not the full watch list:

```sh
CONFIG_YML_FILEPATH=config/list_test.yaml TOKEN=... CHAT_ID=... .venv/bin/python main.py
```

- Running with the full `config/list.yaml` is fine occasionally (e.g. a final
  end-to-end sanity run), but not as the default: it fans out into 45+ live
  checkers running in background threads, and heavy repeated traffic from a
  desktop IP can trigger sign-up/risk-control on sites that rate-limit (some
  ban the IP), plus it sends ~40 real messages to the Telegram channel.
- Shortlist should contain the target media plus one or two other media types
  so checker selection and scheduling still get covered.
- Prefer smaller steps first: unit tests (`.venv/bin/python -m unittest discover
  tests`), then a standalone probe script in `/tmp/opencode/` replicating the
  closest checker's request flow, then the shortlisted app run.
- For single-checker iteration without TgHelper, a tiny script instantiating
  just the checker (`BilibiliUploaderChecker(url).get_latest_chapter_list()`)
  is enough — Telegram env vars are only needed when running `main.py`.

## Tool-call hygiene in opencode TUI

- Never make unbounded `kubectl` calls: wrap with `timeout 30 kubectl ... > /tmp/opencode/file.log 2>&1`, then grep the file. A hanging `kubectl logs` blocks the TUI session.
- Do not pipe `kubectl logs` directly into `grep`/`tail` inside a long `sleep ... ; ...` chain: while a pod is booting or mid-rollout, the log stream can be empty or stall (slow uv cache mount) and the whole call returns nothing with no hint. After a `kubectl rollout restart`, first confirm `kubectl get pods -o wide` shows exactly one Running pod with a nonzero age before reading logs.
- When grepping Chinese logs, match both traditional and simplified variants, e.g. `grep -e '藥屋' -e '药屋' file.log`. Media names may be traditional while video titles/URLs are simplified, and vice versa.
- Prefer one bounded command that writes to a file, over repeated live queries; `sleep 120 && kubectl logs` style calls are the common source of "stuck" tool calls.
