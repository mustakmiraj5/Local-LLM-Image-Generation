import base64
import json
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

API_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"

OUTPUT_DIR = Path(__file__).parent / "outputs" / "generated"


def generate_image(
    prompt: str,
    width: int | None = None,
    height: int | None = None,
    negative_prompt: str | None = None,
) -> Path:
    """Generate an image with Draw Things. Unset options use the app's current settings."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    payload = {"prompt": prompt}
    if width and height:
        payload["width"] = width
        payload["height"] = height
    if negative_prompt:
        payload["negative_prompt"] = negative_prompt

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    print("Sending prompt to Draw Things...")
    print("Generating image. Please wait...")

    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            result = json.loads(response.read().decode("utf-8"))

    except Exception as error:
        raise RuntimeError(
            f"Image generation failed: {error}"
        ) from error

    images = result.get("images", [])

    if not images:
        raise RuntimeError("Draw Things returned no images.")

    image_data = base64.b64decode(
        images[0].split(",", 1)[-1]
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"image_{timestamp}.png"

    output_path.write_bytes(image_data)

    print(f"\nImage generated successfully!")
    print(f"Saved to: {output_path}")
    print(f"File size: {len(image_data):,} bytes")

    return output_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate an image with Draw Things (prompt from stdin).")
    parser.add_argument("--width", type=int, help="Multiple of 64; needs --height too")
    parser.add_argument("--height", type=int, help="Multiple of 64; needs --width too")
    args = parser.parse_args()
    if bool(args.width) != bool(args.height):
        parser.error("set both --width and --height, or neither")

    print("\nDescribe the image you want (Ctrl-D on a new line to finish):")
    prompt = sys.stdin.read().strip()

    if not prompt:
        print("Prompt cannot be empty.")
    else:
        generate_image(prompt, args.width, args.height)
