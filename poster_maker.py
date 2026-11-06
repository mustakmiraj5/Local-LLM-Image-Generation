from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

FONTS_DIR = Path(__file__).parent / "fonts"
SIZE = (5400, 7200)  # 18x24 in at 300 dpi
MARGIN = 0.10  # of page width, each side


def font(weight: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS_DIR / f"Inter-{weight}.ttf"), size)


def text_width(text: str, weight: str, size: int) -> int:
    left, _, right, _ = font(weight, size).getbbox(text)
    return right - left


def fit_size(lines: list[str], weights: list[str], max_width: int) -> int:
    """Largest font size at which the widest line fits within max_width."""
    def widest(size):
        return max(text_width(line, w, size) for line, w in zip(lines, weights))

    # Width scales ~linearly with size; estimate, then correct for hinting.
    size = int(1000 * max_width / widest(1000))
    while widest(size) > max_width:
        size -= 1
    while widest(size + 1) <= max_width:
        size += 1
    return size


def make_poster(
    quote: str,
    author: str | None = None,
    bg: str = "#F2EBDD",
    text_color: str = "#252525",
    author_color: str = "#A66B52",
    background: Path | None = None,
    emphasis_last: bool = False,
    size: tuple[int, int] = SIZE,
) -> Image.Image:
    W, H = size
    if background:
        img = ImageOps.fit(Image.open(background).convert("RGB"), size, Image.LANCZOS)
    else:
        img = Image.new("RGB", size, bg)
    draw = ImageDraw.Draw(img)

    lines = quote.split("\n")
    weights = ["Bold"] * len(lines)
    if emphasis_last and len(lines) > 1:
        weights[-1] = "Black"

    x = round(W * MARGIN)
    q_size = fit_size(lines, weights, W - 2 * x)
    pitch = round(q_size * 1.08)  # tight display leading
    cap = q_size * 0.73  # Inter cap height
    gap = round(q_size * 0.5)
    rule_w, rule_t = round(W * 0.08), max(2, round(H * 0.0015))
    a_size = round(q_size * 0.3)
    a_text = f"— {author}" if author else None

    # Block: cap top of line 1 -> baseline of author (or rule); centred vertically.
    block_h = cap + pitch * (len(lines) - 1) + gap + rule_t
    if a_text:
        block_h += gap + a_size * 0.73
    y = (H - block_h) / 2 + cap  # first baseline

    for line, weight in zip(lines, weights):
        f = font(weight, q_size)
        # Shift by the glyph's left bearing so every line's ink starts exactly at x.
        draw.text((x - f.getbbox(line, anchor="ls")[0], y), line, font=f, fill=text_color, anchor="ls")
        y += pitch
    y += gap - pitch

    draw.rectangle((x, y, x + rule_w, y + rule_t - 1), fill=author_color)
    y += rule_t

    if a_text:
        y += gap + a_size * 0.73
        f = font("Light", a_size)
        draw.text((x - f.getbbox(a_text, anchor="ls")[0], y), a_text, font=f, fill=author_color, anchor="ls")

    return img
