"""python -m q2v init FOLDER "question" | check FOLDER | plan FOLDER | render FOLDER OUT_DIR [--every N]"""
import sys

from .core import plan, render, scaffold, validate


def _plan_text(folder):
    lines, total, dur = plan(folder)
    out = list(lines)
    out.append(f"Total: {total} frames, {float(dur):.2f} s ({int(dur // 60)}:{int(dur % 60):02d})")
    return "\n".join(out)


def main(argv=None) -> int:
    a = sys.argv[1:] if argv is None else argv
    if a[:1] == ["init"] and len(a) == 3:
        scaffold(a[1], a[2])
        print(f"Created {a[1]}/storyboard.json, style.json and 3 scene files")
        return 0
    if a[:1] in (["check"], ["plan"], ["render"]) and len(a) >= 2:
        problems = validate(a[1])
        if problems:
            print("\n".join(problems), file=sys.stderr)
            return 1
        if a[0] == "check":
            print("OK")
        elif a[0] == "plan":
            print(_plan_text(a[1]))
        else:
            if len(a) < 3:
                print(__doc__, file=sys.stderr)
                return 2
            every = int(a[a.index("--every") + 1]) if "--every" in a else 1
            total, written = render(a[1], a[2], every)
            print(_plan_text(a[1]))
            print(f"Wrote {written} SVG frames to {a[2]}")
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
