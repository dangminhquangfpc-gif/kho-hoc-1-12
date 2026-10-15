// Use a disposable API database: this imports one self-authored text document.
const { chromium } = require('playwright');

(async () => {
  const token = process.env.KHOHOC_ADMIN_TOKEN;
  if (!token) throw Error('Set local KHOHOC_ADMIN_TOKEN');
  const apiBase = process.env.KHOHOC_SMOKE_API_URL || 'http://127.0.0.1:8010';
  const adminBase = process.env.KHOHOC_SMOKE_ADMIN_URL || 'http://127.0.0.1:3002';
  const id = 'document_ui_' + Date.now();
  const document = {
    id, title: 'Tài liệu tự biên soạn kiểm thử ' + id,
    grade: 1, subject: 'toan', topic: 'Phép cộng', semester: 1,
    textbook: 'independent', kind: 'study_notes',
    summary: 'Nội dung riêng dùng để kiểm thử nhập và duyệt tài liệu qua giao diện.',
    author: 'Kiểm thử Kho Học', source_name: 'Fixture tự biên soạn',
    source_url: null, source_type: 'original', license: 'original_content',
    rights_evidence: 'Tự biên soạn cho kiểm thử luồng quản trị tài liệu.',
    distribution_allowed: true, download_allowed: false, pdf_filename: null,
    sections: [{ heading: 'Phép cộng mẫu', text: 'Một vật thêm một vật được hai vật: 1 + 1 = 2.' }],
  };
  const browser = await chromium.launch({
    executablePath: process.env.CHROME_EXECUTABLE || '/usr/bin/chromium',
    headless: true, args: ['--no-sandbox'],
  });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 1000 } });
    page.setDefaultTimeout(90000);
    await page.goto(adminBase + '/login');
    await page.getByLabel('Token quản trị').fill(token);
    await page.getByRole('button', { name: 'Đăng nhập' }).click();
    await page.getByRole('heading', { name: 'Kiểm duyệt nội dung' }).waitFor();
    await page.getByRole('link', { name: 'Quản lý thư viện tài liệu, nguồn và giấy phép' }).click();
    await page.getByRole('heading', { name: 'Quản lý tài liệu học tập' }).waitFor();
    await page.getByLabel('Dữ liệu tài liệu (JSON)').fill(JSON.stringify({ documents: [document] }, null, 2));
    await page.getByRole('button', { name: 'Kiểm tra và nhập tài liệu nháp' }).click();
    const card = page.locator('article').filter({ has: page.getByRole('heading', { name: document.title }) });
    await card.getByRole('heading', { name: document.title }).waitFor();
    let publicResponse = await page.request.get(apiBase + '/documents/' + id);
    if (publicResponse.status() !== 404) throw Error('Draft document exposed publicly');
    await card.getByText('Xem nội dung và toàn bộ dữ liệu trước khi duyệt').click();
    await card.getByRole('heading', { name: 'Phép cộng mẫu' }).waitFor();
    await card.getByLabel('Tôi đã kiểm tra nội dung, nguồn và quyền chia sẻ tài liệu này.').check();
    await card.getByRole('button', { name: 'Duyệt tài liệu' }).click();
    await card.getByRole('button', { name: 'Xuất bản tài liệu đã duyệt' }).waitFor();
    await card.getByRole('button', { name: 'Xuất bản tài liệu đã duyệt' }).click();
    await card.getByText('Lớp 1 · toan · published · phiên bản 1').waitFor();
    publicResponse = await page.request.get(apiBase + '/documents/' + id);
    if (publicResponse.status() !== 200 || (await publicResponse.json()).sections[0].text !== document.sections[0].text) throw Error('Published document missing');
    if ((await page.request.get(apiBase + '/admin/documents')).status() !== 403) throw Error('Admin authorization bypass');
    if (process.env.KHOHOC_SMOKE_SCREENSHOT) await page.screenshot({ path: process.env.KHOHOC_SMOKE_SCREENSHOT, fullPage: true });
    console.log('PASS: document JSON import stays private, source/content preview, explicit rights approval, publication, protected admin route');
  } finally { await browser.close(); }
})().catch(e => { console.error(e.message); process.exit(1); });
