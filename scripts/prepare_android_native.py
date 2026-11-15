"""Prepare reviewed sources for Android 16KB rebuilds; never change app pins."""

import argparse
import hashlib
import json
import shutil
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SOURCES = {
    'pydantic_core': {
        'version': '2.41.4',
        'url': 'https://files.pythonhosted.org/packages/df/18/d0944e8eaaa3efd0a91b0f1fc537d3be55ad35091b6a87638211ba691964/pydantic_core-2.41.4.tar.gz',
        'sha256': '70e47929a9d4a1905a67e4b687d5946026390568a8e952b92824118063cee4d5',
        'checksum_source': 'https://pypi.org/pypi/pydantic-core/2.41.4/json',
    },
    'freetype': {
        'version': '2.15.0',
        'commit': '37515cf56ba3349656049edbed89ffc6f6466f2d',
        'url': 'https://codeload.github.com/freetype/freetype/tar.gz/37515cf56ba3349656049edbed89ffc6f6466f2d',
    },
    'libpng': {
        'version': '1.6.59',
        'commit': 'cd952f49f95bb27154ae77dbb103032d95f6e580',
        'url': 'https://codeload.github.com/pnggroup/libpng/tar.gz/cd952f49f95bb27154ae77dbb103032d95f6e580',
    },
    'openblas': {
        'version': '0.3.34',
        'commit': 'e0166008be8e466242aa76b2ff75ce3f0fbf574a',
        'url': 'https://github.com/OpenMathLib/OpenBLAS/releases/download/v0.3.34/OpenBLAS-0.3.34.tar.gz',
        'sha256': 'cd7e129868320cc2d033afa920e31202dfe0b8066a5b66661900ccc0f197dfed',
        'checksum_source': 'https://api.github.com/repos/OpenMathLib/OpenBLAS/releases/tags/v0.3.34',
    },
}


def prepare(output):
    output.mkdir(parents=True, exist_ok=False)
    scripts = Path(__file__).resolve().parent
    contract = scripts.parent / 'android/native-consumer-contract.json'
    data = contract.read_bytes()
    (output / 'consumer-contract.json').write_bytes(data)
    manifest = {
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'consumer_contract_sha256': hashlib.sha256(data).hexdigest(),
        'sources': {},
    }
    for name, source in SOURCES.items():
        request = urllib.request.Request(source['url'], headers={'User-Agent': 'Fuorigiri-Android-build'})
        with urllib.request.urlopen(request, timeout=120) as response:
            data = response.read()
        digest = hashlib.sha256(data).hexdigest()
        if source.get('sha256', digest) != digest:
            raise ValueError(f'Source checksum mismatch: {name}')
        filename = name + '.tar.gz'
        (output / filename).write_bytes(data)
        manifest['sources'][name] = dict(
            source,
            filename=filename,
            sha256=digest,
            checksum_kind='publisher-metadata' if 'checksum_source' in source else 'observed-download-pinned-commit',
        )
        print(f'{name} {source["version"]}: {digest}', flush=True)
    for name in [
        'build_android_native.py',
        'android_native_tools.py',
        'build_android_pillow.py',
        'audit_android_native.py',
        'check_android_native_runtime.py',
    ]:
        shutil.copy2(scripts / name, output / name)
    shutil.copy2(scripts.parent / 'docs/ANDROID_NATIVE_16KB.md', output / 'README.md')
    (output / 'sources.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(f'Prepared: {output.resolve()}. Sources only; no qualified wheel or APK.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    prepare(parser.parse_args().output)
