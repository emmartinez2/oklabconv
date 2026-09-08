import os
import tempfile
import unittest

from oklabconv.cli import format_oklab, parse_oklab, read_lines


class ParseOklabTests(unittest.TestCase):
    def test_functional_notation(self):
        self.assertEqual(parse_oklab("oklab(0.5 0.1 -0.2)"), (0.5, 0.1, -0.2))

    def test_functional_notation_is_case_insensitive(self):
        self.assertEqual(parse_oklab("OKLAB(0.5 0.1 -0.2)"), (0.5, 0.1, -0.2))

    def test_bare_numbers_separated_by_spaces(self):
        self.assertEqual(parse_oklab("0.5 0.1 -0.2"), (0.5, 0.1, -0.2))

    def test_bare_numbers_separated_by_commas(self):
        self.assertEqual(parse_oklab("0.5, 0.1, -0.2"), (0.5, 0.1, -0.2))

    def test_wrong_number_of_values_raises(self):
        with self.assertRaises(ValueError):
            parse_oklab("0.5 0.1")

    def test_non_numeric_value_raises(self):
        with self.assertRaises(ValueError):
            parse_oklab("0.5 abc -0.2")


class FormatOklabTests(unittest.TestCase):
    def test_formats_with_four_decimal_places(self):
        self.assertEqual(format_oklab(0.5, 0.1, -0.2), "oklab(0.5000 0.1000 -0.2000)")

    def test_round_trips_through_parse(self):
        original = (0.62796, 0.22486, 0.12585)
        formatted = format_oklab(*original)
        parsed = parse_oklab(formatted)
        for a, b in zip(original, parsed):
            self.assertAlmostEqual(a, b, places=4)


class ReadLinesTests(unittest.TestCase):
    def test_skips_blank_lines_and_strips_whitespace(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "colors.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write("#ff0000\n\n  #00ff00  \n\n#0000ff\n")
            self.assertEqual(
                list(read_lines([path])), ["#ff0000", "#00ff00", "#0000ff"]
            )

    def test_reads_multiple_files_in_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            path_a = os.path.join(tmp, "a.txt")
            path_b = os.path.join(tmp, "b.txt")
            with open(path_a, "w", encoding="utf-8") as f:
                f.write("#ff0000\n")
            with open(path_b, "w", encoding="utf-8") as f:
                f.write("#00ff00\n")
            self.assertEqual(
                list(read_lines([path_a, path_b])), ["#ff0000", "#00ff00"]
            )


if __name__ == "__main__":
    unittest.main()
