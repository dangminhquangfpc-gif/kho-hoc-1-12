'use client';

import { useState } from 'react';
import { useFormStatus } from 'react-dom';
import { editQuestion } from '../../actions';

type Preview = {
  question: string;
  options?: { id: string; text: string }[];
  correct_answer?: string[];
  explanation?: string;
  max_score?: string | number;
};

function SaveButton({ reviewed }: { reviewed: boolean }) {
  const { pending } = useFormStatus();
  return <button disabled={!reviewed || pending}>{pending ? 'Đang lưu…' : 'Lưu thành phiên bản nháp mới'}</button>;
}

export default function QuestionEditor({ question, version }: { question: Record<string, unknown>; version: number }) {
  const [text, setText] = useState(JSON.stringify(question, null, 2));
  const [preview, setPreview] = useState<Preview | null>(null);
  const [error, setError] = useState('');
  function review() {
    try {
      const candidate = JSON.parse(text);
      if (!candidate || typeof candidate !== 'object' || Array.isArray(candidate) || typeof candidate.question !== 'string') {
        throw new Error('Cần một đối tượng JSON có trường question dạng văn bản.');
      }
      if (candidate.id !== question.id) throw new Error('ID câu hỏi phải giữ nguyên.');
      if (candidate.options && (!Array.isArray(candidate.options) || candidate.options.some((item: unknown) => !item || typeof item !== 'object' || typeof (item as { id?: unknown }).id !== 'string' || typeof (item as { text?: unknown }).text !== 'string'))) {
        throw new Error('Mỗi lựa chọn cần id và text dạng văn bản.');
      }
      if (candidate.correct_answer && (!Array.isArray(candidate.correct_answer) || candidate.correct_answer.some((item: unknown) => typeof item !== 'string'))) {
        throw new Error('correct_answer phải là danh sách văn bản.');
      }
      if (candidate.explanation !== undefined && typeof candidate.explanation !== 'string') throw new Error('explanation phải là văn bản.');
      setPreview(candidate);
      setError('');
    } catch (e) {
      setPreview(null);
      setError(e instanceof Error ? e.message : 'JSON không hợp lệ.');
    }
  }
  return <form action={editQuestion}>
    <input type="hidden" name="id" value={String(question.id)} />
    <input type="hidden" name="version" value={version} />
    <label>Nội dung câu hỏi (JSON)<textarea name="data" rows={20} required value={text} onChange={e => { setText(e.target.value); setPreview(null); setError(''); }} /></label>
    <button type="button" className="secondary" onClick={review}>Xem trước nội dung sửa</button>
    {error && <p role="alert" className="error">{error}</p>}
    {preview && <article className="question" aria-label="Bản xem trước nội dung sửa">
      <h3>{preview.question}</h3>
      {!!preview.options?.length && <ul>{preview.options.map(option => <li key={option.id}>{option.id}: {option.text}</li>)}</ul>}
      <p>Đáp án chuẩn: {preview.correct_answer?.join(', ') || 'Theo rubric tự luận'}</p>
      <p>Lời giải: {preview.explanation}</p>
      <details><summary>Kiểm tra toàn bộ dữ liệu và quyền sử dụng</summary><pre>{JSON.stringify(preview, null, 2)}</pre></details>
      <p>Cấu trúc câu hỏi, đáp án, điểm và rubric sẽ được backend kiểm tra lại khi lưu.</p>
    </article>}
    <label>Lý do sửa<textarea name="note" rows={2} required maxLength={1000} placeholder="Ví dụ: sửa đáp án và giải thích phép tính" /></label>
    <SaveButton reviewed={!!preview} />
  </form>;
}
