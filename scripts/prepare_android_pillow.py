"""Prepare a source kit, never install wheels or change the application's pins."""
import argparse
import hashlib
import json
import shutil
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


SOURCES = {
    'pillow': {
        'version': '13.0.0',
        'url': 'https://files.pythonhosted.org/packages/ce/a4/9cc30690a394a8305e8be4c9036aa16d0dfddadd09079860b582f562496d/pillow-13.0.0.tar.gz',
        'sha256': 'cdcd1ba258178f7356d74170c9a81ba4eab6a5d55748bc402a5a2a6fe6be3510',
        'checksum_source': 'https://pypi.org/pypi/pillow/13.0.0/json',
    },
    'jpeg': {
        'version': '3.2.0',
        'commit': 'c85e6b905bf237038faa936dab160ebfc5da0344',
        'url': 'https://github.com/libjpeg-turbo/libjpeg-turbo/releases/download/3.2.0/libjpeg-turbo-3.2.0.tar.gz',
        'sha256': '6f30092cef9fb839779646608f4ee14ae3cbac989c47fa05e841b0841f09878e',
        'checksum_source': 'https://api.github.com/repos/libjpeg-turbo/libjpeg-turbo/releases/tags/3.2.0',
    },
    'freetype': {
        'version': '2.14.3',
        'commit': '0a0221a1347e2f1e07c395263540026e9a0aa7c7',
        'url': 'https://codeload.github.com/freetype/freetype/tar.gz/0a0221a1347e2f1e07c395263540026e9a0aa7c7',
    },
}


def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'Fuorigiri-Android-build'})
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def prepare(output):
    output.mkdir(parents=True, exist_ok=False)
    manifest = {'created_utc': datetime.now(timezone.utc).isoformat(), 'sources': {}}
    # Keep the original responses as evidence, including package availability.
    metadata = fetch('https://pypi.org/pypi/pillow/13.0.0/json')
    (output / 'pypi-pillow-13.0.0.json').write_bytes(metadata)
    index = fetch('https://chaquo.com/pypi-13.1/pillow/')
    (output / 'chaquopy-pillow.html').write_bytes(index)
    published = json.loads(metadata)
    sdist = next(f for f in published['urls'] if f['packagetype'] == 'sdist')
    if sdist['digests']['sha256'] != SOURCES['pillow']['sha256']:
        raise ValueError('Pillow sdist differs from the reviewed PyPI digest')
    for name, source in SOURCES.items():
        data = fetch(source['url'])
        digest = hashlib.sha256(data).hexdigest()
        if source.get('sha256', digest) != digest:
            raise ValueError(f'Checksum mismatch: {name}')
        filename = f'{name}.tar.gz'
        (output / filename).write_bytes(data)
        manifest['sources'][name] = dict(source, filename=filename, sha256=digest,
            checksum_kind=('publisher-PyPI' if name == 'pillow' else
                           'publisher-GitHub-release' if name == 'jpeg' else
                           'observed-download-pinned-commit'))
    for name in ['build_android_pillow.py', 'check_android_pillow_runtime.py', 'scan_build_paths.py', 'android_neutral_env.sh']:
        shutil.copy2(Path(__file__).with_name(name), output / name)
    shutil.copy2(Path(__file__).resolve().parents[1] / 'docs/ANDROID_PILLOW.md', output / 'README.md')
    (output / 'sources.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(f'Source kit: {output.resolve()} (not a qualified wheel or APK)')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New directory only')
    prepare(parser.parse_args().output)
