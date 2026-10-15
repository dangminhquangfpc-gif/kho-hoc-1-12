"use server";
import { redirect } from 'next/navigation';
import { revalidatePath } from 'next/cache';
import { parse } from 'csv-parse/sync';
import { api, logout, requireAdmin } from '../lib/auth';
async function result(task:()=>Promise<unknown>, path='/') {
  let error='';
  try { await task(); revalidatePath('/'); } catch(e) { error=e instanceof Error?e.message:'Không thể xử lý'; }
  revalidatePath(path);
  redirect(path+'?message='+encodeURIComponent(error||'Đã lưu thành công')+'&error='+(error?'1':'0'));
}
export async function importData(form:FormData) {
  await result(async()=>{
    const text=String(form.get('data')||'');
    let batch;
    if (form.get('format')==='csv') {
      const rows=parse(text,{columns:true,skip_empty_lines:true,bom:true}) as Record<string,string>[];
      batch={questions:rows.map(row=>{const out:Record<string,unknown>={};for(const[k,v]of Object.entries(row)){if(v!=='')out[k]=['options','correct_answer','rubric'].includes(k)?JSON.parse(v):v;}return out;})};
    } else { batch=JSON.parse(text); }
    return api('/admin/import',{method:'POST',body:JSON.stringify(batch)});
  });
}
export async function approve(form:FormData) { await result(()=>api('/admin/questions/'+encodeURIComponent(String(form.get('id')))+ '/approve?rights_confirmed='+String(form.get('rights')==='on')+'&expected_version='+String(form.get('version')),{method:'POST'})); }
export async function publishQuestion(form:FormData) { await result(()=>api('/admin/questions/'+encodeURIComponent(String(form.get('id')))+ '/publish?expected_version='+String(form.get('version')),{method:'POST'})); }
export async function createExam(form:FormData) { await result(()=>api('/admin/exams',{method:'POST',body:JSON.stringify({id:form.get('id'),title:form.get('title'),grade:Number(form.get('grade')),subject:form.get('subject'),duration_minutes:Number(form.get('duration')),question_ids:String(form.get('questions')).split(',').map(s=>s.trim()).filter(Boolean)})})); }
export async function publishExam(form:FormData) { await result(()=>api('/admin/exams/'+encodeURIComponent(String(form.get('id')))+ '/publish',{method:'POST'})); }
export async function signOut() { await logout(); redirect('/login'); }

export async function editQuestion(form:FormData) {
  await requireAdmin();
  const id=String(form.get('id')||'');
  await result(async()=>{
    const question=JSON.parse(String(form.get('data')||''));
    return api('/admin/questions/'+encodeURIComponent(id)+'/edit',{
      method:'POST',
      body:JSON.stringify({question,expected_version:Number(form.get('version')),note:String(form.get('note')||'').trim()}),
    });
  },'/questions/'+encodeURIComponent(id));
}

export async function rollbackQuestion(form:FormData) {
  await requireAdmin();
  const id=String(form.get('id')||'');
  await result(()=>api('/admin/questions/'+encodeURIComponent(id)+'/rollback',{
    method:'POST',
    body:JSON.stringify({expected_version:Number(form.get('version')),target_version:Number(form.get('target_version')),note:String(form.get('note')||'').trim()}),
  }),'/questions/'+encodeURIComponent(id));
}

export async function importDocuments(form:FormData) {
  await requireAdmin();
  await result(()=>api('/admin/documents/import',{
    method:'POST',body:JSON.stringify(JSON.parse(String(form.get('data')||''))),
  }),'/documents');
}

export async function approveDocument(form:FormData) {
  await result(()=>api('/admin/documents/'+encodeURIComponent(String(form.get('id')))+
    '/approve?rights_confirmed='+String(form.get('rights')==='on'),{method:'POST'}),'/documents');
}

export async function publishDocument(form:FormData) {
  await result(()=>api('/admin/documents/'+encodeURIComponent(String(form.get('id')))+
    '/publish',{method:'POST'}),'/documents');
}
