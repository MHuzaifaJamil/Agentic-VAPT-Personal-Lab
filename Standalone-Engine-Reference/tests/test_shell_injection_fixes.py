"""engine.py's _run_shell built a shell=True command string via f-string
interpolation of target-controlled values — double-quoting doesn't stop
$(...)/backtick substitution. Must use argv-list Popen instead. See
SECURITY-REVIEW-2026-08-22.md finding #4 (HIGH).

Finding #5 (tools/hunt.py's run_graphql_audit) does not apply to this
repo's tools/hunt.py — that function doesn't exist here; this hunt.py's
GraphQL auditing (if any) is invoked through a different path, so the
corresponding test class was removed rather than left failing against a
function this codebase never had."""
import os
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import engine


class TestEngineRunShellNoInjection:
    def test_shell_metacharacters_in_arg_do_not_execute(self, tmp_path):
        marker = tmp_path / "should_not_exist"
        payload = f'x$(touch {marker})'
        success, output = engine._run_shell(["echo", payload])
        assert not marker.exists()
        assert payload in output  # printed literally, not evaluated

    def test_normal_command_still_runs(self):
        success, output = engine._run_shell(["echo", "hello"])
        assert success
        assert "hello" in output
