"""Run offline integration checks in a temporary copy; requires Pillow.
Usage: python3 <skill>/scripts/validate_skill.py
Does not change installed palettes or create artwork in the user's project.
"""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile


def run():
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix='pixel-studio-check-') as work:
        work = Path(work)
        skill = work / 'skill'
        shutil.copytree(root, skill, ignore=shutil.ignore_patterns('__pycache__'))
        sys.path.insert(0, str(skill / 'scripts'))
        from PIL import Image
        from pixelstudio import Sprite, detect_scale
        from lpc import LPCSheet, row_of

        art = work / 'art'
        art.mkdir()
        subprocess.run([sys.executable, str(skill / 'examples/slime-build.py')],
                       cwd=art, check=True, capture_output=True)
        master = art / 'slime.png'
        assert Image.open(master).size == (32, 32)
        assert Image.open(art / 'slime@8x.png').size == (256, 256)
        meta = json.loads((art / 'slime_sheet.json').read_text())
        assert len(meta['frames']) == 4
        assert [f['duration'] for f in meta['frames']] == [160, 90, 120, 90]
        assert meta['meta']['frameTags'][0] == {
            'name': 'idle', 'from': 0, 'to': 3, 'direction': 'forward'}
        with Image.open(art / 'slime_transparent.gif') as gif:
            assert gif.n_frames == 4
            assert [gif.seek(i) or gif.info['duration'] for i in range(4)] == [160, 90, 120, 90]
        s = Sprite.load_project(art / 'slime.pxproj.json')
        assert s.n_frames == 4
        assert s.composite(1).tobytes() == Image.open(master).convert('RGBA').tobytes()
        assert s.stats(print_=False)['semi_alpha_px'] == 0
        before = hashlib.sha256(master.read_bytes()).hexdigest()
        subprocess.run([sys.executable, str(skill / 'examples/slime-build.py')],
                       cwd=art, check=True, capture_output=True)
        assert hashlib.sha256(master.read_bytes()).hexdigest() == before
        im = Image.open(master).convert('RGBA')
        enlarged = im.resize((128, 128), Image.Resampling.NEAREST)
        assert detect_scale(enlarged) == 4
        source = work / 'source.png'
        enlarged.save(source)
        out = work / 'pipe'
        subprocess.run([sys.executable, str(skill / 'scripts/pixelpipe.py'), str(source),
                        '--scale', '4', '--palette', 'gameboy', '--study', 'validation_style',
                        '--out', str(out)], check=True, capture_output=True)
        report = json.loads((out / 'report.json').read_text())
        assert report['true_size'] == [32, 32]
        assert report['palette'] == 'gameboy'
        assert report['after']['colors'] <= 4
        assert report['after']['semi_alpha_px'] == 0
        subprocess.run([sys.executable, str(out / 'build.py')], cwd=out,
                       check=True, capture_output=True)
        learned = skill / 'references/learned/palettes.json'
        assert 'validation_style' in json.loads(learned.read_text())
        env = dict(os.environ, PYTHONPATH=str(skill / 'scripts'))
        subprocess.run([sys.executable, '-c',
                        'from pixelstudio import Sprite; Sprite(4,4,palette="validation_style")'],
                       check=True, env=env, capture_output=True)
        sheet = LPCSheet()
        assert len(list(sheet.slots())) == 178
        assert row_of('walk', 'down') == 10
        sheet.place('walk', 'down', 0, im)
        sheet.save(work / 'lpc.png')
        assert Image.open(work / 'lpc.png').size == (832, 1344)
        oversized = Image.new('RGBA', (65, 65), 'red')
        try:
            sheet.place('walk', 'down', 1, oversized)
        except ValueError:
            pass
        else:
            raise AssertionError('oversized LPC crop accepted')
    print('PASS: animation/export metadata, project roundtrip, deterministic rebuild, scale recovery, cleanup, study/palette reload, LPC layout and rejection')


if __name__ == '__main__':
    run()
