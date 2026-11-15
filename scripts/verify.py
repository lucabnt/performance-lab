"""Run every local check with one command (RT-06).

Steps run in order and the script continues after a failure, so one run lists
every problem; the exit code is non-zero when any step fails. Use the same
interpreter that has the development dependencies installed, for example
``.venv/Scripts/python.exe scripts/verify.py`` on Windows.

    python scripts/verify.py                 # all steps
    python scripts/verify.py --skip build    # skip one or more steps
    python scripts/verify.py --list          # show step names
"""

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def steps():
    python = sys.executable
    npm = shutil.which('npm') or 'npm'
    return [
        ('versions', 'Coerenza delle versioni', [python, 'scripts/verify_versions.py'], ROOT),
        ('suite-ui', 'UI comune incorporata', [python, 'scripts/verify_suite_ui.py'], ROOT),
        ('core', 'Common Python incorporato', [python, 'scripts/verify_core.py'], ROOT),
        ('lock-hashes', 'Hash del lockfile Python', [python, 'scripts/lock_hashes.py'], ROOT),
        ('lint', 'Linter Python (ruff)', [python, '-m', 'ruff', 'check', '.'], ROOT),
        ('format-py', 'Formato Python (ruff format)', [python, '-m', 'ruff', 'format', '--check', '.'], ROOT),
        ('format-js', 'Formato frontend (prettier)', [npm, 'run', 'format:check'], ROOT / 'frontend'),
        ('pytest', 'Test Python', [python, '-m', 'pytest', '-q', '-p', 'no:cacheprovider'], ROOT),
        ('signals', 'Test dei modelli frontend', [npm, 'run', 'test:signals'], ROOT / 'frontend'),
        ('build', 'Build frontend con controllo dei tipi (tsc)', [npm, 'run', 'build'], ROOT / 'frontend'),
        ('whitespace', 'Spazi e conflitti nel diff (git diff --check)', ['git', 'diff', '--check'], ROOT),
    ]


def main(argv=None):
    parser = argparse.ArgumentParser(description='Esegue tutte le verifiche locali di Fuorigiri.')
    parser.add_argument('--skip', nargs='+', default=[], metavar='STEP', help='passi da saltare')
    parser.add_argument('--list', action='store_true', help='elenca i passi e termina')
    args = parser.parse_args(argv)
    plan = steps()
    names = {name for name, *_ in plan}
    unknown = set(args.skip) - names
    if unknown:
        parser.error('passi sconosciuti: ' + ', '.join(sorted(unknown)))
    if args.list:
        for name, label, *_ in plan:
            print(f'{name:<11} {label}')
        return 0
    results = []
    for name, label, command, cwd in plan:
        if name in args.skip:
            results.append((name, label, 'saltato', 0.0))
            continue
        print(f'\n=== {label} [{name}]', flush=True)
        start = time.monotonic()
        try:
            code = subprocess.run(command, cwd=cwd).returncode
        except FileNotFoundError as exc:
            print(f'Comando non disponibile: {exc}', flush=True)
            code = 127
        results.append((name, label, 'ok' if code == 0 else f'FALLITO ({code})', time.monotonic() - start))
    print('\n=== Riepilogo')
    for name, label, status, elapsed in results:
        print(f'{status:<14} {name:<11} {elapsed:6.1f} s  {label}')
    failed = [r for r in results if r[2].startswith('FALLITO')]
    print('\nTutte le verifiche eseguite sono riuscite.' if not failed else f'\n{len(failed)} verifiche non riuscite.')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
