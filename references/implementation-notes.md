# Source-verified implementation notes

These details take precedence over general claims in inherited references.

## Drawing and export

- `Sprite` frames are **1-based**, including `frame`, `composite`, `tag`, and duration lists. Drawing hits the current frame and layer. Coordinates are zero-based, y downward.
- `add_frame(copy=True)` copies and selects the new frame; returns its integer index, not the Sprite. `copy_cel(link=True)` shares the image object across frames.
- `dither(x0,y0,x1,y1,c1,c2,...)` and `gradient_dither(x0,y0,x1,y1,colors,...)` take separate coordinates, not a box tuple. `"keep"` is special to dither, not a general color.
- `save_png()` defaults to the CURRENT frame. Select `frame=1` explicitly for a master still when animation finishes on another frame.
- `save_spritesheet()` writes an Aseprite-style JSON **array** of frames named `frame_0`, etc.; exported tag indices are zero-based. This is metadata, not an `.aseprite` file. Check the chosen engine/importer supports this array schema; do not guarantee automatic engine compatibility.
- GIF tag playback expands ping-pong/reverse; sheets retain ascending physical frame order and describe playback in tags. Inspect both timing and frame order.
- Use positive INTEGER export scales. `_scaled()` coerces via `int(scale)` rather than rejecting every fractional value; the caller enforces the integer rule.
- `stats()` counts colors/semi-alpha across frames, but isolated-pixel coordinates only for the current frame, truncated to 20; near-color pairs are truncated to 10. Inspect all relevant frames.
- `save_project` preserves frames/layers/palettes/tags as JSON with base64 PNG cels. It is not the editable procedural build script.

## Import, cleanup, and study

- `from_png` loads one image, not an animation sequence or automatic sheet slicer. Scale auto-detection is heuristic. Supply the known scale if available and visually verify native dimensions.
- Non-integer import scales use `block_downscale`: dominant-color buckets (5 bits/channel), averaging within the winning bucket. Older prose calling this center sampling is inaccurate.
- `strip_checker` removes qualifying bright near-gray pixels throughout the image. It does not detect spatial checkerboard patterns or flood-fill only the background. Preserve the input, compare before/after, and leave stripping off if white details disappear.
- Despeckle removes small connected OPAQUE components, regardless of color; intentional detached sparkles can disappear. It does not remove a contrasting eye pixel connected to the body merely because its color differs. Checker stripping can remove pale eye details. Tune each step against before/after images.
- `clean` order: flatten → harden → despeckle → dedupe → optional dehalo → palette/quantize. `quantize` also flattens. Preserve a project before destructive cleanup if editable part layers matter. Cleanup methods default to the current cel; apply explicit frame/layer selection when processing an existing animation.
- `pixelpipe` defaults: max colors 24, display 6, despeckle 2, dedupe 10, harden on; `--dehalo` is opt-in. Unknown `--palette` prints a warning and falls back to max-colors: verify the report rather than claiming a successful palette lock.
- `pixelpipe --out DIR` controls outputs; default is `<input-stem>_pipe/`. The generated build.py stores absolute source and skill paths: keep the input available; update paths if relocating. Run that build from its output directory.
- `study.py` defaults to `<input-stem>_study/`; `--out` overrides. It prints a skeleton, not a finished style card. It analyzes the first image only. An all-transparent image can fail swatch rendering (no palette); do not treat it as a completed study.
- `pixelpipe --study NAME` analyzes clean.png, writes analysis images/report under output/study, saves `<skill>/references/learned/palettes.json`, and PRINTS a proposed card path/skeleton. It does **not** create the card or update INDEX.md. Inspect zoom/swatch, write an imperative card using TEMPLATE.md, and update INDEX.md yourself.
- Learned palettes load when `pixelstudio` is imported. Start a fresh process after saving a palette; an already imported module does not automatically reload it. Durable learning belongs under this skill, not just beside the source image. Merely cleaning an image does not request new durable style rules.

## LPC adapter

- Sprite frames are 1-based; **LPC action frame slots are 0-based**.
- 64px cells, 13 columns × 21 rows = 832×1344. Directions up/left/down/right. Spellcast 7, thrust 8, walk 9 (0 idle), slash 6, shoot 13; hurt 6, down only. Partial sheets remain transparent.
- `place` tightly crops EACH pose and centers its visible bounding box. It does not preserve a fixed anatomical pivot across poses. `feet=58` means the usual last occupied row is 57 (exclusive bottom at 58), rather than the inherited prose's literal bottom row 58. Large crops clamp placement toward row 0.
- Check feet and weapon-hand drift across the rendered row. If stable pivots are required, compose directly into a fixed 64px cell using a shared origin and paste into the known sheet row/column, then use the adapter's export metadata. Do not promise automatic anchoring from `place`.
- Crops over 64px raise ValueError. A generous scratch canvas prevents early drawing clipping but does not enlarge the final LPC cell. If reach must exceed it, explain the layout conflict and use an agreed oversized action format instead of silently clipping.
- This package supplies the LPC layout adapter, not third-party LPC artwork or asset licenses.

## Visual review in Codex

Inspect PNG previews through the available image viewer. Review animation playback when a viewer supports it; otherwise inspect extracted frames/contact sheets and durations, and disclose that playback was not observed. Do not claim to have watched three loops from a static image. Keep upstream's 2–3 see/critique/fix passes for art tasks; counts and successful exports alone do not establish visual quality.
