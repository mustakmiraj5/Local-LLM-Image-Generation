import prompt_refiner
from prompt_refiner import clean, refine_prompt

assert clean('Prompt: "A red fox in snow."') == "A red fox in snow."
assert clean("<think>planning...</think>\nRefined prompt: A red fox.") == "A red fox."
assert clean("A fox at dawn.") == "A fox at dawn."
assert clean("   ") is None

# Fallback: Qwen unreachable -> None, caller keeps the original prompt.
prompt_refiner.OLLAMA_URL = "http://127.0.0.1:9/api/chat"
assert refine_prompt("a fox") is None

print("ok")
