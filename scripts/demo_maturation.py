"""Compatibility entry point: reduced suite including growth and maturation."""

import argparse
from pathlib import Path
from demo_suite import generate


def generate_growth(destination):
    manifest = generate(destination, small=True)
    print('Corpus SOLO DEMO creato:', Path(destination).resolve())
    return manifest['growth_cases']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    generate_growth(parser.parse_args().data)
