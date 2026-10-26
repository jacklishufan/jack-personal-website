#!/usr/bin/env python3
"""Capture unmodified frames from unified_demo.html and encode them as GIFs.

This does not redraw the demos: every GIF frame is Chrome's screenshot of the
original page at the listed timeline offset.
"""
from pathlib import Path
from subprocess import run
from PIL import Image
import shutil

ROOT = Path(__file__).parent
OUT = ROOT / "gifs"
FRAMES = OUT / ".browser_frames"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
URL = (ROOT / "unified_demo.html").as_uri()

def screenshot(at_ms: int, target: Path):
    run([
        CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
        "--window-size=1280,820", f"--screenshot={target}",
        f"--virtual-time-budget={at_ms}", URL,
    ], check=True)

def capture(name: str, offsets: list[int], durations: list[int]):
    folder = FRAMES / name
    folder.mkdir(parents=True, exist_ok=True)
    paths = []
    for index, offset in enumerate(offsets):
        target = folder / f"{index:03d}.png"
        screenshot(offset, target)
        paths.append(target)
    images = [Image.open(p).convert("P", palette=Image.Palette.ADAPTIVE, colors=256) for p in paths]
    images[0].save(OUT / f"{name}.gif", save_all=True, append_images=images[1:],
                   duration=durations, loop=0, disposal=2, optimize=False)

OUT.mkdir(exist_ok=True)
shutil.rmtree(FRAMES, ignore_errors=True)

# The original T2I tab runs for 8s. Its images appear at the same cadence the
# page uses (0.9s for LaViDa-O, 2.05s for BAGEL); frames are captured directly
# from the running page, including its CSS fades and fixed notice/progress UI.
t2i_times = [100, 900, 1800, 2700, 3600, 4500, 5400, 6300, 7200]
capture("text_to_image_speed", t2i_times, [800] * 8 + [900])

# Detection begins at 8s. These are browser captures of its original typewriter
# output, flashing masks, and bounding-box timing before the tab auto-advances.
grounding_times = [8100, 8500, 8900, 9300, 9700, 10100, 10600, 11100, 11600, 12100, 12600, 13100]
capture("visual_grounding", grounding_times, [400] * 11 + [800])

# The three planning/reflection tabs follow in the page's original auto-advance
# sequence. Each frame remains a direct screenshot of the unmodified HTML.
capture("planning_text_to_image", [14100, 15600, 17100], [1500, 1500, 1500])
capture("planning_image_editing", [18600, 20100, 21600], [1500, 1500, 1500])
capture("self_reflection", [23100, 24600, 26100], [1500, 1500, 1500])

shutil.rmtree(FRAMES, ignore_errors=True)
print(f"Created browser-captured GIFs in {OUT}")
