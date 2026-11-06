import argparse
from datetime import datetime
from pathlib import Path

from image_generator import generate_image
from poster_maker import SIZE, make_poster

POSTER_DIR = Path(__file__).parent / "outputs" / "posters"

parser = argparse.ArgumentParser(description="Make a typography poster (18x24 in, 300 dpi).")
parser.add_argument("--quote", required=True, help=r'Quote text; "\n" starts a new line')
parser.add_argument("--author", help="Attribution, shown as '— Author'")
parser.add_argument("--bg", default="#F2EBDD", help="Background colour")
parser.add_argument("--text-color", default="#252525")
parser.add_argument("--author-color", default="#A66B52", help="Author and accent line colour")
parser.add_argument("--bg-prompt", help="Generate the background with Draw Things from this prompt")
parser.add_argument("--emphasis-last", action="store_true", help="Set the last quote line heavier")
args = parser.parse_args()

background = None
if args.bg_prompt:
    background = generate_image(
        f"{args.bg_prompt}, no text, no letters, no words",
        width=768,  # 3:4 like the poster; multiples of 64
        height=1024,
        negative_prompt="text, letters, words, typography, watermark, signature",
    )

poster = make_poster(
    args.quote.replace("\\n", "\n"),
    author=args.author,
    bg=args.bg,
    text_color=args.text_color,
    author_color=args.author_color,
    background=background,
    emphasis_last=args.emphasis_last,
)

POSTER_DIR.mkdir(parents=True, exist_ok=True)
output_path = POSTER_DIR / f"poster_{datetime.now():%Y%m%d_%H%M%S}.png"
poster.save(output_path, dpi=(300, 300))
print(f"Poster saved to: {output_path} ({SIZE[0]}x{SIZE[1]})")
