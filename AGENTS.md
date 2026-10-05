# AGENTS.md

## Watch list (config/list.yaml)

The chapter watch list is gitignored. Any change to `config/list.yaml` must be
saved to BOTH the local file and the gist, then deployed: run
`sh config/update-list.sh` (details in `config/AGENTS.md`).

## Tool-call hygiene in opencode TUI

- Never make unbounded `kubectl` calls: wrap with `timeout 30 kubectl ... > /tmp/opencode/file.log 2>&1`, then grep the file. A hanging `kubectl logs` blocks the TUI session.
- Do not pipe `kubectl logs` directly into `grep`/`tail` inside a long `sleep ... ; ...` chain: while a pod is booting or mid-rollout, the log stream can be empty or stall (slow uv cache mount) and the whole call returns nothing with no hint. After a `kubectl rollout restart`, first confirm `kubectl get pods -o wide` shows exactly one Running pod with a nonzero age before reading logs.
- When grepping Chinese logs, match both traditional and simplified variants, e.g. `grep -e '藥屋' -e '药屋' file.log`. Media names may be traditional while video titles/URLs are simplified, and vice versa.
- Prefer one bounded command that writes to a file, over repeated live queries; `sleep 120 && kubectl logs` style calls are the common source of "stuck" tool calls.
