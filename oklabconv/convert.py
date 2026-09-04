"""sRGB <-> OKLab math.

OKLab is defined in two linear steps around a cube root nonlinearity:
sRGB -> linear sRGB -> LMS -> L'M'S' (cube root) -> OKLab.
The matrices below are the ones published by Bjoern Ottosson when he
introduced OKLab; they are what browsers use for CSS Color 4's oklab().
"""

# linear sRGB -> LMS
_M1 = (
    (0.4122214708, 0.5363325363, 0.0514459929),
    (0.2119034982, 0.6806995451, 0.1073969566),
    (0.0883024619, 0.2817188376, 0.6299787005),
)

# L'M'S' -> OKLab
_M2 = (
    (0.2104542553, 0.7936177850, -0.0040720468),
    (1.9779984951, -2.4285922050, 0.4505937099),
    (0.0259040371, 0.7827717662, -0.8086757660),
)

# OKLab -> L'M'S' (inverse of _M2)
_M2_INV = (
    (1.0, 0.3963377774, 0.2158037573),
    (1.0, -0.1055613458, -0.0638541728),
    (1.0, -0.0894841775, -1.2914855480),
)

# LMS -> linear sRGB (inverse of _M1)
_M1_INV = (
    (4.0767416621, -3.3077115913, 0.2309699292),
    (-1.2684380046, 2.6097574011, -0.3413193965),
    (-0.0041960863, -0.7034186147, 1.7076147010),
)


def _apply_matrix(m, v):
    return tuple(m[i][0] * v[0] + m[i][1] * v[1] + m[i][2] * v[2] for i in range(3))


def srgb_to_linear(c: float) -> float:
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def linear_to_srgb(c: float) -> float:
    if c <= 0.0031308:
        return c * 12.92
    return 1.055 * (c ** (1 / 2.4)) - 0.055


def hex_to_rgb(text: str) -> tuple[int, int, int]:
    text = text.strip().lstrip("#")
    if len(text) == 3:
        text = "".join(ch * 2 for ch in text)
    if len(text) != 6:
        raise ValueError(f"not a 6-digit (or 3-digit) hex color: {text!r}")
    return (int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    r = min(255, max(0, round(r)))
    g = min(255, max(0, round(g)))
    b = min(255, max(0, round(b)))
    return f"#{r:02x}{g:02x}{b:02x}"


def rgb_to_oklab(r: int, g: int, b: int) -> tuple[float, float, float]:
    linear = tuple(srgb_to_linear(c / 255.0) for c in (r, g, b))
    lms = _apply_matrix(_M1, linear)
    lms_cbrt = tuple(v ** (1 / 3) if v >= 0 else -((-v) ** (1 / 3)) for v in lms)
    return _apply_matrix(_M2, lms_cbrt)


def oklab_to_rgb(L: float, a: float, b: float) -> tuple[int, int, int]:
    lms_cbrt = _apply_matrix(_M2_INV, (L, a, b))
    lms = tuple(v ** 3 for v in lms_cbrt)
    linear = _apply_matrix(_M1_INV, lms)
    srgb = tuple(linear_to_srgb(c) * 255.0 for c in linear)
    return tuple(min(255, max(0, round(c))) for c in srgb)
