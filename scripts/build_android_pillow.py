"""Experimental Fedora build: one ABI per new output directory. No APK or signing."""

import argparse
import hashlib
import json
import os
import platform
import shlex
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path


def unpack(archive, destination, expected):
    if hashlib.sha256(archive.read_bytes()).hexdigest() != expected:
        raise ValueError(f'Source checksum mismatch: {archive.name}')
    destination.mkdir(exist_ok=False)
    with tarfile.open(archive) as source:
        source.extractall(destination, filter='data')
    roots = list(destination.iterdir())
    if len(roots) != 1 or not roots[0].is_dir():
        raise ValueError(f'Unexpected source layout: {archive.name}')
    return roots[0]


def run(command, cwd, log, env=None):
    with log.open('a', encoding='utf-8') as stream:
        stream.write('\n' + repr([str(c) for c in command]) + '\n')
        stream.flush()
        subprocess.run([str(c) for c in command], cwd=cwd, env=env, stdout=stream, stderr=subprocess.STDOUT, check=True)


def build(kit, output, abi):
    if sys.platform != 'linux':
        raise SystemExit('Run inside the Fedora Toolbox, after sourcing ambiente.sh')
    if sys.version_info < (3, 12):
        raise SystemExit('Host Python >= 3.12 required for safe tar extraction')
    kit, output = kit.resolve(), output.resolve()
    if output.exists():
        raise SystemExit('Output already exists: preserved; choose a new directory')
    home = Path.home().resolve()
    if output.is_relative_to(home) or output.is_relative_to(Path('/var/home')):
        # Static libjpeg/FreeType embed source paths: build under a neutral root.
        raise SystemExit(
            'Output under a home directory: use a neutral root such as /build/<id> (see ANDROID_WHEEL_FEDORA.md)'
        )
    ndk = Path(os.environ.get('ANDROID_NDK_ROOT', '__missing__')).resolve()
    toolchain = ndk / 'build/cmake/android.toolchain.cmake'
    tools = ndk / 'toolchains/llvm/prebuilt/linux-x86_64/bin'
    if not toolchain.is_file() or not (tools / 'llvm-readelf').is_file():
        raise SystemExit('Android NDK missing: restore ambiente.sh first')
    for name in ['cmake', 'ninja', 'java']:
        if not shutil.which(name):
            raise SystemExit(f'Build tool missing: {name}')
    subprocess.run([sys.executable, '-c', 'import cibuildwheel'], check=True)
    manifest = json.loads((kit / 'sources.json').read_text(encoding='utf-8'))
    output.mkdir(parents=True)
    log = output / 'build.log'
    provenance = {
        'status': 'build-started-not-runtime-qualified',
        'abi': abi,
        'api': 26,
        'python': '3.13',
        'host_python': sys.version,
        'host': platform.platform(),
        'sources': manifest,
        'ndk': (ndk / 'source.properties').read_text(),
        'wheels': {},
    }
    report = output / 'build.json'
    report.write_text(json.dumps(provenance, indent=2) + '\n')
    for command in [
        [sys.executable, '-m', 'pip', 'freeze'],
        ['cmake', '--version'],
        ['java', '-version'],
        [tools / 'clang', '--version'],
    ]:
        run(command, output, log)
    sources = {
        name: unpack(kit / item['filename'], output / name, item['sha256'])
        for name, item in manifest['sources'].items()
    }
    prefix = output / 'target'
    cmake_abi = 'arm64-v8a' if abi == 'arm64_v8a' else 'x86_64'
    common = [
        f'-DCMAKE_TOOLCHAIN_FILE={toolchain}',
        f'-DANDROID_ABI={cmake_abi}',
        '-DANDROID_PLATFORM=android-26',
        '-DANDROID_SUPPORT_FLEXIBLE_PAGE_SIZES=ON',
        '-DCMAKE_BUILD_TYPE=Release',
        '-DCMAKE_POSITION_INDEPENDENT_CODE=ON',
        f'-DCMAKE_INSTALL_PREFIX={prefix}',
        '-DCMAKE_INSTALL_LIBDIR=lib',
        '-DBUILD_SHARED_LIBS=OFF',
        f'-DCMAKE_C_FLAGS=-ffile-prefix-map={home}=/home/builder',
    ]
    for name, options in [
        ('jpeg', ['-DENABLE_SHARED=OFF', '-DENABLE_STATIC=ON', '-DWITH_TURBOJPEG=OFF', '-DWITH_SIMD=OFF']),
        (
            'freetype',
            [
                '-DFT_DISABLE_ZLIB=ON',
                '-DFT_DISABLE_BZIP2=ON',
                '-DFT_DISABLE_PNG=ON',
                '-DFT_DISABLE_HARFBUZZ=ON',
                '-DFT_DISABLE_BROTLI=ON',
            ],
        ),
    ]:
        binary = output / f'{name}-build'
        run(['cmake', '-S', sources[name], '-B', binary, '-G', 'Ninja', *common, *options], output, log)
        run(['cmake', '--build', binary, '--parallel', '4'], output, log)
        run(['cmake', '--install', binary], output, log)
    # cibuildwheel resets compiler flags. Place only Android files in its target
    # prefix, as with the existing CFFI build. Never copy host headers/libraries.
    hook = output / 'prepare_target.py'
    triplet = 'aarch64-linux-android' if abi == 'arm64_v8a' else 'x86_64-linux-android'
    hook.write_text(
        '''import pathlib, shutil, sysconfig
prefix = pathlib.Path(sysconfig.get_config_var('prefix')).resolve()
assert sysconfig.get_platform().startswith('android-'), 'Not Android'
assert 'cibw-run-' in str(prefix), 'Unexpected target prefix'
source = pathlib.Path('''
        + repr(str(prefix))
        + ''')
shutil.copytree(source / 'include', prefix / 'include', dirs_exist_ok=True)
shutil.copytree(source / 'lib', prefix / 'lib', dirs_exist_ok=True)
sysroot = pathlib.Path('''
        + repr(str(tools.parent / 'sysroot'))
        + ''')
for name in ['zlib.h', 'zconf.h']:
    shutil.copy2(sysroot / 'usr/include' / name, prefix / 'include' / name)
shutil.copy2(sysroot / 'usr/lib' / '''
        + repr(triplet)
        + ''' / '26/libz.so', prefix / 'lib/libz.so')
''',
        encoding='utf-8',
    )
    config = output / 'cibuildwheel.toml'
    config.write_text(
        '''[tool.cibuildwheel]
build-frontend = "build"
before-all = ""
before-build = '''
        + json.dumps('python ' + shlex.quote(hook.as_posix()))
        + '''
test-command = ""
test-requires = []
test-extras = []
config-settings = { platform-guessing="disable", jpeg="enable", zlib="enable", freetype="enable", raqm="disable", lcms="disable", webp="disable", jpeg2000="disable", tiff="disable", imagequant="disable", xcb="disable", avif="disable" }
''',
        encoding='utf-8',
    )
    env = dict(os.environ)
    # Do not inherit CIBW overrides from the cryptography/CFFI session.
    for key in list(env):
        if key.startswith('CIBW_'):
            del env[key]
    env.update(ANDROID_API_LEVEL='26', CIBW_ENVIRONMENT="LDFLAGS='-Wl,-z,max-page-size=16384' PKG_CONFIG=/bin/false")
    wheelhouse = output / 'wheelhouse'
    run(
        [
            sys.executable,
            '-m',
            'cibuildwheel',
            sources['pillow'],
            '--only',
            f'cp313-android_{abi}',
            '--config-file',
            config,
            '--output-dir',
            wheelhouse,
        ],
        output,
        log,
        env,
    )
    wheels = list(wheelhouse.glob(f'pillow-13.0.0-cp313-cp313-android_*_{abi}.whl'))
    if len(wheels) != 1:
        raise ValueError('Expected exactly one Pillow cp313 Android wheel')
    # Preserve readelf output for every native object. Runtime and dependency
    # closure remain separate gates; a compiler success cannot close them.
    import zipfile

    extracted = output / 'wheel-audit'
    with zipfile.ZipFile(wheels[0]) as archive:
        if archive.testzip():
            raise ValueError('Wheel CRC failed')
        for name in archive.namelist():
            if name.endswith('.so'):
                target = extracted / Path(name).name
                target.parent.mkdir(exist_ok=True)
                target.write_bytes(archive.read(name))
                run([tools / 'llvm-readelf', '-h', '-d', '-lW', target], output, output / 'elf.txt')
    provenance.update(
        status='compiled-pending-ELF-review-and-runtime',
        wheels={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in wheels},
    )
    report.write_text(json.dumps(provenance, indent=2) + '\n')
    print(f'Wheel and evidence: {output}. Not approved for distribution.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kit', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--abi', choices=['x86_64', 'arm64_v8a'], required=True)
    args = parser.parse_args()
    build(args.kit, args.output, args.abi)
