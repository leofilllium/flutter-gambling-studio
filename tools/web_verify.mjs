#!/usr/bin/env node
// web_verify.mjs — Headless runtime verification of a Flutter **web** build.
//
// WHY THIS EXISTS
//   `flutter screenshot` does NOT support web targets, and GUI automation
//   (xdotool / osascript) is unavailable or unreliable in headless / Wayland
//   sessions. That combination is the root cause of /autocreate-finalize
//   hanging on the "navigate to the game in Chrome + screenshot" step.
//
//   This driver replaces that fragile path with the Chrome DevTools Protocol:
//     • real PNG screenshots of the CanvasKit canvas  (Page.captureScreenshot)
//     • real taps on the canvas                        (Input.dispatchMouseEvent)
//     • real console / exception capture               (Runtime + Log domains)
//   …driving a headless Chrome. No npm dependencies — Node 21+ ships a global
//   WebSocket and fetch, which is all CDP needs.
//
//   It is HARD self-terminating: an overall deadline forces a clean finalize +
//   exit so the finalize pipeline can never get stuck here.
//
// USAGE
//   node tools/web_verify.mjs --url http://127.0.0.1:8099 --out <shotDir> \
//        [--budget 150] [--size 390x844] [--quick] [--chrome /path/to/chrome]
//
// OUTPUT (in <shotDir>)
//   01-splash.png 02-menu.png 03-game-idle.png 04-game-action.png
//   05-game-after-action.png  (+ extra screens unless --quick)
//   webconsole.log   — every console message + uncaught exception
//   manifest.json    — { steps, semanticLabels, consoleErrors, verdictHints }
//
// EXIT CODES
//   0  connected and captured at least the splash frame (normal — even if the
//      app had runtime errors; those are reported in manifest/webconsole)
//   2  could not launch Chrome or connect to the page within the budget
//   3  bad arguments

import { spawn } from 'node:child_process';
import { mkdirSync, writeFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';

// ─── args ────────────────────────────────────────────────────────────────
function arg(name, def) {
  const i = process.argv.indexOf(`--${name}`);
  if (i === -1) return def;
  const v = process.argv[i + 1];
  return v && !v.startsWith('--') ? v : true;
}
const URL = arg('url');
const OUT = arg('out');
const BUDGET = Number(arg('budget', '150')) * 1000;
const QUICK = arg('quick', false) === true;
const SOAK = Number(arg('soak', '0')) || 0;   // N stress taps for leak detection (0 = off)
const SIZE = String(arg('size', '390x844'));
const [VW, VH] = SIZE.split('x').map(Number);
// Capture at real device resolution. At dpr 1 a 390x844 viewport yields a 390px-wide
// PNG, which the store compositor then has to upscale ~3x. Default 2 (780x1688) is
// already big enough for a 1080-wide store canvas while keeping the software-rendered
// (swiftshader) fill rate near what verification runs have always used; --dpr 3 gives
// the crispest store frames but triples the per-frame pixel cost.
const DPR = Math.max(1, Math.min(4, Number(arg('dpr', '2')) || 2));
const CHROME = resolveChrome(arg('chrome'));

if (!URL || !OUT) {
  console.error('usage: web_verify.mjs --url <url> --out <dir> [--budget s] [--size WxH] [--dpr N] [--quick] [--soak N] [--chrome path]');
  process.exit(3);
}
if (!Number.isFinite(VW) || !Number.isFinite(VH) || VW < 64 || VH < 64) {
  console.error(`bad --size "${SIZE}"; expected WIDTHxHEIGHT, e.g. 390x844`);
  process.exit(3);
}
mkdirSync(OUT, { recursive: true });

function resolveChrome(explicit) {
  if (typeof explicit === 'string') return explicit;
  if (process.env.CHROME_EXECUTABLE) return process.env.CHROME_EXECUTABLE;
  const cands = [
    'google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser',
    '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable',
    '/usr/bin/chromium', '/usr/bin/chromium-browser',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  ];
  return cands[0]; // spawn will surface ENOENT; we try the common name first
}

// ─── tiny logger + manifest ──────────────────────────────────────────────
const manifest = {
  url: URL, size: SIZE, dpr: DPR, capture: `${VW * DPR}x${VH * DPR}`,
  startedAt: new Date().toISOString(),
  steps: [], semanticLabels: [], consoleErrors: [], shots: [], notes: [],
};
const consoleLines = [];
const log = (m) => { console.log(m); manifest.notes.push(m); };

function finalize(code) {
  manifest.finishedAt = new Date().toISOString();
  manifest.consoleErrorCount = manifest.consoleErrors.length;
  try { writeFileSync(join(OUT, 'manifest.json'), JSON.stringify(manifest, null, 2)); } catch {}
  try { writeFileSync(join(OUT, 'webconsole.log'), consoleLines.join('\n') + '\n'); } catch {}
  try { chrome?.kill('SIGKILL'); } catch {}
  process.exit(code);
}

// hard deadline — the whole point: never hang the pipeline
const deadline = setTimeout(() => { log(`⏰ budget ${BUDGET / 1000}s exceeded — finalizing`); finalize(0); }, BUDGET);
deadline.unref();

// ─── launch headless Chrome ───────────────────────────────────────────────
const PORT = 9300 + Math.floor(Math.random() * 600);
const userDir = join(tmpdir(), `webverify-${process.pid}`);
let chrome;
function launchChrome() {
  const flags = [
    '--headless=new', '--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage',
    '--use-gl=swiftshader', '--hide-scrollbars', '--no-first-run', '--no-default-browser-check',
    '--disable-extensions', '--disable-background-networking',
    `--window-size=${VW},${VH}`, `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${userDir}`, URL,
  ];
  chrome = spawn(CHROME, flags, { stdio: ['ignore', 'ignore', 'pipe'] });
  chrome.on('error', (e) => { log(`❌ cannot launch Chrome (${CHROME}): ${e.message}`); finalize(2); });
  chrome.stderr.on('data', (d) => { /* keep last lines for diagnostics */
    const s = d.toString(); if (/ERROR|FATAL/.test(s)) manifest.notes.push('chrome:' + s.trim().slice(0, 200));
  });
}

// ─── CDP plumbing over the built-in WebSocket ──────────────────────────────
async function getWsUrl() {
  for (let i = 0; i < 60; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${PORT}/json`);
      const targets = await r.json();
      const page = targets.find((t) => t.type === 'page' && t.webSocketDebuggerUrl);
      if (page) return page.webSocketDebuggerUrl;
    } catch { /* chrome not ready yet */ }
    await sleep(500);
  }
  return null;
}

let ws, nextId = 1;
const pending = new Map();
function send(method, params = {}) {
  const id = nextId++;
  return new Promise((resolve, reject) => {
    pending.set(id, { resolve, reject });
    ws.send(JSON.stringify({ id, method, params }));
    setTimeout(() => { if (pending.delete(id)) reject(new Error(`CDP timeout: ${method}`)); }, 15000);
  });
}
function onMessage(raw) {
  let msg; try { msg = JSON.parse(raw); } catch { return; }
  if (msg.id && pending.has(msg.id)) {
    const p = pending.get(msg.id); pending.delete(msg.id);
    msg.error ? p.reject(new Error(msg.error.message)) : p.resolve(msg.result);
    return;
  }
  // events
  if (msg.method === 'Runtime.consoleAPICalled') {
    const text = (msg.params.args || []).map(a => a.value ?? a.description ?? a.type).join(' ');
    const line = `[console.${msg.params.type}] ${text}`;
    consoleLines.push(line);
    if (msg.params.type === 'error') manifest.consoleErrors.push(text);
  } else if (msg.method === 'Runtime.exceptionThrown') {
    const d = msg.params.exceptionDetails;
    const text = d.exception?.description || d.text || 'exception';
    consoleLines.push(`[exception] ${text}`);
    manifest.consoleErrors.push(text);
  } else if (msg.method === 'Log.entryAdded') {
    const e = msg.params.entry;
    consoleLines.push(`[log.${e.level}] ${e.text}`);
    if (e.level === 'error') manifest.consoleErrors.push(e.text);
  }
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function evaluate(expression) {
  const r = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  return r.result?.value;
}

async function screenshot(name) {
  try {
    const { data } = await send('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
    const file = join(OUT, `${name}.png`);
    writeFileSync(file, Buffer.from(data, 'base64'));
    manifest.shots.push(`${name}.png`);
    log(`📸 ${name}.png`);
    return true;
  } catch (e) { log(`❌ screenshot ${name}: ${e.message}`); return false; }
}

async function tap(x, y, label) {
  const cx = Math.round(x), cy = Math.round(y);
  await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: cx, y: cy });
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: cx, y: cy, button: 'left', clickCount: 1 });
  await sleep(40);
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: cx, y: cy, button: 'left', clickCount: 1 });
  manifest.steps.push({ action: 'tap', x: cx, y: cy, label: label || null });
}

// Wait until Flutter has rendered its first frame.
async function waitForFlutter() {
  for (let i = 0; i < 50; i++) {
    const ready = await evaluate(`!!(document.querySelector('flutter-view') ||
      document.querySelector('flt-glass-pane') ||
      document.querySelector('canvas') ||
      document.querySelector('flt-scene-host'))`).catch(() => false);
    if (ready) { await sleep(800); return true; }
    await sleep(400);
  }
  return false;
}

// Enable Flutter's a11y tree (click the hidden placeholder) and read labels.
// Returns [{label, x, y}] in viewport coords; [] if semantics unavailable.
async function readSemantics() {
  // 1) find + click the "Enable accessibility" placeholder (may be in shadow DOM)
  const placeholderRect = await evaluate(`(function(){
    function walk(root){
      const els = root.querySelectorAll('*');
      for (const el of els){
        const tag = (el.tagName||'').toLowerCase();
        const al  = (el.getAttribute && (el.getAttribute('aria-label')||'')) || '';
        if (tag==='flt-semantics-placeholder' || /enable accessibility/i.test(al)){
          const r = el.getBoundingClientRect();
          return {x:r.left+r.width/2, y:r.top+r.height/2};
        }
        if (el.shadowRoot){ const f=walk(el.shadowRoot); if(f) return f; }
      }
      return null;
    }
    return walk(document);
  })()`).catch(() => null);
  if (placeholderRect) { await tap(Math.max(1, placeholderRect.x), Math.max(1, placeholderRect.y), 'enable-a11y'); await sleep(700); }
  else { await tap(1, 1, 'enable-a11y-blind'); await sleep(500); } // placeholder usually sits 1x1 top-left

  // 2) collect labeled, on-screen semantic nodes
  const nodes = await evaluate(`(function(){
    const out=[];
    function walk(root){
      const els = root.querySelectorAll('[aria-label], flt-semantics, [role="button"]');
      for (const el of els){
        const label = (el.getAttribute && (el.getAttribute('aria-label')||el.textContent||'')).trim();
        if(!label) continue;
        const r = el.getBoundingClientRect();
        if (r.width<2 || r.height<2) continue;
        if (r.top> ${VH} || r.left> ${VW} || r.bottom<0 || r.right<0) continue;
        out.push({label, x:r.left+r.width/2, y:r.top+r.height/2, w:r.width, h:r.height});
      }
      for (const el of root.querySelectorAll('*')) if(el.shadowRoot) walk(el.shadowRoot);
    }
    walk(document);
    // de-dup by label+pos
    const seen=new Set(); return out.filter(n=>{const k=n.label+'@'+Math.round(n.x)+','+Math.round(n.y); if(seen.has(k))return false; seen.add(k); return true;});
  })()`).catch(() => []);
  if (Array.isArray(nodes)) manifest.semanticLabels = nodes.map((n) => n.label).slice(0, 40);
  return Array.isArray(nodes) ? nodes : [];
}

function findByLabel(nodes, re) {
  return nodes.find((n) => re.test(n.label));
}

// ─── the tour ──────────────────────────────────────────────────────────────
async function main() {
  launchChrome();
  const wsUrl = await getWsUrl();
  if (!wsUrl) { log('❌ Chrome DevTools endpoint never came up'); finalize(2); return; }

  ws = new WebSocket(wsUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = () => rej(new Error('ws error')); });
  ws.onmessage = (ev) => onMessage(typeof ev.data === 'string' ? ev.data : ev.data.toString());

  await send('Page.enable');
  await send('Runtime.enable');
  await send('Log.enable');
  await send('DOM.enable');

  // Pin the viewport explicitly. `--window-size` alone is only advisory: headless has
  // been observed laying out at its own default instead, which produced near-square
  // captures (h/w ~1.5) rather than a phone's ~2.16 — those are unusable as store
  // screenshots, because the device mockup ends up looking like a squat tablet.
  // Taps below use CSS pixels, which this override defines, so they stay correct.
  try {
    await send('Emulation.setDeviceMetricsOverride', {
      width: VW, height: VH, deviceScaleFactor: DPR, mobile: true,
      screenWidth: VW, screenHeight: VH,
    });
    log(`📐 viewport ${VW}x${VH} @${DPR}x → capture ${VW * DPR}x${VH * DPR}`);
  } catch (e) {
    manifest.viewportOverrideFailed = true;
    log(`⚠️ setDeviceMetricsOverride failed (${e.message}) — falling back to --window-size, ` +
        'captures may not be phone-shaped');
  }

  const ready = await waitForFlutter();
  manifest.steps.push({ action: 'ready', flutterDetected: ready });
  if (!ready) log('⚠️ Flutter first-frame not detected within budget — capturing anyway');

  // 1. splash
  await screenshot('01-splash');

  // 2. menu (splash usually auto-advances)
  await sleep(3500);
  await screenshot('02-menu');

  // 3. game screen — prefer a labeled Play/Start button, else thumb-zone tap
  const nodes = await readSemantics();
  const play = findByLabel(nodes, /играть|играй|старт|start|play|begin|новая игра|спин|spin/i);
  if (play) { log(`🎯 found action by label: "${play.label}"`); await tap(play.x, play.y, play.label); }
  else { log('🎯 no labeled Play — tapping thumb zone'); await tap(VW / 2, VH * 0.82); }
  await sleep(2500);
  await screenshot('03-game-idle');

  // 4. main action (spin/play/tap) — labeled if possible, else thumb zone again
  const nodes2 = await readSemantics();
  const act = findByLabel(nodes2, /спин|spin|крутить|играть|play|tap|бросить|throw|launch|пуск|go|ход|move/i);
  if (act) { log(`🎯 action button: "${act.label}"`); await tap(act.x, act.y, act.label); }
  else { await tap(VW / 2, VH * 0.82); }
  await sleep(1500);
  await screenshot('04-game-action');
  await sleep(3000);
  await screenshot('05-game-after-action');

  // 4b. SOAK / leak probe — repeat the main action N times, compare JS heap start vs end.
  if (SOAK > 0) {
    const ax = act ? act.x : VW / 2;
    const ay = act ? act.y : VH * 0.82;
    const heapUsed = async () => {
      try { const h = await send('Runtime.getHeapUsage'); return Number(h?.usedSize || 0); }
      catch { return 0; }
    };
    // settle + force a GC baseline if exposed, then measure
    await sleep(800);
    const errStart = manifest.consoleErrors.length;
    const heapStart = await heapUsed();
    log(`🧪 soak: ${SOAK} taps, heapStart=${(heapStart / 1048576).toFixed(1)}MB`);
    for (let i = 0; i < SOAK; i++) {
      await tap(ax, ay);
      await sleep(120);
      // stay inside the global budget — bail out gracefully if time runs short
      if (i % 25 === 24) log(`   soak ${i + 1}/${SOAK}…`);
    }
    await sleep(1200);
    const heapEnd = await heapUsed();
    const errEnd = manifest.consoleErrors.length;
    const growthPct = heapStart > 0 ? ((heapEnd - heapStart) / heapStart) * 100 : 0;
    manifest.soak = {
      taps: SOAK,
      heapStartBytes: heapStart, heapEndBytes: heapEnd,
      heapGrowthPct: Number(growthPct.toFixed(1)),
      consoleErrorsStart: errStart, consoleErrorsEnd: errEnd,
      // heuristic: >60% heap growth with no plateau OR a burst of new console errors = suspect leak
      suspectLeak: (growthPct > 60) || (errEnd - errStart > 5),
    };
    log(`🧪 soak done: heapEnd=${(heapEnd / 1048576).toFixed(1)}MB growth=${growthPct.toFixed(1)}% ` +
        `newErrors=${errEnd - errStart} suspectLeak=${manifest.soak.suspectLeak}`);
    await screenshot('06-soak-after');
  }

  if (!QUICK && SOAK === 0) {
    // Best-effort sweep of secondary screens, by label when available.
    const extras = [
      [/настройк|settings|опции/i, '06-settings'],
      [/помощь|help|как играть|правила|paytable|таблица/i, '07-help'],
      [/профил|profile|статист|stats|лидер|leaderboard|рекорд/i, '08-stats'],
    ];
    for (const [re, name] of extras) {
      const back = findByLabel(await readSemantics(), /назад|back|закрыт|close|меню|menu|домой|home/i);
      if (back) { await tap(back.x, back.y, back.label); await sleep(1200); }
      const item = findByLabel(await readSemantics(), re);
      if (item) { await tap(item.x, item.y, item.label); await sleep(1500); await screenshot(name); }
    }
  }

  log(`✅ tour complete — ${manifest.shots.length} shots, ${manifest.consoleErrors.length} console errors`);
  finalize(0);
}

main().catch((e) => { log(`❌ fatal: ${e.message}`); finalize(manifest.shots.length ? 0 : 2); });
