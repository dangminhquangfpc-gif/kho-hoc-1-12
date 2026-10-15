// Rebuild the authored study-note PDFs using the admin's existing Playwright dependency.
// This renderer serves only the four source pages and the bundled licensed font locally.
const { chromium } = require('../../apps/admin/node_modules/playwright');
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');

const root = path.resolve(__dirname, '../..');
const documents = JSON.parse(fs.readFileSync(path.join(__dirname, 'documents.json'), 'utf8')).documents.filter(doc => doc.pdf_filename);

async function main() {
  const server = http.createServer((request, response) => {
    if (request.url === '/fonts/NotoSans.ttf') {
      response.setHeader('Content-Type', 'font/ttf');
      response.end(fs.readFileSync(path.join(root, 'apps/mobile/assets/fonts/NotoSans.ttf')));
      return;
    }
    const doc = documents.find(item => request.url === `/notes/${item.id}`);
    if (!doc) {
      response.writeHead(404);
      response.end();
      return;
    }
    response.setHeader('Content-Type', 'text/html; charset=utf-8');
    const html = fs.readFileSync(path.join(__dirname, 'sources', `${doc.id}.html`), 'utf8');
    response.end(html.replace('../../../apps/mobile/assets/fonts/NotoSans.ttf', '/fonts/NotoSans.ttf'));
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const baseUrl = `http://127.0.0.1:${server.address().port}`;
  let browser;
  try {
    browser = await chromium.launch({
      executablePath: process.env.CHROME_EXECUTABLE || '/usr/bin/chromium',
      headless: true,
      args: ['--no-sandbox', '--disable-dev-shm-usage'],
    });
    const page = await browser.newPage();
    // Each request is local; remote resources are deliberately blocked.
    await page.route('**/*', route => {
      if (route.request().url().startsWith(baseUrl + '/')) return route.continue();
      return route.abort();
    });
    for (const doc of documents) {
      await page.goto(`${baseUrl}/notes/${doc.id}`, { waitUntil: 'load' });
      await page.evaluate(() => document.fonts.ready);
      const pdfPath = path.join(__dirname, 'files', doc.pdf_filename);
      await page.pdf({
        path: pdfPath,
        format: 'A4',
        preferCSSPageSize: true,
        printBackground: true,
      });
      fs.chmodSync(pdfPath, 0o644);
      process.stdout.write(`${doc.pdf_filename} generated\n`);
    }
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
}

main().catch(error => { process.stderr.write(String(error) + '\n'); process.exitCode = 1; });
