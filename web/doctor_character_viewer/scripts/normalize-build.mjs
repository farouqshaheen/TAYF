import { readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const bundlePath = resolve(scriptDir, '../../../static/doctor_character/assets/doctor-viewer.js');
const bundle = await readFile(bundlePath, 'utf8');
const normalized = bundle
  .replace(/[\t ]+$/gm, '')
  .replace(/^ +(?=\t)/gm, '');

if (normalized !== bundle) {
  await writeFile(bundlePath, normalized);
}
