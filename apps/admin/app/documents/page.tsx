import Link from 'next/link';
import { api, requireAdmin } from '../../lib/auth';
import { approveDocument, importDocuments, publishDocument } from '../actions';

type Document = {
  id: string; title: string; grade: number; subject: string; summary: string;
  author: string; source_name: string; source_url: string | null;
  source_type: 'original' | 'licensed' | 'link_only'; license: string; rights_evidence: string;
  distribution_allowed: boolean; download_allowed: boolean; pdf_filename: string | null;
  sections: { heading: string; text: string }[];
};
type DocumentRecord = { document: Document; state: string; rights_confirmed: boolean; version: number };

export default async function Documents({ searchParams }: { searchParams: Promise<{ message?: string; error?: string }> }) {
  await requireAdmin();
  const params = await searchParams;
  let rows: DocumentRecord[] = [];
  let failure = '';
  try { rows = await api('/admin/documents'); } catch (e) { failure = e instanceof Error ? e.message : 'Backend không khả dụng'; }
  return <main>
    <p><Link href="/">← Quay lại quản trị câu hỏi</Link></p>
    <h1>Quản lý tài liệu học tập</h1>
    <p>Nhập tài liệu nháp, kiểm tra nội dung và nguồn, xác nhận quyền sử dụng rồi xuất bản vào thư viện.</p>
    {params.message && <p role="status" className={params.error === '1' ? 'error' : 'success'}>{params.message}</p>}
    {failure && <p role="alert" className="error">Backend chưa sẵn sàng: {failure}</p>}
    <section className="stats"><article><strong>{rows.length}</strong><span>Tài liệu</span></article><article><strong>{rows.filter(row => row.state === 'draft').length}</strong><span>Chờ duyệt</span></article><article><strong>{rows.filter(row => row.state === 'published').length}</strong><span>Đã xuất bản</span></article></section>
    <section>
      <h2>Nhập tài liệu JSON</h2>
      <p>Dữ liệu nhập luôn ở trạng thái nháp. Nội dung dạng liên kết chỉ dẫn đến nguồn; tài liệu có nội dung hoặc PDF cần quyền chia sẻ tương ứng. PDF cần có trong kho tài liệu trước khi nhập; chức năng tải file lên đang được hoàn thiện.</p>
      <form action={importDocuments}>
        <label>Dữ liệu tài liệu (JSON)<textarea name="data" rows={10} required placeholder={'{ "documents": [...] }'} /></label>
        <button>Kiểm tra và nhập tài liệu nháp</button>
      </form>
    </section>
    <section>
      <h2>Hàng chờ tài liệu và bản xem trước</h2>
      {!rows.length && <p>Chưa có tài liệu. Nhập dữ liệu đã kiểm tra để bắt đầu.</p>}
      {rows.map(({ document, state, rights_confirmed, version }) => <article key={document.id} className="question">
        <p className="tag">Lớp {document.grade} · {document.subject} · {state} · phiên bản {version}</p>
        <h3>{document.title}</h3>
        <p>{document.summary}</p>
        <p>Tác giả: {document.author} · Nguồn: {document.source_name}</p>
        {document.source_url && <p><a href={document.source_url} target="_blank" rel="noopener noreferrer">Mở nguồn để kiểm tra</a></p>}
        <p>Giấy phép: {document.license}. {document.source_type === 'link_only' ? 'Tài liệu dạng liên kết đến nguồn.' : 'Chia sẻ nội dung: ' + (document.distribution_allowed ? 'cho phép' : 'không cho phép') + '. Tải PDF: ' + (document.download_allowed ? 'cho phép' : 'không cho phép') + '.'}</p>
        <p>Bằng chứng quyền: {document.rights_evidence}</p>
        <p>Quyền sử dụng: {rights_confirmed ? 'đã xác nhận' : 'chưa xác nhận'}{document.pdf_filename ? ' · Có PDF: ' + document.pdf_filename : ''}</p>
        <details><summary>Xem nội dung và toàn bộ dữ liệu trước khi duyệt</summary>
          {document.sections.map((section, index) => <div key={index}><h4>{section.heading}</h4><p style={{ whiteSpace: 'pre-wrap' }}>{section.text}</p></div>)}
          <pre>{JSON.stringify(document, null, 2)}</pre>
        </details>
        {state === 'draft' && <form action={approveDocument}>
          <input type="hidden" name="id" value={document.id} />
          <label className="check"><input type="checkbox" name="rights" required />Tôi đã kiểm tra nội dung, nguồn và quyền chia sẻ tài liệu này.</label>
          <button>Duyệt tài liệu</button>
        </form>}
        {state === 'approved' && <form action={publishDocument}>
          <input type="hidden" name="id" value={document.id} />
          <button>Xuất bản tài liệu đã duyệt</button>
        </form>}
      </article>)}
    </section>
  </main>;
}
