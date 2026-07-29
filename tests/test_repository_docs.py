import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


class RepositoryDocumentationTest(unittest.TestCase):
    def test_all_relative_markdown_links_exist(self):
        missing = []
        for document in ROOT.rglob("*.md"):
            for raw_target in MARKDOWN_LINK.findall(document.read_text(encoding="utf-8")):
                target = raw_target.strip("<>").split("#", 1)[0]
                if not target or target.startswith(("http://", "https://", "mailto:", "/")):
                    continue
                if not (document.parent / target).resolve().exists():
                    missing.append(f"{document.relative_to(ROOT)} -> {raw_target}")
        self.assertEqual(missing, [])

    def test_documented_module_entrypoints_exist(self):
        missing = []
        for document in ROOT.rglob("*.md"):
            for module in re.findall(r"python(?:3)?\s+-m\s+([A-Za-z_][\w.]*)", document.read_text(encoding="utf-8")):
                if module.split(".", 1)[0] not in {"client", "server", "web"}:
                    continue
                module_path = ROOT.joinpath(*module.split(".")).with_suffix(".py")
                if not module_path.exists():
                    missing.append(f"{document.relative_to(ROOT)} -> {module}")
        self.assertEqual(missing, [])

    def test_each_service_has_isolated_requirements_and_environment_example(self):
        for service in ("client", "server", "web"):
            with self.subTest(service=service):
                self.assertTrue((ROOT / service / "requirements.txt").is_file())
                self.assertTrue((ROOT / service / ".env.example").is_file())

    def test_requirements_do_not_list_standard_library_modules(self):
        stdlib = {"csv", "json", "logging", "math", "os", "pathlib", "socket", "threading", "typing", "uuid"}
        for requirements in ROOT.rglob("requirements*.txt"):
            packages = {
                line.split(";", 1)[0].split("=", 1)[0].strip().lower()
                for line in requirements.read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.lstrip().startswith(("#", "-r"))
            }
            self.assertTrue(stdlib.isdisjoint(packages), requirements)
