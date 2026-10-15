/* Tự học 111 browser OCR bridge. Runs only on an explicit file selection.
 * The unmodified, pinned Tesseract.js 6 worker protocol is documented alongside
 * these assets. Images never leave this browser and are not stored by this code.
 */
(() => {
  'use strict';
  const scriptUrl = document.currentScript && document.currentScript.src;
  const assetRoot = new URL('./', scriptUrl || new URL('ocr/ocr.js', document.baseURI));
  const MAX_BYTES = 8 * 1024 * 1024;
  const MAX_EDGE = 6000;
  const MAX_PIXELS = 16000000;
  const DEADLINE_MS = 60000;
  const MATH_WARNING = 'OCR phù hợp với chữ in. Chữ viết tay, phân số, số mũ và công thức toán có thể nhận sai; hãy kiểm tra và sửa trước khi dùng.';
  let active = null;
  let operationNumber = 0;

  class OcrError extends Error {}
  function fail(message) { throw new OcrError(message); }
  function supported() {
    return typeof Worker !== 'undefined' && typeof WebAssembly === 'object' &&
      typeof FileReader !== 'undefined' && typeof HTMLCanvasElement !== 'undefined';
  }
  function emit(op, stage, progress = 0) {
    if (active !== op || op.cancelled) return;
    op.stage = stage;
    op.progress = Math.max(0, Math.min(1, Number(progress) || 0));
    window.dispatchEvent(new CustomEvent('tu-hoc-ocr-progress', {
      detail: { stage: op.stage, progress: op.progress },
    }));
  }
  function begin() {
    if (!supported()) fail('Trình duyệt này chưa hỗ trợ nhận dạng ảnh. Bạn có thể nhập nội dung bằng tay.');
    if (active) fail('Một ảnh đang được nhận dạng. Hãy chờ hoặc hủy trước khi chọn ảnh khác.');
    const op = { id: ++operationNumber, stage: 'selecting', progress: 0,
      worker: null, input: null, job: null, cancelled: null, timer: null, cleanups: [] };
    op.aborted = new Promise((_, reject) => { op.abortReject = reject; });
    // This promise may be aborted before the first asynchronous file read starts.
    op.aborted.catch(() => {});
    active = op;
    return op;
  }
  function check(op) { if (op.cancelled) throw op.cancelled; }
  function race(op, promise) { check(op); return Promise.race([promise, op.aborted]); }
  function abort(op, message, timeout = false) {
    if (!op || op.cancelled) return;
    const error = new OcrError(message);
    error.name = timeout ? 'TimeoutError' : 'AbortError';
    op.cancelled = error;
    if (op.worker) { op.worker.terminate(); op.worker = null; }
    if (op.input) { op.input.remove(); op.input = null; }
    op.abortReject(error);
  }
  function cancel() { abort(active, 'Đã hủy nhận dạng ảnh.'); }
  function finish(op) {
    clearTimeout(op.timer);
    if (op.worker) op.worker.terminate();
    if (op.input) op.input.remove();
    op.worker = null;
    op.input = null;
    for (const cleanup of op.cleanups) cleanup();
    op.cleanups.length = 0;
    if (active === op) active = null;
  }
  function dimensions(bytes) {
    const data = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
    const ascii = (offset, count) => String.fromCharCode(...bytes.subarray(offset, offset + count));
    if (bytes.length >= 24 && ascii(0, 8) === '\x89PNG\r\n\x1a\n' &&
        data.getUint32(8) === 13 && ascii(12, 4) === 'IHDR') {
      return { type: 'image/png', width: data.getUint32(16), height: data.getUint32(20) };
    }
    if (bytes.length >= 12 && bytes[0] === 255 && bytes[1] === 216) {
      // Read SOF dimensions before asking a decoder to allocate image memory.
      let offset = 2;
      while (offset + 4 <= bytes.length) {
        if (bytes[offset++] !== 255) break;
        while (offset < bytes.length && bytes[offset] === 255) offset++;
        const marker = bytes[offset++];
        if (marker === 0xD9 || marker === 0xDA) break;
        if (marker === 0x01 || (marker >= 0xD0 && marker <= 0xD7)) continue;
        if (offset + 2 > bytes.length) break;
        const length = data.getUint16(offset);
        if (length < 2 || offset + length > bytes.length) break;
        if ([0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF].includes(marker)) {
          if (length < 8) break;
          return { type: 'image/jpeg', width: data.getUint16(offset + 5), height: data.getUint16(offset + 3) };
        }
        offset += length;
      }
    }
    if (bytes.length >= 30 && ascii(0, 4) === 'RIFF' && ascii(8, 4) === 'WEBP' &&
        data.getUint32(4, true) + 8 === bytes.length) {
      const type = ascii(12, 4);
      const chunkLength = data.getUint32(16, true);
      if (chunkLength + 20 > bytes.length) fail('Ảnh WebP không hợp lệ. Hãy chọn ảnh khác.');
      if (type === 'VP8X' && chunkLength === 10) {
        if (bytes[20] & 2) fail('Chưa hỗ trợ ảnh động. Hãy chọn ảnh PNG, JPEG hoặc WebP tĩnh.');
        const u24 = p => bytes[p] + (bytes[p + 1] << 8) + (bytes[p + 2] << 16);
        return { type: 'image/webp', width: u24(24) + 1, height: u24(27) + 1 };
      }
      if (type === 'VP8 ' && chunkLength >= 10 && bytes[23] === 0x9D && bytes[24] === 0x01 && bytes[25] === 0x2A) {
        return { type: 'image/webp', width: data.getUint16(26, true) & 0x3FFF, height: data.getUint16(28, true) & 0x3FFF };
      }
      if (type === 'VP8L' && chunkLength >= 5 && bytes[20] === 0x2F) {
        const bits = data.getUint32(21, true);
        return { type: 'image/webp', width: (bits & 0x3FFF) + 1, height: ((bits >>> 14) & 0x3FFF) + 1 };
      }
    }
    fail('Tệp không phải ảnh PNG, JPEG hoặc WebP hợp lệ. Chưa hỗ trợ PDF, SVG và GIF.');
  }
  function checkDimensions(width, height) {
    if (!width || !height || width > MAX_EDGE || height > MAX_EDGE || width * height > MAX_PIXELS) {
      fail('Ảnh quá lớn hoặc không hợp lệ. Chọn ảnh tối đa 16 triệu điểm ảnh, mỗi chiều không quá 6.000 điểm ảnh.');
    }
  }
  async function decode(op, blob) {
    if (typeof createImageBitmap === 'function') {
      const pending = createImageBitmap(blob, { imageOrientation: 'from-image' });
      // A decode finishing after cancellation must release its bitmap as well.
      pending.then(bitmap => { if (op.cancelled) bitmap.close(); }, () => {});
      const bitmap = await race(op, pending);
      op.cleanups.push(() => bitmap.close());
      return bitmap;
    }
    const image = new Image();
    const url = URL.createObjectURL(blob);
    op.cleanups.push(() => { image.onload = null; image.onerror = null; image.src = ''; URL.revokeObjectURL(url); });
    await race(op, new Promise((resolve, reject) => {
      image.onload = resolve;
      image.onerror = () => reject(new OcrError('Không đọc được ảnh. Hãy chụp hoặc lưu lại ảnh rồi thử lại.'));
      image.src = url;
    }));
    return image;
  }
  function canvasFor(op, image, width, height) {
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    op.cleanups.push(() => { canvas.width = 0; canvas.height = 0; });
    const ctx = canvas.getContext('2d', { alpha: false });
    if (!ctx) fail('Không thể xử lý ảnh trên trình duyệt này. Bạn có thể nhập nội dung bằng tay.');
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, width, height);
    ctx.drawImage(image, 0, 0, width, height);
    return canvas;
  }
  function request(op, action, payload) {
    check(op);
    const jobId = `${op.id}-${action}`;
    return race(op, new Promise((resolve, reject) => {
      op.job = { jobId, action, resolve, reject };
      op.worker.postMessage({ workerId: `tuhoc-${op.id}`, jobId, action, payload });
    }));
  }
  async function recognize(op, file) {
    clearTimeout(op.timer);
    op.timer = setTimeout(() => abort(op, 'Nhận dạng mất quá 60 giây. Hãy cắt ảnh rõ hơn hoặc nhập nội dung bằng tay.', true), DEADLINE_MS);
    emit(op, 'validating');
    if (!(file instanceof Blob) || !file.size || file.size > MAX_BYTES) fail('Chọn ảnh PNG, JPEG hoặc WebP có dung lượng từ 1 byte đến 8 MB.');
    if (file.type && !['image/png', 'image/jpeg', 'image/webp'].includes(file.type.toLowerCase())) {
      fail('Chỉ hỗ trợ ảnh PNG, JPEG và WebP. Chưa hỗ trợ PDF, SVG và GIF.');
    }
    const bytes = new Uint8Array(await race(op, file.arrayBuffer()));
    const header = dimensions(bytes);
    if (file.type && file.type.toLowerCase() !== header.type) fail('Định dạng thực tế của ảnh không khớp. Hãy lưu lại ảnh thành PNG hoặc JPEG.');
    checkDimensions(header.width, header.height);
    const image = await decode(op, new Blob([bytes], { type: header.type }));
    const width = image.width || image.naturalWidth;
    const height = image.height || image.naturalHeight;
    checkDimensions(width, height);
    if (!((width === header.width && height === header.height) || (width === header.height && height === header.width))) {
      fail('Kích thước ảnh không khớp. Hãy lưu lại ảnh rồi thử lại.');
    }
    check(op);
    const scale = Math.min(1, 3200 / Math.max(width, height), Math.sqrt(8000000 / (width * height)));
    const canvas = canvasFor(op, image, Math.max(1, Math.round(width * scale)), Math.max(1, Math.round(height * scale)));
    const previewScale = Math.min(1, 900 / Math.max(width, height));
    const preview = canvasFor(op, image, Math.max(1, Math.round(width * previewScale)), Math.max(1, Math.round(height * previewScale)));
    const previewData = preview.toDataURL('image/jpeg', 0.72);
    // Re-encoding drops filenames, EXIF, GPS and other image metadata.
    const encoded = await race(op, new Promise(resolve => canvas.toBlob(resolve, 'image/png')));
    if (!encoded) fail('Không thể xử lý ảnh. Hãy thử ảnh khác.');
    const normalizedBytes = new Uint8Array(await race(op, encoded.arrayBuffer()));
    emit(op, 'initializing');
    op.worker = new Worker(new URL('vendor/worker.min.js', assetRoot));
    op.worker.onerror = () => { if (op.job) op.job.reject(new OcrError('Không khởi động được bộ nhận dạng. Hãy tải lại trang và thử lại.')); };
    op.worker.onmessageerror = op.worker.onerror;
    op.worker.onmessage = event => {
      const message = event.data;
      if (!op.job || !message || message.jobId !== op.job.jobId || message.action !== op.job.action) return;
      if (message.status === 'resolve') { const job = op.job; op.job = null; job.resolve(message.data); }
      else if (message.status === 'reject') {
        const job = op.job;
        op.job = null;
        job.reject(new OcrError('Chưa nhận dạng được ảnh này. Hãy dùng ảnh rõ hơn hoặc nhập nội dung bằng tay.'));
      } else if (message.status === 'progress' && op.job.action === 'recognize') {
        emit(op, 'recognizing', message.data && message.data.progress);
      }
    };
    await request(op, 'load', { options: { lstmOnly: true, corePath: new URL('vendor/', assetRoot).href, logging: false } });
    await request(op, 'loadLanguage', { langs: ['vie', 'eng'], options: {
      langPath: new URL('lang/', assetRoot).href, cacheMethod: 'none', gzip: true, lstmOnly: true,
    } });
    await request(op, 'initialize', { langs: ['vie', 'eng'], oem: 1, config: {} });
    emit(op, 'recognizing');
    const result = await request(op, 'recognize', { image: normalizedBytes, options: {}, output: { text: true } });
    check(op);
    const text = typeof result.text === 'string' ? result.text.normalize('NFC').trim().slice(0, 20000) : '';
    const confidence = Math.max(0, Math.min(100, Number(result.confidence) || 0));
    const warnings = [MATH_WARNING];
    if (!text) warnings.unshift('Chưa tìm thấy chữ rõ trong ảnh. Hãy chụp gần hơn, đủ sáng và đặt trang giấy thẳng.');
    else if (confidence < 70) warnings.unshift('Độ tin cậy thấp. Hãy đối chiếu từng dòng và sửa các chữ, số nhận sai.');
    if (scale < 1) warnings.push('Ảnh lớn đã được thu nhỏ để xử lý; hãy cắt riêng từng bài nếu chữ nhỏ khó đọc.');
    if (typeof result.text === 'string' && result.text.length > 20000) warnings.push('Văn bản dài được giới hạn 20.000 ký tự. Hãy nhận dạng từng trang nhỏ.');
    return { text, confidence, warnings, preview_data_url: previewData };
  }
  function friendly(error) {
    if (error instanceof OcrError) return error;
    return new OcrError('Không đọc được ảnh. Hãy dùng ảnh PNG, JPEG hoặc WebP rõ hơn, hoặc nhập nội dung bằng tay.');
  }
  async function recognizeFile(file) {
    const op = begin();
    try { return await recognize(op, file); }
    catch (error) { throw friendly(error); }
    finally { finish(op); }
  }
  async function pickAndRecognize() {
    const op = begin();
    try {
      const picked = new Promise(resolve => {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/png,image/jpeg,image/webp';
        input.setAttribute('aria-label', 'Chọn ảnh để nhận dạng');
        input.style.cssText = 'position:fixed;left:-10000px;top:0;width:1px;height:1px;opacity:0';
        op.input = input;
        const chosen = () => resolve(input.files && input.files.length ? input.files[0] : null);
        input.addEventListener('change', chosen, { once: true });
        input.addEventListener('cancel', () => resolve(null), { once: true });
        const focused = () => {
          const timer = setTimeout(() => { if (op.input === input) chosen(); }, 500);
          op.cleanups.push(() => clearTimeout(timer));
        };
        window.addEventListener('focus', focused, { once: true });
        op.cleanups.push(() => window.removeEventListener('focus', focused));
        document.body.appendChild(input);
        // Keep this call synchronous with the user's button press (Safari).
        input.click();
      });
      op.timer = setTimeout(() => abort(op, 'Đã hết thời gian chọn ảnh. Bạn có thể chọn lại ảnh.', true), 120000);
      const file = await race(op, picked);
      if (op.input) { op.input.remove(); op.input = null; }
      if (!file) return null;
      return await recognize(op, file);
    } catch (error) { throw friendly(error); }
    finally { finish(op); }
  }
  window.tuHocOcr = Object.freeze({
    version: '1.0.0-tesseract6', supported, pickAndRecognize, recognizeFile, cancel,
    status: () => active ? { busy: true, stage: active.stage, progress: active.progress } : { busy: false, stage: 'idle', progress: 0 },
  });
})();
