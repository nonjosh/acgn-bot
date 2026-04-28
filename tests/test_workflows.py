"""Regression tests for GitHub workflow configuration."""

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


class TestPythonTestWorkflow(unittest.TestCase):
    """Ensure the Python test workflow matches the repo tooling."""

    def test_python_test_workflow_uses_uv_and_pr_trigger(self) -> None:
        workflow = (
            REPO_ROOT / ".github" / "workflows" / "python-test.yml"
        ).read_text(encoding="utf-8")

        self.assertIn("pull_request", workflow)
        self.assertIn("astral-sh/setup-uv@v6", workflow)
        self.assertIn("uv sync --frozen --group dev", workflow)
        self.assertIn("uv run python -m unittest", workflow)


if __name__ == "__main__":
    unittest.main()
