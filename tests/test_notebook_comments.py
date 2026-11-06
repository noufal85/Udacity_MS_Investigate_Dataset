import io
import json
from pathlib import Path
import tokenize
import unittest


NOTEBOOK = Path(__file__).resolve().parents[1] / "Investigate_a_Dataset.ipynb"


class NotebookDocumentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cells = json.loads(NOTEBOOK.read_text())["cells"]

    def test_each_code_cell_contains_an_explanatory_comment(self):
        for index, cell in enumerate(self.cells, 1):
            if cell["cell_type"] != "code":
                continue
            source = "".join(cell["source"])
            with self.subTest(cell=index):
                comments = [
                    token.string[1:].strip()
                    for token in tokenize.generate_tokens(io.StringIO(source).readline)
                    if token.type == tokenize.COMMENT
                ]
                self.assertTrue(any(comments), "Code cell has no explanatory comment")

    def test_cleaned_summary_displays_standard_deviation(self):
        tables = [
            "".join(output.get("data", {}).get("text/plain", []))
            for cell in self.cells
            for output in cell.get("outputs", [])
        ]
        self.assertTrue(any(
            "Standard deviation" in table
            and "Age (years)" in table
            and "Booking delay (days)" in table
            for table in tables
        ), "Saved cleaned-data summary must show spread for age and booking delay")


if __name__ == "__main__":
    unittest.main()
