def draw(t, numbers, style):
    w, h = style.width, style.height
    size = int(100 + 100 * t)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        f'<rect width="{w}" height="{h}" fill="{style.background}"/>'
        f'<text x="{w // 2}" y="{h // 2}" font-size="{size}" fill="{style.accent}" font-family="{style.font}" '
        f'text-anchor="middle">{numbers["answer"]}</text></svg>'
    )
