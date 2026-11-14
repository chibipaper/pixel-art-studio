"""Security regression checks; stdlib only. Run with python -m unittest discover -s tests."""
import ast
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
import validate_skill  # noqa: E402


class SecurityRegressions(unittest.TestCase):
    def test_bundled_builds_resolve_repository_scripts(self):
        paths = [ROOT / "examples/slime-bounce.py", *sorted((ROOT / "pixel-art").glob("*/build.py"))]
        for path in paths:
            with self.subTest(path=path):
                source = path.read_text(encoding="utf-8")
                ast.parse(source, filename=str(path))
                self.assertNotIn("/Users/game/", source)
                self.assertIn("Path(__file__).resolve().parents[", source)

    def test_validator_does_not_execute_generated_build(self):
        source = (SCRIPTS / "validate_skill.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        # Regression check: generated build is parsed, but never passed to subprocess.
        self.assertIn("ast.parse(generated.read_text", source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == "_run_checked":
                    self.assertNotIn("out / 'build.py'", ast.get_source_segment(source, node) or "")

    def test_child_env_excludes_sensitive_variables(self):
        env = validate_skill._child_env()
        allowed = {"PATH", "SYSTEMROOT", "WINDIR", "TMPDIR", "TMP", "TEMP",
                   "PYTHONNOUSERSITE"}
        self.assertLessEqual(set(env), allowed)
        self.assertEqual(env["PYTHONNOUSERSITE"], "1")
        custom = validate_skill._child_env(ROOT / "scripts")
        self.assertEqual(custom["PYTHONPATH"], str(SCRIPTS))

    def test_generated_code_does_not_run_on_parse(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "executed"
            code = "from pathlib import Path\\nPath(" + repr(str(marker)) + ").write_text('bad')\\n"
            ast.parse(code)
            self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
