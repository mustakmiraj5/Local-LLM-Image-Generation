import json
import re
import urllib.request

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "qwen3.5:4b"

SYSTEM_PROMPT = """You rewrite image prompts for the FLUX text-to-image model.

Rules:
- Keep everything the user asked for: subject, details, style, colours and mood. Never remove or contradict any of it.
- If the prompt is short or vague, add specific, plausible visual detail that fits the user's intent.
- If the prompt is already detailed, improve wording and order only; do not pad it.
- Write natural, descriptive English sentences in this order: main subject, setting, lighting, composition and camera, style or medium.
- Do not use weights like (word:1.2), comma-separated tag lists, negative phrasing, or filler like "8k, masterpiece".
- Aim for 40 to 120 words.
- Reply with the prompt only: no title, no quotes, no explanation."""

BACKGROUND_RULES = """

This image is the background of a typography poster; the text is added later by other software.
- Keep a large, calm, uncluttered area where text can sit.
- End the prompt with exactly: "No text or lettering anywhere in the image." (the only negative phrasing allowed)."""


def clean(reply: str) -> str | None:
    """Strip reasoning blocks, labels and wrapping quotes from the model's reply."""
    text = re.sub(r"<think>.*?</think>", "", reply, flags=re.S).strip()
    text = re.sub(r"^(refined |improved )?prompt\s*:\s*", "", text, flags=re.I)
    text = text.strip().strip("\"'`").strip()
    return text or None


def refine_prompt(prompt: str, purpose: str = "image") -> str | None:
    """Return Qwen's improved prompt, or None if Qwen is unavailable.

    purpose: "image" for a standalone image, "background" for a poster background.
    """
    system = SYSTEM_PROMPT + (BACKGROUND_RULES if purpose == "background" else "")
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "think": False,  # skip the reasoning pass; it's slow and not needed here
        "options": {"temperature": 0.7},
    }
    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            reply = json.loads(response.read().decode("utf-8"))["message"]["content"]
    except (OSError, ValueError, KeyError) as error:
        print(f"Qwen unavailable ({error}), using your prompt as-is.")
        return None

    refined = clean(reply)
    if refined is None:
        print("Qwen returned an empty prompt, using your prompt as-is.")
    return refined
