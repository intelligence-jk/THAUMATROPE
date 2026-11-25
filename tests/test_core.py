import json
import shutil
from fractions import Fraction as F
from pathlib import Path

from q2v import load, plan, render, scaffold, validate
from q2v.__main__ import main

EX = Path(__file__).resolve().parent.parent / "examples" / "percent"


def copy_example(tmp_path):
    dst = tmp_path / "p"
    shutil.copytree(EX, dst)
    return dst


def test_example_is_valid():
    assert validate(EX) == []


def test_frame_maths_exact():
    lines, total, dur = plan(EX)
    # 3 s, 4 s and 2.5 s at 30 fps
    assert lines[0].startswith("scene01: frames 0 to 89 (90 frames")
    assert lines[1].startswith("scene02: frames 90 to 209 (120 frames")
    assert lines[2].startswith("scene03: frames 210 to 284 (75 frames")
    assert total == 285
    assert dur == F(19, 2)  # 9.5 seconds exactly


def test_restyle_is_one_edit_pace_and_fps(tmp_path):
    p = copy_example(tmp_path)
    style = json.loads((p / "style.json").read_text())
    style["fps"] = 60
    (p / "style.json").write_text(json.dumps(style))
    assert plan(p)[1:] == (570, F(19, 2))  # twice the frames, same length
    style["pace"] = 2
    (p / "style.json").write_text(json.dumps(style))
    total, dur = plan(p)[1:]
    # 3/2 s = 90 frames, 4/2 = 120, 2.5/2 s = 75 frames at 60 fps
    assert (total, dur) == (285, F(19, 4))


def test_decimal_seconds_are_exact(tmp_path):
    p = copy_example(tmp_path)
    sb = json.loads((p / "storyboard.json").read_text())
    sb["scenes"][0]["seconds"] = 0.1  # 0.1 s is exactly 1/10 here, not a float
    (p / "storyboard.json").write_text(json.dumps(sb))
    sb_loaded, _ = load(p)
    assert sb_loaded.scenes[0].seconds == F(1, 10)
    assert plan(p)[0][0].startswith("scene01: frames 0 to 2 (3 frames")


def test_missing_scene_file_and_number(tmp_path):
    p = copy_example(tmp_path)
    (p / "scenes" / "scene02.py").unlink()
    assert any("scene02" in x and "missing" in x for x in validate(p))
    sb = json.loads((p / "storyboard.json").read_text())
    del sb["scenes"][2]["numbers"]["answer"]
    (p / "storyboard.json").write_text(json.dumps(sb))
    assert any("numbers['answer']" in x for x in validate(p))


def test_duplicate_ids_and_bad_values(tmp_path):
    p = copy_example(tmp_path)
    sb = json.loads((p / "storyboard.json").read_text())
    sb["scenes"][1]["id"] = "scene01"
    sb["scenes"][0]["seconds"] = 0
    sb["scenes"][2]["numbers"]["answer"] = "30"
    (p / "storyboard.json").write_text(json.dumps(sb))
    text = " ".join(validate(p))
    assert "used twice" in text and "seconds must be positive" in text and "must be a number" in text


def test_unreadable_project(tmp_path):
    assert validate(tmp_path / "nothing")[0].startswith("cannot read project")


def test_scaffold_then_check_and_render(tmp_path):
    p = tmp_path / "new"
    scaffold(p, "What is 2 + 2?")
    assert validate(p) == []
    assert plan(p)[1] == 270  # 3 scenes of 3 s at 30 fps
    total, written = render(p, tmp_path / "out", every=90)
    assert (total, written) == (270, 3)
    svg = (tmp_path / "out" / "frame000000.svg").read_text()
    assert svg.startswith("<svg") and "<circle" in svg


def test_render_every_frame_count_on_example(tmp_path):
    total, written = render(EX, tmp_path / "o", every=100)
    assert total == 285 and written == 3  # frames 0, 100, 200


def test_cli(tmp_path, capsys):
    assert main(["check", str(EX)]) == 0
    assert main(["plan", str(EX)]) == 0
    assert "Total: 285 frames, 9.50 s (0:09)" in capsys.readouterr().out
    assert main(["render", str(EX), str(tmp_path / "f"), "--every", "95"]) == 0
    assert "Wrote 3 SVG frames" in capsys.readouterr().out
    assert main(["check", str(tmp_path / "none")]) == 1
    assert main([]) == 2
