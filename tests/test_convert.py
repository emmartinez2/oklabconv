import unittest

from oklabconv.convert import (
    hex_to_rgb,
    linear_to_srgb,
    oklab_to_oklch,
    oklab_to_rgb,
    oklch_to_oklab,
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


class OklabOklchTests(unittest.TestCase):
    def test_neutral_gray_has_zero_chroma(self):
        L, C, H = oklab_to_oklch(0.5, 0.0, 0.0)
        self.assertAlmostEqual(L, 0.5)
        self.assertAlmostEqual(C, 0.0)
        self.assertAlmostEqual(H, 0.0)

    def test_red_matches_published_reference_value(self):
        # derived from the published OKLab reference value for red:
        # C = hypot(a, b), H = atan2(b, a) in degrees.
        L, C, H = oklab_to_oklch(0.6280, 0.2249, 0.1258)
        self.assertAlmostEqual(C, 0.2577, places=3)
        self.assertAlmostEqual(H, 29.22, places=1)

    def test_hue_wraps_into_zero_to_360(self):
        _, _, H = oklab_to_oklch(0.5, -0.1, -0.1)
        self.assertGreaterEqual(H, 0.0)
        self.assertLess(H, 360.0)

    def test_round_trips_through_oklab(self):
        for L, a, b in (
            (0.5, 0.1, -0.05),
            (0.8, -0.15, 0.2),
            (0.2, 0.0, 0.0),
            (0.6280, 0.2249, 0.1258),
        ):
            L2, a2, b2 = oklch_to_oklab(*oklab_to_oklch(L, a, b))
            self.assertAlmostEqual(L, L2, places=9)
            self.assertAlmostEqual(a, a2, places=9)
            self.assertAlmostEqual(b, b2, places=9)

    def test_full_round_trip_through_rgb(self):
        for hexcode in ("#ff0000", "#3366ff", "#123456", "#abcdef"):
            r, g, b = hex_to_rgb(hexcode)
            L, C, H = oklab_to_oklch(*rgb_to_oklab(r, g, b))
            r2, g2, b2 = oklab_to_rgb(*oklch_to_oklab(L, C, H))
            for original, restored in zip((r, g, b), (r2, g2, b2)):
                self.assertLessEqual(abs(original - restored), 1)


if __name__ == "__main__":
    unittest.main()
