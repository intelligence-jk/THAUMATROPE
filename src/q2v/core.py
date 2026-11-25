"""One question, one storyboard, one code file per scene, one style file.

Layout of a project folder:
    storyboard.json   the question, and per scene: id, seconds, numbers, optional "say" text
    style.json        size, fps, pace, colours, font (the only file you edit to restyle)
    scenes/<id>.py    defines draw(t, numbers, style) -> SVG text, with t from 0 to 1

Frame maths is exact: frames for a scene = round(seconds / pace * fps), computed with Fraction.
"""
import importlib.util
import json
import re
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path


@dataclass(frozen=True)
class Style:
    width: int = 1080
    height: int = 1920
    fps: int = 30
    pace: F = F(1)  # 2 means everything runs twice as fast
    background: str = "#0b1f3a"
    text: str = "#ffffff"
    accent: str = "#ffb703"
    font: str = "sans-serif"


@dataclass(frozen=True)
class Scene:
    id: str
    seconds: F
    numbers: dict
    say: str = ""


@dataclass(frozen=True)
class Storyboard:
    question: str
    scenes: tuple


def _frac(x):
    """Exact from JSON numbers and strings: 2.5 and "2.5" both become 5/2."""
    return F(str(x))


def load(folder):
    folder = Path(folder)
    sb = json.loads((folder / "storyboard.json").read_text())
    scenes = tuple(
        Scene(s["id"], _frac(s["seconds"]), dict(s.get("numbers", {})), s.get("say", ""))
        for s in sb["scenes"]
    )
    sd = json.loads((folder / "style.json").read_text()) if (folder / "style.json").exists() else {}
    if "pace" in sd:
        sd["pace"] = _frac(sd["pace"])
    return Storyboard(sb["question"], scenes), Style(**sd)


def validate(folder):
    """Return a list of problems (empty means the project is sound)."""
    folder = Path(folder)
    problems = []
    try:
        sb, style = load(folder)
    except (OSError, KeyError, ValueError, TypeError, json.JSONDecodeError) as e:
        return [f"cannot read project: {e}"]
    if not sb.question.strip():
        problems.append("the question is empty")
    if not sb.scenes:
        problems.append("there are no scenes")
    if style.fps <= 0 or style.pace <= 0:
        problems.append("fps and pace must be positive")
    seen = set()
    for s in sb.scenes:
        if s.id in seen:
            problems.append(f"{s.id}: the id is used twice")
        seen.add(s.id)
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", s.id):
            problems.append(f"{s.id}: the id must be a plain name such as scene01")
            continue
        if s.seconds <= 0:
            problems.append(f"{s.id}: seconds must be positive")
        for k, v in s.numbers.items():
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                problems.append(f"{s.id}: number '{k}' must be a number")
        path = folder / "scenes" / f"{s.id}.py"
        if not path.exists():
            problems.append(f"{s.id}: the code file scenes/{s.id}.py is missing")
            continue
        used = set(re.findall(r"""numbers\[\s*["']([A-Za-z_0-9]+)["']\s*\]""", path.read_text()))
        for k in sorted(used - set(s.numbers)):
            problems.append(f"{s.id}: the code uses numbers['{k}'] but the storyboard does not give it")
    return problems


def scene_frames(scene, style):
    return int(round(scene.seconds / style.pace * style.fps))


def plan(folder):
    """Plan lines and totals: (lines, total_frames, duration_seconds as Fraction)."""
    sb, style = load(folder)
    lines, start = [], 0
    for s in sb.scenes:
        n = scene_frames(s, style)
        lines.append(f"{s.id}: frames {start} to {start + n - 1} ({n} frames, {float(F(n, style.fps)):.2f} s)")
        start += n
    return lines, start, F(start, style.fps)


def _load_scene(folder, scene_id):
    path = Path(folder) / "scenes" / f"{scene_id}.py"
    spec = importlib.util.spec_from_file_location(f"q2v_scene_{scene_id}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def render(folder, out_dir, every=1):
    """Write SVG frames (every `every`-th frame) to out_dir and return (total_frames, written)."""
    sb, style = load(folder)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    index, written = 0, 0
    for s in sb.scenes:
        mod = _load_scene(folder, s.id)
        n = scene_frames(s, style)
        for i in range(n):
            if index % every == 0:
                t = float(F(i, n - 1)) if n > 1 else 1.0
                svg = mod.draw(t, s.numbers, style)
                (out / f"frame{index:06d}.svg").write_text(svg)
                written += 1
            index += 1
    return index, written


def scaffold(folder, question, scene_ids=("scene01", "scene02", "scene03")):
    folder = Path(folder)
    (folder / "scenes").mkdir(parents=True, exist_ok=True)
    scenes = [{"id": sid, "seconds": 3, "numbers": {"value": 1}, "say": ""} for sid in scene_ids]
    (folder / "storyboard.json").write_text(json.dumps({"question": question, "scenes": scenes}, indent=2) + "\n")
    (folder / "style.json").write_text(json.dumps({
        "width": 1080, "height": 1920, "fps": 30, "pace": 1,
        "background": "#0b1f3a", "text": "#ffffff", "accent": "#ffb703", "font": "sans-serif",
    }, indent=2) + "\n")
    for sid in scene_ids:
        p = folder / "scenes" / f"{sid}.py"
        if not p.exists():
            p.write_text(SCENE_TEMPLATE)
    return folder


SCENE_TEMPLATE = '''def draw(t, numbers, style):
    """t runs from 0 to 1 across this scene. Return one SVG frame as text."""
    w, h = style.width, style.height
    x = int(w * (0.1 + 0.8 * t))
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        f'<rect width="{w}" height="{h}" fill="{style.background}"/>'
        f'<circle cx="{x}" cy="{h // 2}" r="60" fill="{style.accent}"/>'
        f'<text x="{w // 2}" y="{h // 4}" font-size="96" fill="{style.text}" '
        f'font-family="{style.font}" text-anchor="middle">{numbers["value"]}</text></svg>'
    )
'''
