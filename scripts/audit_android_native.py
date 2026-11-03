"""Audit all ELF objects, including Python libraries nested in Chaquopy APK assets."""
import argparse
import hashlib
import json
from pathlib import Path
from android_native_tools import elf_info, modules_in_zip


def audit(path):
    objects = []
    for name,data in modules_in_zip(path):
        info = elf_info(data)
        info.update(file=name, sha256=hashlib.sha256(data).hexdigest())
        objects.append(info)
    if not objects:
        raise ValueError('No ELF objects found')
    return {'input':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'objects':objects,'unaligned':[x['file'] for x in objects if not x['aligned_16k']]}


def consumer_contract(report):
    """Symbols actually imported by direct consumers of the three legacy libraries."""
    result = {}
    for machine in [62,183]:
        group = [o for o in report['objects'] if o['machine'] == machine]
        abi = 'x86_64' if machine == 62 else 'arm64_v8a'
        result[abi] = {}
        for library in ['libfreetype.so','libpng16.so','libopenblas.so']:
            old = next(o for o in group if o['file'].endswith('/'+library))
            consumers = [o for o in group if library in o['needed']]
            required = set().union(*(set(o['imports']) for o in consumers)) & set(old['exports'])
            if consumers and not required:
                raise ValueError(f'Empty consumer contract: {abi} / {library}')
            result[abi][library] = {'required_exports':sorted(required),
                                   'consumers':[o['file'] for o in consumers],
                                   'status':'direct-ELF-consumers' if consumers else 'no-direct-ELF-consumer'}
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--contract',type=Path)
    parser.add_argument('--require-16k',action='store_true')
    args = parser.parse_args()
    report = audit(args.input)
    contract = consumer_contract(report) if args.contract else None
    with args.output.open('x',encoding='utf-8') as stream:
        json.dump(report,stream,indent=2)
    if args.contract:
        with args.contract.open('x',encoding='utf-8') as stream:
            json.dump(contract,stream,indent=2)
    print(f"ELF objects: {len(report['objects'])}; unaligned: {len(report['unaligned'])}")
    for name in report['unaligned']:
        print(name)
    if args.require_16k and report['unaligned']:
        raise SystemExit(1)
