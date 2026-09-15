import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from oklabconv.cli import (
    format_oklab,
    format_oklch,
    main,
    parse_oklab,
    parse_oklch,
    read_lines,
)


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


class ParseOklchTests(unittest.TestCase):
    def test_functional_notation(self):
        self.assertEqual(parse_oklch("oklch(0.5 0.1 29.2)"), (0.5, 0.1, 29.2))

    def test_functional_notation_is_case_insensitive(self):
        self.assertEqual(parse_oklch("OKLCH(0.5 0.1 29.2)"), (0.5, 0.1, 29.2))

    def test_bare_numbers_separated_by_commas(self):
        self.assertEqual(parse_oklch("0.5, 0.1, 29.2"), (0.5, 0.1, 29.2))

    def test_wrong_number_of_values_raises(self):
        with self.assertRaises(ValueError):
            parse_oklch("0.5 0.1")


class FormatOklchTests(unittest.TestCase):
    def test_formats_hue_with_two_decimal_places(self):
        self.assertEqual(format_oklch(0.5, 0.1, 29.2), "oklch(0.5000 0.1000 29.20)")


class MainCliTests(unittest.TestCase):
    def _run(self, argv):
        buf = io.StringIO()
        with redirect_stdout(buf):
            main(argv)
        return buf.getvalue()

    def _write(self, tmp, name, contents):
        path = os.path.join(tmp, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(contents)
        return path

    def test_hex_to_oklch_has_expected_shape(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(tmp, "in.txt", "#ff0000\n")
            output = self._run(["--to", "oklch", path]).strip()
            self.assertTrue(output.startswith("oklch(0.6280 "))
            L, C, H = parse_oklch(output)
            self.assertAlmostEqual(C, 0.2577, places=3)
            self.assertGreaterEqual(H, 0.0)
            self.assertLess(H, 360.0)

    def test_hex_to_oklch_round_trips_through_srgb(self):
        with tempfile.TemporaryDirectory() as tmp:
            hex_path = self._write(tmp, "hex.txt", "#3366ff\n")
            oklch_line = self._run(["--to", "oklch", hex_path])
            oklch_path = self._write(tmp, "oklch.txt", oklch_line)
            output = self._run(["--to", "srgb", oklch_path])
            self.assertEqual(output.strip(), "#3366ff")

    def test_oklab_lines_still_work_with_to_srgb(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(tmp, "in.txt", "oklab(0.6280 0.2249 0.1258)\n")
            output = self._run(["--to", "srgb", path])
            self.assertEqual(output.strip(), "#ff0000")


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
