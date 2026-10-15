// Use a disposable API database: this imports one self-authored test question.
const { chromium } = require('playwright');

(async () => {
  const token = process.env.KHOHOC_ADMIN_TOKEN;
  if (!token) throw Error('Set local KHOHOC_ADMIN_TOKEN');
  const apiBase = process.env.KHOHOC_SMOKE_API_URL || 'http://127.0.0.1:8010';
  const adminBase = process.env.KHOHOC_SMOKE_ADMIN_URL || 'http://127.0.0.1:3002';
  async function api(path, body) {
    const response = await fetch(apiBase + path, {
      method: body ? 'POST' : 'GET',
      headers: { Authorization: 'Bearer ' + token, 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
    });
    if (!response.ok) throw Error('Test API request failed: ' + response.status);
    return response.json();
  }
  const id = 'revision_ui_' + Date.now();
  const question = {
    id, grade: 1, subject: 'toan', topic: 'phep_cong', type: 'single_choice',
    question: 'Câu tự biên soạn kiểm thử lịch sử ' + id + ': 1 + 1 bằng bao nhiêu?',
    options: [{ id: 'A', text: '2' }, { id: 'B', text: '3' }],
    correct_answer: ['A'], max_score: 1, explanation: '1 + 1 = 2.',
    source_type: 'original', license: 'original_content', rights_evidence: 'Fixture tự biên soạn cho kiểm thử giao diện.',
  };
  await api('/admin/import', { questions: [question] });
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
    await page.goto(adminBase + '/questions/' + id);
    await page.getByRole('heading', { name: 'Sửa câu hỏi và lịch sử phiên bản' }).waitFor();
    const jsonInput = page.getByLabel('Nội dung câu hỏi (JSON)');
    const save = page.getByRole('button', { name: 'Lưu thành phiên bản nháp mới' });
    if (await save.isEnabled()) throw Error('Save should require preview');
    await jsonInput.fill('{broken');
    await page.getByRole('button', { name: 'Xem trước nội dung sửa' }).click();
    await page.locator('p[role="alert"]').waitFor();
    if (await save.isEnabled()) throw Error('Invalid JSON was allowed');
    const edited = { ...question, correct_answer: ['B'], explanation: 'Đáp án sửa cho kiểm thử phiên bản.' };
    await jsonInput.fill(JSON.stringify(edited, null, 2));
    await page.getByRole('button', { name: 'Xem trước nội dung sửa' }).click();
    await page.getByLabel('Bản xem trước nội dung sửa').waitFor();
    await page.getByLabel('Lý do sửa').fill('Kiểm thử đổi đáp án, lưu và lịch sử.');
    await save.click();
    await page.getByRole('status').filter({ hasText: 'Đã lưu thành công' }).waitFor();
    let saved = await api('/admin/questions/' + id);
    if (saved.version !== 2 || saved.state !== 'draft' || saved.rights_confirmed || saved.question.correct_answer[0] !== 'B') throw Error('Revision edit did not persist correctly');
    await page.getByLabel('Lý do khôi phục phiên bản 1').fill('Khôi phục đáp án gốc để kết thúc kiểm thử.');
    await page.getByRole('button', { name: 'Khôi phục phiên bản 1 thành bản nháp mới' }).click();
    await page.getByRole('heading', { name: 'Phiên bản 3 · hiện tại' }).waitFor();
    saved = await api('/admin/questions/' + id);
    const history = await api('/admin/questions/' + id + '/versions');
    if (saved.version !== 3 || saved.question.correct_answer[0] !== 'A' || saved.state !== 'draft' || history.versions.length !== 3) throw Error('Rollback/history invalid');
    const shot = process.env.KHOHOC_SMOKE_SCREENSHOT;
    if (shot) await page.screenshot({ path: shot, fullPage: true });
    console.log('PASS: admin preview rejects malformed JSON, edit creates draft v2, rollback creates draft v3, all versions preserved');
  } finally { await browser.close(); }
})().catch(e => { console.error(e.message); process.exit(1); });
