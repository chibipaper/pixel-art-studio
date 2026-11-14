# Validation

Validated 2026-11-14 with Python 3 and Pillow 12.2.0.

- Codex skill-creator quick_validate.py: passed frontmatter/name/scaffold checks.
- `python3 <skill>/scripts/validate_skill.py`: passed real four-frame example execution, native/display dimensions, GIF frame count and timing, JSON frame rectangles/tag indices, project reload pixel equality, repeat-build master checksum, exact 4x grid recovery, palette lock/color budget/hard alpha, generated cleanup build execution, durable palette save and fresh-process reload, LPC dimensions/slots/row mapping and oversized-pose rejection. Uses a temporary skill copy so tests do not pollute learning.
- Four inherited tools verified against their GitHub blob SHA at the pinned commit (see provenance.md): no engine modifications.
- A no-skill baseline evaluator could not determine library imports, indexing, exports, or --study persistence from the name alone. This was a knowledge-gap baseline, not an observed rule violation. The entrypoint and implementation notes supply these specifics.

Structural and integration checks do not prove artistic quality. Future artwork still
requires the visual critique loop, and GIF playback review requires an animation-capable
viewer. Engine-specific imports were not tested in Unity/Godot/Phaser. Python 3.9 and
Pillow 9 are the upstream minimums, not a tested version matrix.

Independent forward test: a fresh agent used the installed skill through an isolated
copy to build four 16px frames, inspect two contact-sheet passes, export PNG/GIF/sheet,
and reload the project with per-frame pixel equality. It exercised --study and verified
the fresh-process learned palette, plus absence of an automatically generated card or
index entry. GIF playback was not observed. Reviewer findings about scale/importer
prose were incorporated. Its claim that despeckle removes same-color clusters was
checked against source and rejected: it operates on connected opaque components.
Pillow 12.2 emits upstream getdata deprecation warnings; Pillow 14 is not validated.
