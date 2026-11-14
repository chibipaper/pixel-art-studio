# SkillSpector 2.12.0 review — 2026-11-14

Scope: supplied scan (19 issue instances), compared against the default-branch
repository source. This is a focused source review, not a penetration test or a
claim of safety. No untrusted generated script was executed during review.

Classification key: **Confirmed security risk**, **False positive**,
**Inspection limitation**, **Requires further investigation**.

| # | Scanner location / ID | Classification | Evidence, disposition |
|---|---|---|---|
| 1 | SKILL.md:50 AE1 | Inspection limitation | Scanner cannot fully interpret `pixel-art/capybara-4dir/preview.png`; binary inspection is outside analyzer coverage; no malicious behavior demonstrated. |
| 2 | SKILL.md:54 AE1 | Inspection limitation | Same PNG, duplicate reference; no second independent exploit. Review image decoder behavior separately. |
| 3 | scripts/validate_skill.py:67 E2 | False positive | `dict(os.environ, PYTHONPATH=...)` was used to pass process environment to a local child, not harvesting/transmitting secrets. Still unnecessarily broad; replaced with a limited child environment. |
| 4 | README.md:41 RA2 | False positive | Virtual environment setup is documented installation, not cron/startup/session persistence. Saved palettes are a separate intentional durable feature, now gated by consent in the skill policy. |
| 5 | SKILL.md:1 LP3 | Confirmed security risk | Agent instructions previously invited broad shell/file/install actions without explicit scope. Documented least privilege and consent. Metadata cannot enforce OS/tool sandbox permissions across hosts. |
| 6 | examples/slime-bounce.py:6 SDI-2 | Confirmed security risk | Absolute developer path could load unrelated `pixelstudio` code. Now repository-relative. |
| 7 | pixel-art/anime-cast/build.py:8 SDI-2 | Confirmed security risk | Same absolute developer path; now repository-relative. |
| 8 | pixel-art/capybara-4dir/build.py:8 SDI-2 | Confirmed security risk | Same absolute developer path; now repository-relative. |
| 9 | pixel-art/catmage-lpc/build.py:8 SDI-2 | Confirmed security risk | Same path imports `pixelstudio` and `lpc`; now repository-relative. |
| 10 | scripts/validate_skill.py:28 AST4 | False positive | Explicit argv, no shell expansion; checked-in slime example. Added narrow environment and timeout for defense in depth. |
| 11 | scripts/validate_skill.py:46 AST4 | False positive | Rebuilds same checked-in example to test determinism; no shell expansion. Hardened child settings. |
| 12 | scripts/validate_skill.py:55 AST4 | False positive | Executes checked-in `pixelpipe.py` with explicit argv; input is a generated test PNG. Hardened child settings. |
| 13 | scripts/validate_skill.py:63 AST4 | Confirmed security risk | Ran an output-directory `build.py` generated during validation, crossing from generated text into execution. Replaced with `ast.parse` syntax check, without execution. |
| 14 | scripts/validate_skill.py:68 AST4 | False positive | Fixed `-c` command checks palette loading; no interpolated shell input. Replaced full inherited environment with explicit variables. |
| 15 | SKILL.md:96 SQP-3 | False positive | Thai example is a multilingual user-intent trigger, not an instruction override or malicious action. Retained. |
| 16 | docs/index.html:2 SQP-3 | False positive | HTML `lang="en"` declares document language; not coercive language choice. Retained. |
| 17 | examples/knight-walkcycle.py:90 SQP-2 | False positive | Explicit documented animation export writes; not covert file manipulation. Destination must still be reviewed by user. |
| 18 | examples/tall-iron-man-repulsor.py:199 SQP-2 | False positive | Normal PNG/GIF output generation, consistent with example's purpose. |
| 19 | examples/tall-iron-man-repulsor.py:223 SQP-2 | False positive | Writes validation JSON as documented output; no secret disclosure shown. |

Additional source review identified a fifth hardcoded path in
`pixel-art/knight-spear-lpc/build.py` not separately listed by the scanner. Fixed.

## Trust boundaries / remaining risks

- Generated `build.py` remains intentionally emitted by `pixelpipe` and is editable
  Python. It **must not be auto-executed**. `ast.parse` checks syntax only, not safety.
- The validator still executes a small set of **checked-in** examples and the checked-in
  pipeline. That is intentional functional coverage, not secure sandboxing.
- Python scripts (and Python imports) retain normal host filesystem, subprocess and
  network privileges. A Markdown policy cannot technically constrain a host agent;
  use OS/container isolation and agent tool controls, with network disabled when needed.
- `pixelpipe` embeds a resolved source install path in generated scripts so that
  relocated outputs can still be regenerated. Review that path before running;
  executing a generator from an untrusted installation is not safe.
- Image processing uses Pillow to decode potentially malformed files; binary image
  decoding was outside SkillSpector's inspection. Keep Pillow updated and process
  untrusted images within a restricted workspace/container.
- `study.py --save-palette` intentionally persists learned data under the skill
  installation. Require explicit user consent for persistent learning.
- Dependency version bounds are not hash locks or a software bill of materials.
  Verify package provenance on installation. No network or dependency install is
  needed during normal artwork generation once Pillow is installed.
- Symlinks and arbitrary output paths can still target locations outside the workspace
  when run as unrestricted Python. The agent must check them, or the host must enforce
  filesystem isolation. This PR does not attempt to sandbox arbitrary user scripts.
- Scanner exclusions include `.git` metadata and numerous binary PNG/GIF assets; two
  AE1 reports are duplicate limitations, not verified compromises.

## Regression validation

- `python -m unittest discover -s tests -v` — static safeguards and subprocess environment.
- `python scripts/validate_skill.py` — checked-in slime animation/GIF/spritesheet
  metadata, deterministic rebuild, pixelpipe cleanup/study, LPC layout; generated
  pipeline build syntax is checked but never run.
- Run in an isolated CI worker using Pillow. The maintainers should visually inspect
  representative existing examples (including four-direction capybara and LPC builds)
  for unchanged appearance; full bytewise comparison of all binary assets was not done.
- Passing tests does **not** establish the repository is secure.
