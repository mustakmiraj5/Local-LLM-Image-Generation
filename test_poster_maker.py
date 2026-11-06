from poster_maker import fit_size, make_poster, text_width

lines, weights = ["Keep it simple,", "stupid."], ["Bold", "Black"]

size = fit_size(lines, weights, 480)
assert max(text_width(l, w, size) for l, w in zip(lines, weights)) <= 480
assert max(text_width(l, w, size + 1) for l, w in zip(lines, weights)) > 480

img = make_poster("\n".join(lines), "Kelly Johnson", emphasis_last=True, size=(600, 800))
assert img.size == (600, 800)
assert img.getpixel((0, 0)) == (0xF2, 0xEB, 0xDD)
# Ink stays inside the 10% side margins.
left, _, right, _ = img.convert("L").point(lambda p: p < 128 and 255).getbbox()
assert 60 <= left and right <= 540, (left, right)

print("ok")
