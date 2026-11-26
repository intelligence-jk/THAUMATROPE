# MUSE: Maths Understood through Scenes and Explanations

Formerly `question-to-video`.

A starter for turning one maths question into a short video drawn entirely in code. No paid service, no model, no account.

## What it solves
A video made from code gets messy fast: numbers hidden inside drawing code, one giant script, colours changed in twenty places. This starter keeps four habits so a video stays easy to change:

1. One storyboard file (`storyboard.json`): the question, and for each scene its length and the numbers it shows.
2. One code file per scene (`scenes/scene01.py`, `scene02.py`, ...): a change touches one scene.
3. One style file (`style.json`): size, fps, pace and colours, so restyling the whole video is one edit.
4. A render step that prints the frame count and duration before you spend any time rendering.

It checks the project (every scene has its code file, every number a scene's code asks for is in the storyboard) and does the frame maths exactly with `Fraction`. Pure Python 3.10+, standard library only. The scene files here draw SVG frames; turning frames into a video uses free tools (below).

## Example
The folder `examples/percent` asks "What is 12 percent of 250?" in three scenes.
```bash
python -m q2v check examples/percent
python -m q2v render examples/percent frames --every 100
```
Output of a real run:
```
OK
scene01: frames 0 to 89 (90 frames, 3.00 s)
scene02: frames 90 to 209 (120 frames, 4.00 s)
scene03: frames 210 to 284 (75 frames, 2.50 s)
Total: 285 frames, 9.50 s (0:09)
Wrote 3 SVG frames to frames
```
(`--every 100` writes only every 100th frame, so a quick look costs almost nothing; leave it out to write all 285.)

Start your own project:
```bash
python -m q2v init my-video "What is 2 + 2?"
```
This writes the storyboard, the style file and three scene files to edit.

## The maths behind it
A scene lasting s seconds at f frames per second, at pace p, has round(s / p x f) frames. With 3 s at 30 fps that is 3 x 30 = 90 frames, with 4 s it is 120 and with 2.5 s it is 75, so the video has 90 + 120 + 75 = 285 frames and lasts 285 / 30 = 19/2 = 9.5 seconds. Seconds are read as exact fractions from the text (0.1 is exactly 1/10, not a binary float), so the totals never drift. Doubling the fps doubles the frames and leaves the duration alone; doubling the pace halves the duration (the tests check both). Inside a scene, `t` runs from 0 at the first frame to 1 at the last: frame i of n has t = i / (n - 1).

## Make the video with free tools
Render all the SVG frames, convert them to PNG with any free converter (for example `rsvg-convert` or Inkscape), then join them with FFmpeg at the fps in your style file:
```bash
python -m q2v render my-video frames
for f in frames/*.svg; do rsvg-convert "$f" -o "${f%.svg}.png"; done
ffmpeg -framerate 30 -i frames/frame%06d.png -pix_fmt yuv420p out.mp4
```
Add narration and music afterwards with your own recordings. This repository contains no voice files, brand assets or paid tools.

## Install and run
```bash
python -m pip install -e .
python -m pytest
```
The tests check the storyboard reading and the frame maths and write only a handful of tiny SVG files; nothing is rendered to video.

## Licence
MIT. Made by Math & Myth (mathandmyth.ae): one to one maths mentoring, online, across the UAE.
