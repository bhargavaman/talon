import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "locales" / "en-US.json"


def _deep_get(data, key):
    value = data
    for part in key.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def _walk_strings(data):
    if isinstance(data, dict):
        for value in data.values():
            yield from _walk_strings(value)
    elif isinstance(data, list):
        for value in data:
            yield from _walk_strings(value)
    elif isinstance(data, str):
        yield data


class LocalizationCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with CATALOG_PATH.open("r", encoding="utf-8") as f:
            cls.catalog = json.load(f)

    def test_catalog_metadata(self):
        meta = self.catalog.get("meta")
        self.assertIsInstance(meta, dict)
        self.assertEqual(meta.get("code"), "en-US")
        self.assertEqual(meta.get("direction"), "ltr")
        self.assertTrue(meta.get("native_name"))
        self.assertTrue(meta.get("english_name"))

    def test_referenced_translation_keys_exist(self):
        key_patterns = [
            re.compile(r'i18n\.(?:t|tf)\("([^"]+)"'),
            re.compile(r'\bt\("([^"]+)"'),
        ]
        roots = [
            ROOT / "talon.py",
            ROOT / "configuration_components",
            ROOT / "debloat_components",
            ROOT / "preinstall_components",
            ROOT / "utilities",
            ROOT / "ui" / "configuration",
        ]
        missing = []
        for root in roots:
            paths = [root] if root.is_file() else sorted(root.rglob("*"))
            for path in paths:
                if path.suffix not in (".py", ".qml"):
                    continue
                text = path.read_text(encoding="utf-8")
                for pattern in key_patterns:
                    for match in pattern.finditer(text):
                        key = match.group(1)
                        if _deep_get(self.catalog, key) is None:
                            missing.append(f"{path.relative_to(ROOT)}: {key}")
        self.assertEqual([], missing)

    def test_catalog_placeholders_match_code_usage(self):
        code_text = "\n".join(
            path.read_text(encoding="utf-8")
            for root in [
                ROOT / "talon.py",
                ROOT / "configuration_components",
                ROOT / "debloat_components",
                ROOT / "preinstall_components",
                ROOT / "utilities",
            ]
            for path in ([root] if root.is_file() else sorted(root.rglob("*.py")))
        )
        for key_match in re.finditer(r'\bt\("([^"]+)",\s*\{([^}]+)\}\)', code_text, re.S):
            key = key_match.group(1)
            catalog_value = _deep_get(self.catalog, key)
            self.assertIsInstance(catalog_value, str, key)
            placeholders = set(re.findall(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}", catalog_value))
            supplied = set(re.findall(r'"([a-zA-Z_][a-zA-Z0-9_]*)"\s*:', key_match.group(2)))
            self.assertTrue(placeholders.issubset(supplied), f"{key}: missing {placeholders - supplied}")

    def test_no_obvious_qml_ui_literals_remain(self):
        allowed = {
            'title: "RAVEN Talon"',
            'text: "Talon"',
            'text: "TALON"',
            'property string titleText: ""',
            'property string editorText: ""',
        }
        offenders = []
        for path in sorted((ROOT / "ui" / "configuration").glob("*.qml")):
            for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                stripped = line.strip()
                if stripped in allowed:
                    continue
                if re.search(r'\b(?:text|title):\s*"[A-Za-z]', stripped):
                    offenders.append(f"{path.relative_to(ROOT)}:{line_no}: {stripped}")
                if re.search(r'"label":\s*"[A-Za-z]', stripped):
                    offenders.append(f"{path.relative_to(ROOT)}:{line_no}: {stripped}")
        self.assertEqual([], offenders)


if __name__ == "__main__":
    unittest.main()
