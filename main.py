import argparse
import sys
from datetime import datetime
from pathlib import Path

from image_generator import generate_image
from poster_maker import SIZE, make_poster
from prompt_refiner import refine_prompt

POSTER_DIR = Path(__file__).parent / "outputs" / "posters"
INTERACTIVE = sys.stdin.isatty()  # no terminal (scripted run): never ask, use flags/defaults

parser = argparse.ArgumentParser(
    description="Generate an image or a typography poster. Options you leave out are asked interactively."
)
parser.add_argument("--mode", choices=["image", "poster"])
parser.add_argument("--prompt", help="Image prompt, or the background prompt in poster mode")
parser.add_argument("--refine", action=argparse.BooleanOptionalAction, help="Let Qwen improve the prompt")
parser.add_argument("--width", type=int, help="Image mode; multiple of 64, needs --height")
parser.add_argument("--height", type=int, help="Image mode; multiple of 64, needs --width")
poster = parser.add_argument_group("poster mode")
poster.add_argument("--quote", help=r'Quote text; "\n" starts a new line')
poster.add_argument("--author", help="Attribution, shown as '— Author'")
poster.add_argument("--bg", default="#F2EBDD", help="Background colour (when there is no prompt)")
poster.add_argument("--text-color", default="#252525")
poster.add_argument("--author-color", default="#A66B52", help="Author and accent line colour")
poster.add_argument("--emphasis-last", action=argparse.BooleanOptionalAction, help="Set the last quote line heavier")
args = parser.parse_args()

if bool(args.width) != bool(args.height):
    parser.error("set both --width and --height, or neither")


def ask(question: str) -> str:
    return input(f"{question}: ").strip()


def ask_yes(question: str, default: bool) -> bool:
    answer = input(f"{question} [{'Y/n' if default else 'y/N'}]: ").strip().lower()
    return answer.startswith("y") if answer else default


def read_prompt(label: str) -> str:
    print(f"{label} (paste, then Ctrl-D on an empty line):")
    return sys.stdin.read().strip()


def require(value, flag: str, asker):
    """Use the flag's value, else ask; scripted runs must pass the flag."""
    if value is not None:
        return value
    if not INTERACTIVE:
        parser.error(f"{flag} is required when not running in a terminal")
    return asker()


def choose_prompt(prompt: str, purpose: str) -> str:
    refine = args.refine
    if refine is None:
        refine = INTERACTIVE and ask_yes("Refine the prompt with Qwen?", True)
    if not refine:
        return prompt

    while True:
        print("Asking Qwen to refine the prompt...")
        refined = refine_prompt(prompt, purpose)
        if refined is None:
            return prompt
        print(f"\nRefined prompt:\n  {refined}\n")
        if not INTERACTIVE:
            return refined
        choice = ask("[U]se it / use [o]riginal / [r]etry")[:1].lower()
        if choice == "o":
            return prompt
        if choice != "r":
            return refined


mode = require(args.mode, "--mode", lambda: ask("What do you want to make? [image/poster]").lower())
if mode not in ("image", "poster"):
    parser.error(f"unknown mode {mode!r}; choose image or poster")

if mode == "image":
    prompt = require(args.prompt, "--prompt", lambda: read_prompt("Prompt"))
    if not prompt:
        parser.error("the prompt cannot be empty")
    generate_image(choose_prompt(prompt, "image"), args.width, args.height)
    sys.exit()

# Poster: quote and author are drawn by Pillow and never sent to Qwen, so they stay exact.
quote = require(args.quote, "--quote", lambda: ask(r'Quote (use \n for a new line)'))
if not quote:
    parser.error("the quote cannot be empty")
quote = quote.replace("\\n", "\n")
author = args.author
if author is None and INTERACTIVE:
    author = ask("Author (optional)") or None
emphasis_last = args.emphasis_last
if emphasis_last is None:
    emphasis_last = INTERACTIVE and "\n" in quote and ask_yes("Set the last line heavier?", False)

bg_prompt = args.prompt
if bg_prompt is None and INTERACTIVE:
    bg_prompt = read_prompt("AI background prompt, or leave empty for a flat colour")

background = None
if bg_prompt:
    background = generate_image(
        f"{choose_prompt(bg_prompt, 'background')}, no text, no letters, no words",
        width=768,  # 3:4 like the poster; multiples of 64
        height=1024,
        negative_prompt="text, letters, words, typography, watermark, signature",
    )

poster_image = make_poster(
    quote,
    author=author,
    bg=args.bg,
    text_color=args.text_color,
    author_color=args.author_color,
    background=background,
    emphasis_last=emphasis_last,
)

POSTER_DIR.mkdir(parents=True, exist_ok=True)
output_path = POSTER_DIR / f"poster_{datetime.now():%Y%m%d_%H%M%S}.png"
poster_image.save(output_path, dpi=(300, 300))
print(f"Poster saved to: {output_path} ({SIZE[0]}x{SIZE[1]})")
