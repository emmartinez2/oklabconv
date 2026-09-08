import unittest

from oklabconv.convert import (
    hex_to_rgb,
    linear_to_srgb,
    oklab_to_rgb,
    rgb_to_hex,
    rgb_to_oklab,
    srgb_to_linear,
)


class HexToRgbTests(unittest.TestCase):
    def test_six_digit(self):
        self.assertEqual(hex_to_rgb("#ff00aa"), (255, 0, 170))

    def test_three_digit_expands_each_nibble(self):
        self.assertEqual(hex_to_rgb("#f0a"), (255, 0, 170))

    def test_leading_hash_is_optional(self):
        self.assertEqual(hex_to_rgb("336699"), (51, 102, 153))

    def test_case_insensitive(self):
        self.assertEqual(hex_to_rgb("#FF00AA"), (255, 0, 170))

    def test_surrounding_whitespace_is_stripped(self):
        self.assertEqual(hex_to_rgb("  #ff00aa  "), (255, 0, 170))

    def test_wrong_length_raises(self):
        with self.assertRaises(ValueError):
            hex_to_rgb("#ff00a")

    def test_non_hex_characters_raise(self):
        with self.assertRaises(ValueError):
            hex_to_rgb("#gggggg")

    def test_empty_string_raises(self):
        with self.assertRaises(ValueError):
            hex_to_rgb("")


class RgbToHexTests(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(rgb_to_hex(255, 0, 170), "#ff00aa")

    def test_clamps_high_values(self):
        self.assertEqual(rgb_to_hex(300, 0, 0), "#ff0000")

    def test_clamps_negative_values(self):
        self.assertEqual(rgb_to_hex(-10, 0, 0), "#000000")

    def test_rounds_fractional_values(self):
        self.assertEqual(rgb_to_hex(127.4, 127.6, 0), "#7f8000")


class SrgbLinearTests(unittest.TestCase):
    def test_zero_and_one_are_fixed_points(self):
        self.assertAlmostEqual(srgb_to_linear(0.0), 0.0)
        self.assertAlmostEqual(srgb_to_linear(1.0), 1.0)
        self.assertAlmostEqual(linear_to_srgb(0.0), 0.0)
        self.assertAlmostEqual(linear_to_srgb(1.0), 1.0)

    def test_values_away_from_the_threshold_round_trip_precisely(self):
        for c in (0.01, 0.2, 0.5, 0.9, 0.99):
            self.assertAlmostEqual(linear_to_srgb(srgb_to_linear(c)), c, places=9)

    def test_value_at_the_piecewise_cutover_round_trips(self):
        # the linear and gamma segments meet near c = 0.04045; the
        # rounded constants only agree to a handful of digits there.
        self.assertAlmostEqual(
            linear_to_srgb(srgb_to_linear(0.04045)), 0.04045, places=4
        )


class RgbOklabTests(unittest.TestCase):
    def test_black_is_the_oklab_origin(self):
        L, a, b = rgb_to_oklab(0, 0, 0)
        self.assertAlmostEqual(L, 0.0, places=4)
        self.assertAlmostEqual(a, 0.0, places=4)
        self.assertAlmostEqual(b, 0.0, places=4)

    def test_white_has_lightness_one_and_no_chroma(self):
        L, a, b = rgb_to_oklab(255, 255, 255)
        self.assertAlmostEqual(L, 1.0, places=4)
        self.assertAlmostEqual(a, 0.0, places=4)
        self.assertAlmostEqual(b, 0.0, places=4)

    def test_red_matches_published_reference_value(self):
        L, a, b = rgb_to_oklab(255, 0, 0)
        self.assertAlmostEqual(L, 0.6280, places=4)
        self.assertAlmostEqual(a, 0.2249, places=4)
        self.assertAlmostEqual(b, 0.1258, places=4)

    def test_round_trip_is_stable_within_a_step(self):
        for hexcode in (
            "#000000",
            "#ffffff",
            "#ff0000",
            "#00ff00",
            "#0000ff",
            "#3366ff",
            "#808080",
            "#123456",
            "#abcdef",
        ):
            r, g, b = hex_to_rgb(hexcode)
            r2, g2, b2 = oklab_to_rgb(*rgb_to_oklab(r, g, b))
            for original, restored in zip((r, g, b), (r2, g2, b2)):
                self.assertLessEqual(abs(original - restored), 1)

    def test_out_of_gamut_oklab_clamps_instead_of_raising(self):
        # a very high lightness with strong chroma maps outside [0, 255]
        # before clamping; this must not raise or return an invalid value.
        r, g, b = oklab_to_rgb(1.5, 0.5, 0.5)
        for component in (r, g, b):
            self.assertGreaterEqual(component, 0)
            self.assertLessEqual(component, 255)


if __name__ == "__main__":
    unittest.main()
