def draw(t, numbers, style):
    w, h = style.width, style.height
    one = numbers["total"] / 100
    shown = int(100 * t)  # count of small boxes lit, one box is one percent
    boxes = "".join(
        f'<rect x="{w // 10 + (i % 10) * 80}" y="{h // 3 + (i // 10) * 80}" width="70" height="70" '
        f'fill="{style.accent if i < shown else style.background}" stroke="{style.text}"/>'
        for i in range(100)
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        f'<rect width="{w}" height="{h}" fill="{style.background}"/>{boxes}'
        f'<text x="{w // 2}" y="{h // 4}" font-size="90" fill="{style.text}" font-family="{style.font}" '
        f'text-anchor="middle">1% = {one:g}</text></svg>'
    )
