import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const source = readFileSync(new URL('../web_verify.mjs', import.meta.url), 'utf8');

function sourcePattern(name) {
  const match = source.match(new RegExp(`const ${name} = \/(.*)\/([a-z]*);`));
  assert.ok(match, `${name} is declared in the verifier`);
  return new RegExp(match[1], match[2]);
}

const start = source.indexOf('function findByLabel(');
const end = source.indexOf('\n}', start) + 2;
assert.ok(start >= 0 && end > start, 'Verifier exposes its label matcher');
const findByLabel = vm.runInNewContext(`(${source.slice(start, end)})`);

test('menu matcher skips merged instructions and the How to Play link', () => {
  const play = sourcePattern('PRIMARY_PLAY_LABEL');
  const nodes = [
    {label: 'A jewel carnival of chance PLAY CLASSIC SPIN How to Play'},
    {label: 'How to Play'},
    {label: 'PLAY CLASSIC SPIN'},
  ];
  assert.equal(findByLabel(nodes, play).label, 'PLAY CLASSIC SPIN');
});

test('game action matcher selects the spin control and not a merged route label', () => {
  const action = sourcePattern('PRIMARY_ACTION_LABEL');
  const nodes = [
    {label: 'Back Joker Jewels BALANCE 1000 Paytable and odds'},
    {label: 'Spotlight · 25'},
    {label: 'SPIN • 25'},
  ];
  assert.equal(findByLabel(nodes, action).label, 'SPIN • 25');
});

test('help text alone is not treated as a play action', () => {
  const play = sourcePattern('PRIMARY_PLAY_LABEL');
  assert.equal(findByLabel([{label: 'How to Play'}], play), undefined);
});
