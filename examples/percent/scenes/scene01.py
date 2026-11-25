def draw(t, numbers, style):
    w, h = style.width, style.height
    bar = int(w * 0.8)
    filled = int(bar * numbers["percent"] / 100 * t)  # the 12 percent slice grows
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        f'<rect width="{w}" height="{h}" fill="{style.background}"/>'
        f'<text x="{w // 2}" y="{h // 3}" font-size="120" fill="{style.text}" font-family="{style.font}" '
        f'text-anchor="middle">{numbers["percent"]}% of {numbers["total"]}</text>'
        f'<rect x="{w // 10}" y="{h // 2}" width="{bar}" height="80" fill="none" stroke="{style.text}" stroke-width="4"/>'
        f'<rect x="{w // 10}" y="{h // 2}" width="{filled}" height="80" fill="{style.accent}"/></svg>'
    )
