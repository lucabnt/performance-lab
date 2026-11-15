"""Fedora source rebuild of one Android native component and ABI per new output."""
import argparse
import hashlib
import json
import os
import platform
import shutil
import sys
from pathlib import Path
from android_native_tools import elf_info, native_wheel, modules_in_zip
from build_android_pillow import unpack, run


LIBRARIES = {
    'freetype':('chaquopy_freetype','libfreetype.so'),
    'libpng':('chaquopy_libpng','libpng16.so'),
    'openblas':('chaquopy_openblas','libopenblas.so'),
}


def build(kit, output, component, abi):
    if sys.platform != 'linux' or sys.version_info < (3,12):
        raise SystemExit('Run on Fedora/Linux with Python >=3.12 after sourcing ambiente.sh')
    kit,output = kit.resolve(),output.resolve()
    if output.exists():
        raise SystemExit('Output already exists; preserved. Choose a new directory.')
    ndk = Path(os.environ.get('ANDROID_NDK_ROOT','__missing__')).resolve()
    tools = ndk/'toolchains/llvm/prebuilt/linux-x86_64/bin'
    toolchain = ndk/'build/cmake/android.toolchain.cmake'
    if not toolchain.is_file() or not (tools/'llvm-readelf').is_file():
        raise SystemExit('Android NDK unavailable; restore ambiente.sh')
    manifest = json.loads((kit/'sources.json').read_text())
    contract_data = (kit/'consumer-contract.json').read_bytes()
    if hashlib.sha256(contract_data).hexdigest() != manifest['consumer_contract_sha256']:
        raise ValueError('Consumer contract checksum mismatch')
    contract = json.loads(contract_data)['abis'][abi]
    source_item = manifest['sources'][component]
    output.mkdir(parents=True)
    log = output/'build.log'
    report = {'status':'started-not-qualified','component':component,'abi':abi,
        'api':26,'host':platform.platform(),'host_python':sys.version,
        'ndk':(ndk/'source.properties').read_text(),'source':source_item,
        'consumer_contract_sha256':manifest['consumer_contract_sha256'],'wheels':{}}
    def save():
        (output/'build.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    source = unpack(kit/source_item['filename'],output/'source',source_item['sha256'])
    for command in [[sys.executable,'-m','pip','freeze'],[tools/'clang','--version']]:
        run(command,output,log)
    env = dict(os.environ)
    for key in list(env):
        if key.startswith('CIBW_'):
            del env[key]
    wheelhouse = output/'wheelhouse'
    if component == 'pydantic_core':
        # Keep the exact algorithm/version. Rebuild the linker layout, not .text
        # by merely relabeling ELF p_align or changing wheel hashes.
        config = output/'cibuildwheel.toml'
        config.write_text('[tool.cibuildwheel]\nbuild-frontend="build"\ntest-command=""\n')
        rustflags = '-C link-arg=-Wl,-z,max-page-size=16384 -C link-arg=-Wl,-z,common-page-size=16384'
        env.update(ANDROID_API_LEVEL='26',CIBW_ENVIRONMENT=f"RUSTFLAGS='{rustflags}'")
        run(['rustc','--version'],output,log)
        run(['rustup','target','list','--installed'],output,log)
        run([sys.executable,'-m','cibuildwheel',source,'--only',f'cp313-android_{abi}',
            '--config-file',config,'--output-dir',wheelhouse],output,log,env)
    else:
        for name in ['cmake','ninja']:
            if not shutil.which(name):
                raise SystemExit('Missing host build tool: '+name)
        prefix = output/'target'
        binary_dir = output/'cmake-build'
        common = [f'-DCMAKE_TOOLCHAIN_FILE={toolchain}',
            '-DANDROID_ABI='+('arm64-v8a' if abi=='arm64_v8a' else 'x86_64'),
            '-DANDROID_PLATFORM=android-26','-DANDROID_SUPPORT_FLEXIBLE_PAGE_SIZES=ON',
            '-DCMAKE_BUILD_TYPE=Release','-DCMAKE_POSITION_INDEPENDENT_CODE=ON',
            '-DBUILD_SHARED_LIBS=ON','-DBUILD_TESTING=OFF',
            '-DCMAKE_SHARED_LINKER_FLAGS=-Wl,-z,max-page-size=16384 -Wl,-z,common-page-size=16384',
            f'-DCMAKE_INSTALL_PREFIX={prefix}','-DCMAKE_INSTALL_LIBDIR=lib']
        if component == 'freetype':
            options = ['-DFT_DISABLE_ZLIB=ON','-DFT_DISABLE_BZIP2=ON','-DFT_DISABLE_PNG=ON',
                       '-DFT_DISABLE_HARFBUZZ=ON','-DFT_DISABLE_BROTLI=ON']
            notice_files = ['LICENSE.TXT','docs/FTL.TXT','src/bdf/README','src/pcf/README']
        elif component == 'libpng':
            options = ['-DPNG_SHARED=ON','-DPNG_STATIC=OFF','-DPNG_TESTS=OFF',
                       '-DPNG_TOOLS=OFF','-DPNG_EXECUTABLES=OFF']
            notice_files = ['LICENSE']
        else:
            # NDK has no Fortran. C-translated LAPACK must stay enabled: ONLY_CBLAS
            # or BUILD_WITHOUT_LAPACK would silently remove NumPy linalg support.
            options = ['-DNOFORTRAN=ON','-DC_LAPACK=ON','-DBUILD_WITHOUT_LAPACK=OFF',
                '-DBUILD_WITHOUT_LAPACKE=ON','-DINTERFACE64=OFF','-DDYNAMIC_ARCH=OFF',
                '-DTARGET='+('ARMV8' if abi=='arm64_v8a' else 'NEHALEM'),
                '-DUSE_THREAD=ON','-DNUM_THREADS=4','-DUSE_OPENMP=OFF','-DNO_AFFINITY=ON']
            notice_files = ['LICENSE','lapack-netlib/LICENSE']
        run(['cmake','--version'],output,log)
        run(['cmake','-S',source,'-B',binary_dir,'-G','Ninja',*common,*options],output,log,env)
        run(['cmake','--build',binary_dir,'--parallel','4'],output,log,env)
        run(['cmake','--install',binary_dir],output,log,env)
        package,library = LIBRARIES[component]
        # The unversioned filename is the DT_NEEDED name used by the existing
        # consumers. The compiler's own SONAME is retained and recorded.
        found = list(prefix.rglob(library))
        if len(found) != 1:
            raise ValueError(f'Expected one installed {library}; found {found}')
        data = found[0].read_bytes()
        info = elf_info(data)
        missing = set(contract[library]['required_exports'])-set(info['exports'])
        if missing:
            raise ValueError('Consumer ABI exports missing: '+', '.join(sorted(missing)))
        if not set(info['needed']) <= {'libc.so','libm.so','libdl.so','libz.so','liblog.so'}:
            raise ValueError('Unreviewed runtime dependency: '+repr(info['needed']))
        notices = {name.replace('/','-'):(source/name).read_bytes() for name in notice_files}
        wheelhouse.mkdir()
        native_wheel(wheelhouse,package,source_item['version'],abi,library,data,notices)
        report.update(consumer_required_exports=len(contract[library]['required_exports']),
                      consumer_contract_status=contract[library]['status'])
    wheels = sorted(wheelhouse.glob('*.whl'))
    if len(wheels) != 1:
        raise ValueError('Expected exactly one output wheel')
    modules = []
    for name,data in modules_in_zip(wheels[0]):
        info = elf_info(data)
        if not info['aligned_16k'] or info['machine'] != (183 if abi=='arm64_v8a' else 62):
            raise ValueError('Output wheel fails ABI/16KB gate: '+name)
        module = output/Path(name).name
        module.write_bytes(data)
        run([tools/'llvm-readelf','-h','-d','-lW',module],output,output/'elf.txt')
        modules.append(dict(file=name,**info))
    if not modules:
        raise ValueError('Output wheel has no native modules')
    report.update(status='compiled-ELF-checked-pending-Android-runtime',modules=modules,
                  wheels={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in wheels})
    save()
    print(f'Wheel and evidence: {output}. Runtime and APK not qualified.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kit',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--component',choices=['pydantic_core',*LIBRARIES],required=True)
    parser.add_argument('--abi',choices=['x86_64','arm64_v8a'],required=True)
    args = parser.parse_args()
    build(args.kit,args.output,args.component,args.abi)
