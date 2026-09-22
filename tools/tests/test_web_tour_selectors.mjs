import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const source = readFileSync(new URL('../web_verify.mjs', import.meta.url), 'utf8');
const begin = source.indexOf('function findByLabel');
const end = source.indexOf('\n// ─── the tour', begin);
assert.ok(begin >= 0 && end > begin, 'Verifier exposes its semantic selectors');
const helper = source.slice(begin, end);
const findLeafByLabel = vm.runInNewContext(`(() => { ${helper}; return findLeafByLabel; })()`);

test('exact gameplay label wins over Flutter composite semantics root', () => {
  const nodes = [
    {label: 'Olympus storm, balance 5,000 chips, Spin, Settings', x: 195, y: 422},
    {label: 'SPIN', x: 195, y: 730},
  ];
  const selected = findLeafByLabel(nodes, ['spin'], /spin/i);
  assert.equal(selected.label, 'SPIN');
  assert.equal(selected.y, 730);
});

test('variant labels fall back to the shortest matching leaf', () => {
  const nodes = [
    {label: 'Play now — balance and paytable', x: 195, y: 422},
    {label: 'Play now', x: 195, y: 730},
  ];
  const selected = findLeafByLabel(nodes, ['play'], /play/i);
  assert.equal(selected.label, 'Play now');
  assert.equal(selected.y, 730);
});

test('headless CanvasKit keeps the SwiftShader WebGL path for raster assets', () => {
  assert.match(source, /'--enable-gpu'/);
  assert.match(source, /'--ignore-gpu-blocklist'/);
  assert.match(source, /'--use-gl=angle'/);
  assert.match(source, /'--use-angle=swiftshader'/);
  assert.doesNotMatch(source, /'--disable-gpu'/);
  assert.doesNotMatch(source, /'--disable-background-networking'/);
});
