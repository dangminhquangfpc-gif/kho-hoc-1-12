/* Real Chromium smoke test for the vendored, offline OCR worker.
 * Run: node scripts/test_browser_ocr.cjs
 * Requires the repo's apps/admin Playwright dependency and /usr/bin/chromium.
 * Uses a local HTTP server and blocks every non-local browser request.
 */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const { chromium } = require('../apps/admin/node_modules/playwright');

const root = path.resolve(__dirname, '../apps/mobile/web');
const server = http.createServer((request, response) => {
  const pathname = new URL(request.url, 'http://localhost').pathname;
  if (pathname === '/') {
    response.setHeader('Content-Type', 'text/html; charset=utf-8');
    response.end('<!doctype html><html lang="vi"><script src="ocr/ocr.js"></script><button id="pick">Chọn ảnh</button><script>pick.onclick=()=>{window.picked=tuHocOcr.pickAndRecognize().then(x=>({ok:true,value:x}),e=>({ok:false,message:e.message,name:e.name}));}</script></html>');
    return;
  }
  const filename = path.resolve(root, '.' + pathname);
  if (!filename.startsWith(root + path.sep) || !fs.existsSync(filename) || !fs.statSync(filename).isFile()) {
    response.writeHead(404).end();
    return;
  }
  const mime = filename.endsWith('.js') ? 'application/javascript' : 'application/octet-stream';
  response.setHeader('Content-Type', mime);
  fs.createReadStream(filename).pipe(response);
});

async function main() {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const origin = `http://127.0.0.1:${server.address().port}`;
  const browser = await chromium.launch({ executablePath: '/usr/bin/chromium', headless: true, args: ['--no-sandbox'] });
  try {
    const context = await browser.newContext();
    const external = [];
    const requested = [];
    await context.route('**/*', route => {
      const url = route.request().url();
      requested.push(url);
      if (url.startsWith(origin + '/')) return route.continue();
      external.push(url);
      return route.abort();
    });
    await context.addInitScript(() => {
      const NativeWorker = window.Worker;
      window.ocrTestWorkers = { created: 0, active: 0 };
      window.Worker = class extends NativeWorker {
        constructor(...args) {
          super(...args);
          window.ocrTestWorkers.created++;
          window.ocrTestWorkers.active++;
          this.testTerminated = false;
        }
        terminate() {
          if (!this.testTerminated) { window.ocrTestWorkers.active--; this.testTerminated = true; }
          return super.terminate();
        }
      };
    });
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(origin);
    const imageBase64 = await page.evaluate(() => {
      const canvas = document.createElement('canvas');
      canvas.width = 1500; canvas.height = 500;
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = 'white'; ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = 'black'; ctx.font = '42px "Noto Sans"';
      ['Tự học 111', 'Bài 1: Tính diện tích hình chữ nhật.',
        'Chiều dài 12 cm, chiều rộng 5 cm.', 'Đáp số: 60 cm2.'].forEach((text, i) => ctx.fillText(text, 55, 90 + i * 105));
      const encoded = canvas.toDataURL('image/png').split(',')[1];
      window.ocrTestImage = encoded;
      return encoded;
    });
    const chooser = page.waitForEvent('filechooser');
    await page.locator('#pick').click();
    await (await chooser).setFiles({ name: 'test-no-personal-data.png', mimeType: 'image/png', buffer: Buffer.from(imageBase64, 'base64') });
    await page.waitForFunction(() => !tuHocOcr.status().busy, null, { timeout: 65000 });
    const picked = await page.evaluate(() => window.picked);
    assert.equal(picked.ok, true, JSON.stringify(picked));
    const normalized = picked.value.text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[Đđ]/g, 'd').toLowerCase();
    assert.match(normalized, /tu hoc 111/);
    assert.match(normalized, /dien tich/);
    assert.match(normalized, /12 cm/);
    assert.match(normalized, /60 cm/);
    assert.ok(picked.value.confidence > 60);
    assert.ok(picked.value.preview_data_url.startsWith('data:image/jpeg;base64,'));
    assert.ok(picked.value.preview_data_url.length < 1400000);
    assert.ok(picked.value.warnings.length > 0);
    console.log(JSON.stringify({ case: 'real-vietnamese-ocr', text: picked.value.text, confidence: picked.value.confidence }));

    const invalid = await page.evaluate(async () => {
      const rejected = async blob => {
        try { await tuHocOcr.recognizeFile(blob); return 'accepted'; }
        catch (error) { return error.message; }
      };
      const png = Uint8Array.from(atob(window.ocrTestImage), ch => ch.charCodeAt(0));
      const tooBigHeader = png.slice();
      new DataView(tooBigHeader.buffer).setUint32(16, 7000);
      const tooManyPixels = png.slice();
      const pixelHeader = new DataView(tooManyPixels.buffer);
      pixelHeader.setUint32(16, 5000); pixelHeader.setUint32(20, 4000);
      return {
        svg: await rejected(new Blob(['<svg xmlns="http://www.w3.org/2000/svg"/>'], { type: 'image/svg+xml' })),
        fake: await rejected(new Blob(['not-a-png'], { type: 'image/png' })),
        mismatch: await rejected(new Blob([png], { type: 'image/jpeg' })),
        truncated: await rejected(new Blob([png.slice(0, 32)], { type: 'image/png' })),
        pixels: await rejected(new Blob([tooBigHeader], { type: 'image/png' })),
        megapixels: await rejected(new Blob([tooManyPixels], { type: 'image/png' })),
        bytes: await rejected(new Blob([new Uint8Array(8 * 1024 * 1024 + 1)], { type: 'image/png' })),
        workers: window.ocrTestWorkers,
      };
    });
    for (const key of ['svg', 'fake', 'mismatch', 'truncated', 'pixels', 'megapixels', 'bytes']) assert.notEqual(invalid[key], 'accepted', key);
    assert.equal(invalid.workers.created, 1, 'invalid files must be rejected before worker allocation');
    assert.equal(invalid.workers.active, 0);

    // Actual JPEG and WebP decoding, normalization and OCR, not only header stubs.
    for (const mime of ['image/jpeg', 'image/webp']) {
      const result = await page.evaluate(async mimeType => {
        const image = new Image(); image.src = 'data:image/png;base64,' + window.ocrTestImage;
        await image.decode();
        const canvas = document.createElement('canvas'); canvas.width = image.width; canvas.height = image.height;
        canvas.getContext('2d').drawImage(image, 0, 0);
        const blob = await new Promise(resolve => canvas.toBlob(resolve, mimeType, 0.95));
        return tuHocOcr.recognizeFile(blob);
      }, mime);
      assert.match(result.text, /111/);
      assert.match(result.text, /60/);
    }
    console.log('PASS: PNG picker, JPEG, WebP real OCR; SVG/fake/MIME/dimensions/bytes rejected before worker allocation');

    await page.evaluate(() => {
      const png = Uint8Array.from(atob(window.ocrTestImage), ch => ch.charCodeAt(0));
      window.cancelled = tuHocOcr.recognizeFile(new Blob([png], { type: 'image/png' }))
        .then(() => ({ accepted: true }), error => ({ name: error.name, message: error.message }));
    });
    await page.waitForFunction(() => window.ocrTestWorkers.active === 1);
    const busy = await page.evaluate(async () => {
      try { await tuHocOcr.recognizeFile(new Blob(['x'])); return 'accepted'; }
      catch (error) { return error.message; }
    });
    assert.notEqual(busy, 'accepted');
    await page.evaluate(() => tuHocOcr.cancel());
    const cancelled = await page.evaluate(() => window.cancelled);
    assert.equal(cancelled.name, 'AbortError');
    assert.equal(await page.evaluate(() => window.ocrTestWorkers.active), 0);
    assert.equal(await page.evaluate(() => document.querySelectorAll('input[type=file]').length), 0);

    const emptyPicker = page.waitForEvent('filechooser');
    await page.locator('#pick').click();
    await (await emptyPicker).setFiles([]);
    const noFile = await page.evaluate(() => window.picked);
    assert.equal(noFile.ok, true);
    assert.equal(noFile.value, null);
    assert.equal(await page.evaluate(() => document.querySelectorAll('input[type=file]').length), 0);

    // Simulate a 60s deadline firing promptly; cancellation still uses a real worker.
    const timeout = await page.evaluate(async () => {
      const savedTimer = window.setTimeout;
      window.setTimeout = (callback, delay, ...args) => savedTimer(callback, delay === 60000 ? 80 : delay, ...args);
      try {
        const png = Uint8Array.from(atob(window.ocrTestImage), ch => ch.charCodeAt(0));
        await tuHocOcr.recognizeFile(new Blob([png], { type: 'image/png' }));
        return { accepted: true };
      } catch (error) { return { name: error.name, active: window.ocrTestWorkers.active }; }
      finally { window.setTimeout = savedTimer; }
    });
    assert.equal(timeout.name, 'TimeoutError');
    assert.equal(timeout.active, 0);
    assert.ok(requested.some(url => url.endsWith('/ocr/lang/vie.traineddata.gz')));
    assert.ok(requested.some(url => url.endsWith('/ocr/lang/eng.traineddata.gz')));
    assert.equal(external.length, 0, 'OCR must never contact an external URL');
    assert.deepEqual(errors, []);
    const storage = await page.evaluate(async () => ({ local: localStorage.length, databases: indexedDB.databases ? await indexedDB.databases() : [] }));
    assert.equal(storage.local, 0);
    assert.equal(storage.databases.length, 0);
    console.log('PASS: concurrency guard, immediate worker cancellation, empty picker cancellation, timeout cleanup, no external requests, no image persistence');
    await context.close();
  } finally {
    await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
}
main().catch(error => { console.error(error); server.close(); process.exitCode = 1; });
