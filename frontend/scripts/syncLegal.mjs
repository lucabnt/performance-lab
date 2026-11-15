import {readFile, mkdir, writeFile} from 'node:fs/promises';
const destination = new URL('../public/legal/', import.meta.url);
await mkdir(destination, {recursive: true});
for (const name of ['LICENSE', 'THIRD_PARTY.md'])
  await writeFile(new URL(name, destination), await readFile(new URL('../../' + name, import.meta.url)));
