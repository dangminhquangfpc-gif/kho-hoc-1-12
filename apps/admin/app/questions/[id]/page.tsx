import Link from 'next/link';
import { notFound } from 'next/navigation';
import { api, requireAdmin } from '../../../lib/auth';
import { rollbackQuestion } from '../../actions';
import QuestionEditor from './QuestionEditor';

type Detail = { question: Record<string, unknown>; version: number; state: string; rights_confirmed: boolean; exam_ids: string[] };
type Revision = { version: number; question: Record<string, unknown>; operation: string; note: string; actor: string; created_at: string | null; restored_from: number | null };
type History = { current_version: number; versions: Revision[] };

export default async function QuestionPage({ params, searchParams }: { params: Promise<{ id: string }>; searchParams: Promise<{ message?: string; error?: string }> }) {
  await requireAdmin();
  const { id } = await params;
  if (!/^[a-zA-Z0-9_-]{1,80}$/.test(id)) notFound();
  const messages = await searchParams;
  let detail: Detail | null = null;
  let history: History | null = null;
  let failure = '';
  try {
    [detail, history] = await Promise.all([
      api('/admin/questions/' + encodeURIComponent(id)),
      api('/admin/questions/' + encodeURIComponent(id) + '/versions'),
    ]);
  } catch (e) { failure = e instanceof Error ? e.message : 'Backend không khả dụng'; }
  return <main>
    <p><Link href="/">← Quay lại hàng chờ kiểm duyệt</Link></p>
    <h1>Sửa câu hỏi và lịch sử phiên bản</h1>
    {messages.message && <p role="status" className={messages.error === '1' ? 'error' : 'success'}>{messages.message}</p>}
    {failure && <p role="alert" className="error">{failure}</p>}
    {detail && history && <>
      <section>
        <p className="tag">{id} · phiên bản {detail.version} · {detail.state}</p>
        <p>Mỗi lần sửa hoặc khôi phục tạo phiên bản mới ở trạng thái nháp. Bạn cần duyệt lại nội dung và quyền phân phối, rồi xuất bản lại câu hỏi và các đề liên quan.</p>
        <p>Bài làm đã bắt đầu giữ nguyên câu hỏi và đáp án tại thời điểm bắt đầu.</p>
        {!!detail.exam_ids.length && <p>Đề liên quan: {detail.exam_ids.join(', ')}. Các đề này sẽ trở về nháp khi lưu thay đổi.</p>}
        <QuestionEditor key={detail.version} question={detail.question} version={detail.version} />
      </section>
      <section><h2>Lịch sử thay đổi</h2>
        {history.versions.map(revision => <article className="question" key={revision.version}>
          <h3>Phiên bản {revision.version}{revision.version === detail.version ? ' · hiện tại' : ''}</h3>
          <p>{revision.note}</p>
          <p>{revision.operation === 'rollback' ? `Khôi phục từ phiên bản ${revision.restored_from}` : revision.operation === 'edit' ? 'Chỉnh sửa' : 'Nội dung ban đầu'} · {revision.actor}{revision.created_at ? ' · ' + revision.created_at : ''}</p>
          <details><summary>Xem câu hỏi, đáp án và rubric của phiên bản này</summary><pre>{JSON.stringify(revision.question, null, 2)}</pre></details>
          {revision.version !== detail.version && <form action={rollbackQuestion}>
            <input type="hidden" name="id" value={id} />
            <input type="hidden" name="version" value={detail.version} />
            <input type="hidden" name="target_version" value={revision.version} />
            <label>Lý do khôi phục phiên bản {revision.version}<textarea name="note" rows={2} maxLength={1000} required /></label>
            <button className="secondary">Khôi phục phiên bản {revision.version} thành bản nháp mới</button>
          </form>}
        </article>)}
      </section>
    </>}
  </main>;
}
