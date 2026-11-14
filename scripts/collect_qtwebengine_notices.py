"""Collect Chromium third-party notices for the Qt WebEngine shipped on Windows.

Inputs are official artefacts for the exact runtime version: the source archive
from download.qt.io and the "Qt WebEngine Licensing" page of the same version,
whose third-party list defines the components to include. For each listed
component the README.chromium metadata in the source archive provides the
license files; their texts are copied verbatim. The output is written to a new
file. Components without a matching README remain listed as unresolved, never
silently dropped.
"""
import argparse
import hashlib
import html
import json
import re
import tarfile
from pathlib import Path, PurePosixPath


def listed_components(page):
    """Return (title, [(name, licenses)]) from the per-component links of the page."""
    title = html.unescape(re.search(r'<title>(.*?)</title>', page, re.S).group(1)).strip()
    clean = lambda value: re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', value))).strip()
    pairs = []
    pattern = r'<a href="(qtwebengine-3rdparty-[^"]+)">(.*?)</a>(.*?)(?=<a href="qtwebengine-3rdparty-|</table>|</dl>|</ul>)'
    for href, name, rest in re.findall(pattern, page, re.S):
        pairs.append((html.unescape(clean(name)), clean(rest), href))
    if not pairs:
        raise SystemExit('No third-party list found in the licensing page')
    return title, pairs


def page_text(path):
    """Main text of an official per-component page, which carries the license."""
    page = path.read_text(encoding='utf-8')
    match = re.search(r'<main.*?</main>|<article.*?</article>', page, re.S)
    body = re.sub(r'<script.*?</script>|<style.*?</style>', '', match.group() if match else page, flags=re.S)
    text = html.unescape(html.unescape(re.sub(r'<[^>]+>', '', body)))
    return re.sub(r'\n{3,}', '\n\n', text).strip()


def parse_readme(text):
    fields = {}
    for line in text.splitlines():
        match = re.match(r'^([A-Za-z][A-Za-z ]+):\s*(.*)$', line)
        if match and match.group(1) not in fields:
            fields[match.group(1)] = match.group(2).strip()
        if line.strip() == 'Description:':
            break
    return fields


def collect(archive, page, output, pages=None):
    if output.exists():
        raise SystemExit('Output already exists: choose a new file')
    title, components = listed_components(page.read_text(encoding='utf-8'))
    readmes, wanted = {}, {}
    with tarfile.open(archive) as source:
        for member in source:
            if member.isfile() and member.name.endswith('/README.chromium'):
                fields = parse_readme(source.extractfile(member).read().decode('utf-8', 'replace'))
                if fields.get('Shipped', 'yes').lower() == 'no':
                    continue
                readmes.setdefault(fields.get('Name', ''), []).append((member.name, fields))
    resolved, unresolved = [], []
    official = []
    for name, licenses, href in components:
        matches = readmes.get(name, [])
        if not matches and pages and (pages / href).is_file():
            official.append((name, licenses, href, page_text(pages / href)))
            continue
        if not matches:
            unresolved.append((name, licenses))
            continue
        path, fields = sorted(matches, key=lambda item: len(item[0]))[0]
        folder = PurePosixPath(path).parent
        files = [f.strip() for f in re.split(r',', fields.get('License File', '')) if f.strip() and f.strip() != 'NOT_SHIPPED']
        targets = []
        for item in files:
            # Paths starting with / are relative to the Chromium source root.
            relative = PurePosixPath(item.lstrip('/'))
            chromium = next(p for p in folder.parents if p.name == 'chromium')
            targets.append(str((chromium if item.startswith('/') else folder) / relative))
        resolved.append((name, licenses, fields.get('URL', ''), targets))
        wanted.update({t: None for t in targets})
    with tarfile.open(archive) as source:
        for member in source:
            if member.name in wanted and member.isfile():
                wanted[member.name] = source.extractfile(member).read().decode('utf-8', 'replace')
    texts, sections = {}, []
    for name, licenses, url, targets in resolved:
        refs = []
        for target in targets:
            body = wanted.get(target)
            if body is None:
                refs.append('(file non trovato nel sorgente: ' + target.split('/chromium/', 1)[-1] + ')')
                continue
            digest = hashlib.sha256(body.encode('utf-8')).hexdigest()[:12]
            texts.setdefault(digest, body)
            refs.append('[testo ' + digest + ']')
        sections.append(f'{name}\n  Licenza dichiarata: {licenses}\n  Sorgente: {url or "n/d"}\n  Testi: {", ".join(refs) or "nessun file indicato"}\n')
    for name, licenses, href, text in official:
        digest = hashlib.sha256(text.encode('utf-8')).hexdigest()[:12]
        texts.setdefault(digest, text)
        sections.append(f'{name}\n  Licenza dichiarata: {licenses}\n  Testi: [testo {digest}] dalla pagina ufficiale {href}\n')
    header = (f'Avvisi di terze parti di Chromium in {title.split("|", 1)[1].strip()}\n'
              f'Generato da {archive.name} (download.qt.io) e dalla pagina ufficiale "Qt WebEngine Licensing".\n'
              f'Componenti elencati: {len(components)}; testi dai sorgenti: {len(resolved)}; '
              f'dalle pagine ufficiali: {len(official)}; senza testo: {len(unresolved)}.\n\n')
    body = header + '=' * 78 + '\nCOMPONENTI\n' + '=' * 78 + '\n\n' + '\n'.join(sections)
    if unresolved:
        body += '\nComponenti senza README.chromium corrispondente (licenza dalla pagina ufficiale):\n'
        body += ''.join(f'  {name}: {licenses}\n' for name, licenses in unresolved)
    body += '\n' + '=' * 78 + '\nTESTI DI LICENZA\n' + '=' * 78 + '\n'
    for digest, text in texts.items():
        body += f'\n----- testo {digest} -----\n{text.rstrip()}\n'
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(body)
    summary = {'components': len(components), 'resolved': len(resolved), 'official_pages': len(official),
               'unresolved': [n for n, _ in unresolved], 'texts': len(texts),
               'source_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
               'output_sha256': hashlib.sha256(output.read_bytes()).hexdigest()}
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True, help='qtwebengine-everywhere-src-<version>.tar.xz')
    parser.add_argument('--page', type=Path, required=True, help='Saved qtwebengine-licensing.html')
    parser.add_argument('--pages', type=Path, help='Folder with saved qtwebengine-3rdparty-*.html pages of the same version')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    collect(args.source, args.page, args.output, args.pages)


if __name__ == '__main__':
    main()
